from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

class RocklerScraper():


    def __init__(self, storeID:str='04'):
        self.storeID = storeID
        self.lumber_list = []
        self.service = Service(executable_path=GeckoDriverManager().install())
        self.fireFoxOptions = webdriver.FirefoxOptions()
        self.fireFoxOptions.headless = True
        self.driver = webdriver.Firefox(service=self.service, options=self.fireFoxOptions)

    def get_page(self, storeID:str):
        self.driver.get('https://go.rockler.com/retail_lumber.cfm?store='+storeID)
        button = self.driver.find_element_by_xpath('/html/body/form/input')
        button.click()
        webpage = self.driver.page_source
        return webpage 

   #goes to the webpage for the inventory and returns a dict of info
    def get_table(self, webpage):
        soup = BeautifulSoup(webpage, 'html.parser')
        rows = soup.find_all('tr')[1::]
        new_entry = {}
        for row in rows:
            new_entry['SPECIES'] = row.contents[1].text
            new_entry['SKU'] = row.contents[3].text.strip()
            new_entry['DESCRIPTION'] = row.contents[5].text.strip()
            new_entry['INVENTORY'] = int(row.contents[7].text.strip())
            new_entry['PRICE'], new_entry['TYPE'] = self.price_format(
                                                        row.contents[9].text)
            self.lumber_list.append(new_entry.copy())
        return self.lumber_list


    def price_format(self, price_string:str):        
        if price_string == 'Contact Store':
            return 0, price_string
        words = price_string.split()
        price = words[0][1::]
        price = price.replace(',','')
        if words[-1].lower() == 'foot':
            type_string = 'BOARDFEET' 
        else:
            type_string = 'BOARD'
        return float(price), type_string


    def filter_table(self, search_text:str='', min_inv:float=1.0, 
                     min_price:float=0.0, max_price:float=100.0, 
                     board_search:bool=True, boardfeet_search:bool=True) -> list:
        #splitting search text into list of words or empty string
        wood_types = [x.lower().strip() for x in search_text.split(',')] if search_text != '' else ''        
        filtered_list = []
        #checks if the entry should be filtered into the final list
        for entry in self.lumber_list:
            if wood_types != '' and entry['SPECIES'].lower().strip() not in wood_types:
                continue
            if entry['INVENTORY'] < min_inv:
                continue
            if entry['PRICE'] > max_price:
                continue
            if entry['PRICE'] < min_price:
                continue
            if entry['TYPE'] == 'BOARD' and not board_search:
                continue
            if entry['TYPE'] == 'BOARDFEET' and not boardfeet_search:
               continue
            filtered_list.append(entry.copy())
        return filtered_list
    
    def close_driver(self):
        self.driver.close()