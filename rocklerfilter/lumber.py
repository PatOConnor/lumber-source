from bs4 import BeautifulSoup
from urllib.request import urlopen
import rich
import re
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from fractions import Fraction


class Lumber:
    def __init__(self):
        #testing on cambridge ma store
        store_number = '04'
        #use selenium to click on the link to get updated info
        webpage = self.get_page(store_number)
        #use bs4 to crunch the table of data
        self.lumber_list = self.get_table(webpage)


    #goes to the wood shop website and gets the url for the latest inventory
    def get_page(self, store_number):
        service = Service(executable_path=GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)
        driver.get('https://go.rockler.com/retail_lumber.cfm?store='+store_number)
        button = driver.find_element_by_xpath('/html/body/form/input')
        button.click()
        webpage = driver.page_source
        driver.close()
        return webpage

    #goes to the webpage for the inventory and returns a dict of info
    def get_table(self, webpage):
        soup = BeautifulSoup(webpage, 'html.parser')
        rows = soup.find_all('tr')[1::]
        lumber_list = []
        for row in rows:
            i = 0 #good old manual iteration to condense souping
            new_entry = {}
            for cell in row.find_all('td'):
                if i == 0: new_entry['SPECIES'] = cell.string
                if i == 1: new_entry['SKU'] = cell.string.strip()
                if i == 2: new_entry['DESCRIPTION'], new_entry['DIMENSIONS'] = self.description_format(cell.string)
                if i == 3: new_entry['INVENTORY'] = int(cell.string.strip())
                if i == 4: new_entry['PRICE'], new_entry['TYPE'] = self.price_format(cell.string)

                i += 1
            lumber_list.append(new_entry.copy())
        return lumber_list

    def description_format(self, desc_string):
        #case: 'cherry'
        only_desc = r'[A-Za-z ]+'
        #case: 'cherry 2x12x48"'
        desc_meas = r'([A-Za-z ]+)(([0-9]+(\/[0-9]+)?"?)( ?(X|x) ?)?)+'
        #measurements_then_description = r''

        if re.fullmatch(only_desc, desc_string):
            return desc_string, [0,0,0]

        elif re.fullmatch(desc_meas, desc_string):
            #gets string into 3 parts
            desc_fields = re.split(r'[Xx]', desc_string)
            if len(desc_fields) <= 2:
                return desc_string, [0,0,0,]
            length = desc_fields.pop(-1)
            width = desc_fields.pop(-1)
            desc_fields = desc_fields[0].split()
            depth = desc_fields.pop(-1)
            desc = ' '.join(desc_fields)

            return desc, [depth, width, length] #format from website

        else: #todo: other patterns?
            return desc_string, [0,0,0]

    def price_format(self, price_string):
        if price_string == 'Contact Store':
            return price_string, price_string
        words = price_string.split()
        price = words[0][1::]
        if words[-1].lower() == 'foot':
            type_string = 'BOARD FEET'
        else:
            type_string = 'BOARD'
        return float(price), type_string

    #matches up types of wood based on input from wood types
    def find_lumber(self, wood_types, dimensions=None, sqfootage=None, boardlength=None):
        in_stock_lumber = [x for x in self.lumber_list if x['INVENTORY'] > 30]
        in_stock_lumber = [x for x in in_stock_lumber if x['TYPE'] == 'BOARD FEET']
        in_stock_lumber = [x for x in in_stock_lumber if x['PRICE'] < 6]
        #in_stock_lumber = [x for x in board_lumber if x['SPECIES'].lower() in wood_types]
        return in_stock_lumber




if __name__ == '__main__':
    lumber_scraper = Lumber()
    wood_types = input('Which types of wood? separate by comma. ').split(',')
    wood_types = [x.strip().lower() for x in wood_types]
    selected_types = lumber_scraper.find_lumber(wood_types)
    print(selected_types)
