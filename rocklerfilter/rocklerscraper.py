from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

class RocklerScraper():
    def __init__(self, storeID:str='04'):
        self.storeID = storeID

    def get_page(self, storeID:str):
        service = Service(executable_path=GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)
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
                if i == 0: new_entry['SPECIES'] = cell.string
                if i == 1: new_entry['SKU'] = cell.string.strip()
                if i == 2: new_entry['DESCRIPTION'] = cell.string.strip()
                #if i == 2: new_entry['DESCRIPTION'], new_entry['DIMENSIONS'] = self.description_format(cell.string)
                if i == 3: new_entry['INVENTORY'] = int(cell.string.strip())
                if i == 4: new_entry['PRICE'], new_entry['TYPE'] = self.price_format(cell.string)
                i += 1
            self.lumber_list.append(new_entry.copy())
        return self.lumber_list

    def price_format(self, price_string):
        if price_string == 'Contact Store':
            return price_string, price_string
        words = price_string.split()
        price = words[0][1::]
        type_string = 'BOARDFEET' if words[-1].lower() == 'foot' else 'BOARD'
        return float(price), type_string

    def filter_table(self, search_text:str, min_inv:float=1.0, max_price:float=100.0, 
                     board_search:bool=True, boardfeet_search:bool=True):
        wood_types = [x.lower().strip() for x in search_text.split(',')]
        filtered_list = []
        for entry in self.lumber_list:
            if entry['SPECIES'].lower().strip() not in wood_types:
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
                

            #commands to paste into python console during testing: 

    #new_list = scraper.filter_table(search_text='walnut, zebrawood')
    #from rocklerfilter.rocklerscraper import RocklerScraper as rs; scraper = rs(); webpage = scraper.get_page("04"); data = scraper.get_table(webpage);


            #This splits up the product description string into components;
    #import re
    #from fractions import Fraction
    #
    # def description_format(self, desc_string):
    #     #case: 'cherry'
    #     only_desc = r'[A-Za-z ]+'
    #     #case: 'cherry 2x12x48"'
    #     desc_meas = r'([A-Za-z ]+)(([0-9]+(\/[0-9]+)?"?)( ?(X|x) ?)?)+'
    #     #measurements_then_description = r''

    #     if re.fullmatch(only_desc, desc_string):
    #         return desc_string, [0,0,0]

    #     elif re.fullmatch(desc_meas, desc_string):
    #         #gets string into 3 parts
    #         desc_fields = re.split(r'[Xx]', desc_string)
    #         if len(desc_fields) <= 2:
    #             return desc_string, [0,0,0,]
    #         length = desc_fields.pop(-1)
    #         width = desc_fields.pop(-1)
    #         desc_fields = desc_fields[0].split()
    #         depth = desc_fields.pop(-1)
    #         desc = ' '.join(desc_fields)

    #         return desc, [depth, width, length] #format from website

    #     else: #todo: other patterns?
    #         return desc_string, [0,0,0]
