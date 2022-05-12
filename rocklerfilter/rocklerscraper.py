from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

class RocklerScraper():


    def __init__(self, storeID:str='04'):
        self.storeID = storeID
        self.lumber_list = []

    def get_page(self, storeID:str):
        self.service = Service(executable_path=GeckoDriverManager().install())
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        driver = webdriver.Firefox(service=self.service, options=fireFoxOptions)
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
    
    #
    rockler_stores = {
    'Altamonte Springs, FL': '36',
    'Arlington, TX'   : '27',
    'Beaverton, OR'   : '17',
    'Bolingbrook, IL' : '39',
    'Brandon, FL'     : '46',
    'Brookfield, WI'  : '07',
    'Buffalo, NY'     : '11',
    'Burnsville, MN'  : '12',
    'Cambridge, MA'   : '04',
    'Cincinatti, OH'  : '16',
    'Concord, CA'     : '25',
    'Denver, CO'      : '03',
    'Fairfax, VA'     : '49',
    'Frisco, TX'      : '38',
    'Garland, TX'     : '40',
    'Indianapolis, IN': '21',
    'Houston, TX'     : '30',
    'Kennesaw, GA'    : '41',
    'Maplewood, MN'   : '13',
    'Minnetonka, MN'  : '14',
    'Moorestown, NJ'  : '47',
    'Novi, MI'        : '08',
    'Olathe, KS'      : '44',
    'Ontario, CA'     : '26',
    'Orange, CA'      : '20',
    'Orland Park, IL' : '42',
    'Pasadena, CA'    : '22',
    'Pittsburg, PA'   : '31',
    'Phoenix, AZ'     : '01',
    'Rocklin, CA'     : '37',
    'Round Rock, TX'  : '45',
    'Salem, NH'       : '34',
    'San Diego, CA'   : '06', 
    'Sandy Springs, GA': '29',
    'Schaumburg, IL'  : '10',
    'Seattle, WA'     : '02',
    'Spring, TX'      : '43',
    'St Louis, MO'    : '19',
    'S. Portland ME'  : '33',
    'Torrance, CA'    : '23',
    'Tukwila, WA'     : '15', 
}