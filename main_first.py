import urllib
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pymysql

class main_first():
    def __init__(self, url):
        self.url = url
        self.total_data = []

    def download_page(self):
        """Download function that catches errors"""
        print('Downloading:', self.url)
        try:
            self.html = urlopen(self.url).read()
        except urllib.error.URLError as e:
            print('Download error:', e.reason)
            self.html = None
        print(self.html)

    def parse_page(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        tbody = soup.tbody
        rows = tbody.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            num = calibrate_str(cols[0].string)
            species = calibrate_str(cols[1].i.string)
            year = calibrate_str(cols[2].string)
            period = calibrate_str(cols[3].string)
            from_to = calibrate_str(cols[4].a.string)
            reason = calibrate_str(cols[5].string)
            established = calibrate_str(cols[6].string)
            ref = calibrate_str(cols[7].a.string)

            self.total_data.append({
                'num': num,
                'species': species,
                'year': year,
                'period': period,
                'from_to': from_to,
                'reason': reason,
                'established': established,
                'ref': ref,
            })
        print(self.total_data)


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

        sql = "DROP TABLE IF EXISTS Total_first"
        self.cur.execute(sql)
        sql = "CREATE TABLE Total_first(ID INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL, Species VARCHAR(255)," + \
            "Year VARCHAR(255), Period VARCHAR(255), From_To VARCHAR(255), Reason VARCHAR(255), Established VARCHAR(255), " + \
            "Ref VARCHAR(255))"
        self.cur.execute(sql)

        for row in self.total_data:
            self.cur = self.db.cursor()
            sql = "INSERT INTO Total_first(Species, Year, Period, From_To, Reason, Established, Ref) " + \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s);"
            self.cur.execute(sql, (row['species'], row['year'], row['period'], row['from_to'], row['reason'], row['established'], row['ref']))
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
    app = main_first('http://www.fishbase.se/Introductions/InvasiveIntroduced_list.php?fromvar=&tovar=')
    app.download_page()
    app.parse_page()
    app.save_db()