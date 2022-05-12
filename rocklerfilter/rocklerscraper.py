from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

class RocklerScraper():
    rockler_stores = {
        '36' : 'Altamonte Springs,  FL',
        '27' : 'Arlington, TX',
        '17' : 'Beaverton, OR',
        '39' : 'Bolingbrook, IL',
        '46' : 'Brandon, FL',
        '07' : 'Brookfield, WI',
        '11' : 'Buffalo, NY',
        '12' : 'Burnsville, MN',
        '04' : 'Cambridge, MA',
        '16' : 'Cincinatti, OH',
        '25' : 'Concord, CA',
        '03' : 'Denver, CO',
        '49' : 'Fairfax, VA',     
        '38' : 'Frisco, TX',
        '40' : 'Garland, TX',
        '30' : 'Houston, TX',
        '21' : 'Indianapolis, IN',
        '41' : 'Kennesaw, GA',
        '13' : 'Maplewood, MN',
        '14' : 'Minnetonka, MN',
        '47' : 'Moorestown, NJ',
        '08' : 'Novi, MI',
        '44' : 'Olathe, KS',
        '26' : 'Ontario, CA',
        '20' : 'Orange, CA',
        '42' : 'Orland Park, IL',
        '22' : 'Pasadena, CA',
        '01' : 'Phoenix, AZ',
        '31' : 'Pittsburg, PA',
        '37' : 'Rocklin, CA',
        '45' : 'Round Rock, TX',
        '33' : 'S. Portland ME',
        '29' : 'Sandy Springs, GA',
        '06' : 'San Diego, CA',
        '10' : 'Schaumburg, IL',
        '02' : 'Seattle, WA',
        '34' : 'Salem, NH',
        '43' : 'Spring, TX',
        '19' : 'St Louis, MO',
        '15' : 'Tukwila, WA',
        '23' : 'Torrance, CA',
    }


    def __init__(self, storeID:str='04'):
        self.storeID = storeID
        self.woodfata = []
        self.service = Service(executable_path=GeckoDriverManager().install())

    def get_page(self, storeID:str):
        driver = webdriver.Firefox(service=self.service)
        driver.get('https://go.rockler.com/retail_lumber.cfm?store='+storeID)
        button = driver.find_element_by_xpath('/html/body/form/input')
        button.click()
        webpage = driver.page_source
        driver.close()
        return webpage   

   #goes to the webpage for the inventory and returns a dict of info
    def get_table(self, webpage):
        soup = BeautifulSoup(webpage, 'html.parser')
        rows = soup.find_all('tr')[1::]
        self.lumber_list = []
        for row in rows:
            i = 0 #good old manual iteration to condense souping
            new_entry = {}
            for cell in row.find_all('td'):
                if i == 0: new_entry['SPECIES'] = cell.text
                if i == 1: new_entry['SKU'] = cell.text.strip()
                if i == 2: new_entry['DESCRIPTION'] = cell.text.strip()
                if i == 3: new_entry['INVENTORY'] = int(cell.text.strip())
                if i == 4: new_entry['PRICE'], new_entry['TYPE'] = self.price_format(cell.text)
                i += 1
            self.lumber_list.append(new_entry.copy())
        return self.lumber_list

    def price_format(self, price_string):
        if price_string == 'Contact Store':
            return 0, price_string
        words = price_string.split()
        price = words[0][1::]
        price = price.replace(',','')
        type_string = 'BOARDFEET' if words[-1].lower() == 'foot' else 'BOARD'
        return float(price), type_string



    def filter_table(self, search_text:str=None, min_inv:float=1.0, max_price:float=100.0, 
                     board_search:bool=True, boardfeet_search:bool=True) -> list:
                    
        wood_types = [x.lower().strip() for x in search_text.split(',')]
        filtered_list = []
        for entry in self.lumber_list:
            if entry['SPECIES'].lower().strip() not in wood_types:
                if not wood_types:
                    pass
                else:
                    continue
            if entry['INVENTORY'] < min_inv:
                continue
            if entry['PRICE'] > max_price:
                    continue
            if entry['TYPE'] == 'BOARD' and not board_search:
                continue
            if entry['TYPE'] == 'BOARDFEET' and not boardfeet_search:
               continue
            filtered_list.append(entry.copy())
        return filtered_list
