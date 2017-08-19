import urllib
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class main_first():
    def __init__(self, url):
        self.url = url
        self.total_data = []
        self.total_urls = []

    def search_page_download(self):
        """Download function that catches errors"""
        print('Downloading:', self.url)
        driver = webdriver.Chrome()
        driver.get(self.url)

        ve_code_opts = driver.find_element_by_name("ve_code").find_elements_by_tag_name("option")
        ve_code_opts = ve_code_opts[1:]
        for option in ve_code_opts:
            value = option.get_attribute("value")
            location = option.text

            url = "http://www.fishbase.se/Country/CountryChecklist.php?showAll=yes&c_code=" + value + '&vhabitat=dangerous'
            self.total_urls.append({
                "value": value,
                "location": location,
                "url": url
            })

        driver.close()

    def download_pages(self):

        print('Downloading html pages and parsing them...')

        for element in self.total_urls:
            # print(element["url"])
            url = element["url"]
            try:
                html = urlopen(url).read()
            except urllib.error.URLError as e:
                print('Download error:', e.reason)
                html = None
            print(url, ': downloading and parsing...')

            soup = BeautifulSoup(html, 'html.parser')
            rows = soup.find_all('tr')

            rows = rows[6:]
            for row in rows:
                cols = row.find_all('td')
                order = calibrate_str(cols[0].string)
                family = calibrate_str(cols[1].string)
                species = calibrate_str(cols[2].a.string)
                occurence = calibrate_str(cols[3].string)
                fishbase = calibrate_str(cols[4].string)
                name = calibrate_str(cols[5].string)
                danger = calibrate_str(cols[6].string)

                self.total_data.append({
                    'location': element['location'],
                    'value': element['value'],
                    'order': order,
                    'family': family,
                    'species': species,
                    'occurence': occurence,
                    'fishbase': fishbase,
                    'name': name,
                    'danger': danger,
                })


    def save_db(self):
        # Connect db and Extract data from database
        print('Saving data into mySQL...')
        DB_HOST = 'localhost'
        DB_USER = 'root'
        DB_PASSWORD = 'passion1989'
        DB_NAME = 'Test'

        self.db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

        # prepare a cursor object using cursor() method
        self.cur = self.db.cursor()

        sql = "DROP TABLE IF EXISTS Total_third"
        self.cur.execute(sql)
        sql = "CREATE TABLE Total_third(ID INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL, Location VARCHAR(255), Order_ VARCHAR(255)," + \
            "Family VARCHAR(255), Species VARCHAR(255), Occurence VARCHAR(255), Fishbase_name VARCHAR(255), Name_ VARCHAR(255), " + \
            "Danger VARCHAR(255))"
        self.cur.execute(sql)

        for row in self.total_data:
            #print(row['location'], row['value'])
            #print(row['location'], row['order'], row['family'], row['species'], row['occurence'], row['fishbase'], row['name'], row['danger'])
            self.cur = self.db.cursor()
            sql = "INSERT INTO Total_third(Location, Order_, Family, Species, Occurence, Fishbase_name, Name_, Danger) " + \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            self.cur.execute(sql, (row['location'], row['order'], row['family'], row['species'], row['occurence'], row['fishbase'], row['name'], row['danger']))
            self.db.commit()


        self.db.close()

        print('All data is saved sucessfully!')

def calibrate_str(str):
    if (str == '') or (str is None):
        str = '-'
    else:
        while "\t" in str:
            str = str.replace("\t", "")
        while "\r" in str:
            str = str.replace("\r", "")
        while "\n" in str:
            str = str.replace("\n", "")
        while "\xa0" in str:
            str = str.replace("\xa0", "")

    if (str == '') or (str is None):
        str = '-'

    str = str.strip()
    str = str.encode('utf-8')

    return str


if __name__ == '__main__':
    app = main_first('http://www.fishbase.se/search.php')
    app.search_page_download()
    app.download_pages()
    app.save_db()