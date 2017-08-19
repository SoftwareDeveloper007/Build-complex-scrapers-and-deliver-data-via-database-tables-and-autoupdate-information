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


class main_second():
    def __init__(self, url):
        self.url = url
        self.total_urls = []
        self.total_data = []

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

            url = "http://www.fishbase.se/trophiceco/EcosysRef.php?ve_code=" + value + '&sp='

            self.total_urls.append({
                "value": value,
                "location": location,
                "url": url
            })

        driver.close()

    def download_pages(self):

        print('Downloading html pages and parsing them...')

        for element in self.total_urls:
            #print(element["url"])
            url = element["url"]
            try:
                html = urlopen(url).read()
            except urllib.error.URLError as e:
                print('Download error:', e.reason)
                html = None

            print(url, ': downloading and parsing...')
            #print(html)
            soup = BeautifulSoup(html, 'html.parser')
            trs = soup.find_all('tr')
            #print(len(trs))

            ecosystem = calibrate_str(trs[0].find_all('td')[1].text)
            type = calibrate_str(trs[1].find_all('td')[1].text)
            salinity = calibrate_str(trs[2].find_all('td')[1].text)
            location = calibrate_str(trs[5].find_all('td')[0].text)
            lat_lng = calibrate_str(trs[5].find_all('td')[1].text)

            self.total_data.append({
                'ecosystem': ecosystem,
                'type': type,
                'salinity': salinity,
                'location': location,
                'lat_lng': lat_lng,
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

        sql = "DROP TABLE IF EXISTS Total_second"
        self.cur.execute(sql)
        sql = "CREATE TABLE Total_second(ID INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL, Ecosystem VARCHAR(255)," + \
              "Type VARCHAR(255), Salinity VARCHAR(255), Location VARCHAR(255), Latitude_Longitude VARCHAR(255))"
        self.cur.execute(sql)

        for row in self.total_data:
            self.cur = self.db.cursor()
            sql = "INSERT INTO Total_second(Ecosystem, Type, Salinity, Location, Latitude_Longitude) " + \
                  "VALUES (%s, %s, %s, %s, %s);"
            self.cur.execute(sql, (
            row['ecosystem'], row['type'], row['salinity'], row['location'], row['lat_lng']))
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

    return str.strip()

if __name__ == '__main__':
    app = main_second('http://www.fishbase.se/search.php')
    app.search_page_download()
    app.download_pages()
    app.save_db()

