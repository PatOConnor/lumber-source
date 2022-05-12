from rocklerscraper import RocklerScraper
from rich.columns import Columns
from rich.panel import Panel
from rich.layout import Layout
from rich import print

def main():
    wood_filter = RocklerCLI()
    running = True
    while(running):
        wood_filter.get_wood_data()
        #ask for another search
        wood_filter.wood_layout["infobox"]["message"].update(Panel('Would you like to search again?', expand=False))
        run_again = input()
        if run_again.lower() != 'y': 
            running = False
 
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

class RocklerCLI:
    def __init__(self):
        self.wood_layout = Layout(name="wrapper")
        self.wood_layout.split_column(
            Layout(name="disclaimer_box", size=4),
            Layout(name="content_box", size=28),
            Layout(name="infobox", size=4),
        )
        self.wood_layout["infobox"].split_row(
            Layout(name="message", size=100),
            Layout(name="title"),
        )
        self.wood_layout["disclaimer_box"].update(Panel("Lumber Source uses data scraped from the Rockler Woodworking website and is no way affiliated with Rockler woodworking or any of its parents, siblings or subsidiaries"))
        self.wood_layout["title"].update(Panel("Lumber Sourcing Tool", expand=False))
        print('\nLoading... ')
        self.scraper = RocklerScraper()
        
    def get_wood_data(self):    
        storeID = self.get_store_id()
        self.scraper.get_table(webpage=self.scraper.get_page(storeID))
        search_text = self.get_wood_types()
        min_inv  = self.get_value(default=1.0, msg="Enter the minimum inventory count of what you're looking for: ")
        min_price = self.get_value(default=0.0, msg="Enter the lower bound for the price range: ")
        max_price = self.get_value(default=100.0, msg="Enter the upper bound for the price range: ")
        board_search = self.get_bool(default=True, msg="Are you searching for Boards? Input 'y' if so. ")
        boardfeet_search = self.get_bool(default=True, msg="Are you searching for Board Feet? Input 'y' if so. ")
        #print(search_text, min_inv, min_price, max_price, board_search, boardfeet_search)
        #input()
        data = self.scraper.filter_table(search_text, min_inv, min_price, max_price, 
                        board_search, boardfeet_search)
        self.print_data(data)


    def get_wood_types(self):
        self.wood_layout["message"].update(Panel("Enter Types of Wood You are Searching for, separated by commas.\nPress Enter with no text to see all species of wood in stock.", expand=False))
        #self.wood_layout["infobox"]["message"].update(Panel("Enter Types of Wood You are Searching for, separated by commas.\nPress Enter with no text to see all species of wood in stock.", expand=False))
        print(self.wood_layout)
        woods = input('\t:')
        return woods.strip()

    def get_store_id(self):
        self.wood_layout["message"].update(Panel('which store # would you like to go to? Press Enter for next page.'))
        self.print_stores(page=1)
        good_input = False
        while(not good_input):
            print(self.wood_layout)
            chosen_store = input()
            if chosen_store.lower().strip() == '':
                self.print_stores(page=2)
                continue
            #catching single-digit inputs 
            if len(chosen_store) == 1: chosen_store = '0'+chosen_store
            #checking if its a valid input
            if chosen_store in rockler_stores.values():
                return chosen_store
        
        
        # self.wood_layout["infobox"]["message"].update(Panel(f'\nPlease wait while the webpage for store #{chosen_store} is accessed... '))
        # print(self.wood_layout)
        # #print(Panel(f'\nPlease wait while the webpage for store #{chosen_store} is accessed... ', expand=False))
        return chosen_store

    def print_stores(self, page:int):        
        #wrapping the city names and numbers in styling and linebreaks:
        panel_strings = [f'[b]{self.add_linebreaks_to(x, 16)}\t [yellow]#{rockler_stores[x]}[/yellow][/b]' for x in rockler_stores]
        #chopping into two pages
        panels_1 = [Panel(x) for x in panel_strings[:24]]
        panels_2 = [Panel(x) for x in panel_strings[24:]]
        if page==1:
            self.wood_layout["content_box"].update(Columns(panels_1))
        else:
            self.wood_layout["content_box"].update(Columns(panels_2))
        print(self.wood_layout)

    """this is a boilerplate around the input function to only provide perperly typed input"""
    def get_value(self, default:float, msg:str)->float:
        self.wood_layout["infobox"]["message"].update(Panel(msg, expand=False))
        print(self.wood_layout)
        #print(Panel(msg, expand=False))
        val = input('\t:').strip()
        try:
            val = float(val)
        except ValueError:
            val = default
        return val

    def get_bool(self, default, msg:str)->bool:
        self.wood_layout["infobox"]["message"].update(Panel(msg, expand=False))
        print(self.wood_layout)
        #print(Panel(msg, expand=False))
        val = input('\t:').lower().strip()
        if val == 'y':
            return True
        elif val == '':
            return default
        return False

    def print_data(self, wood_data:list[dict])->None:
        panels = [Panel(self.get_data_string(x)) for x in wood_data]
        self.wood_layout["content_box"].update(Columns(panels))
        #print(Columns(panels))
            
    def get_data_string(self, data:dict)->str:
        species = f"[b][blue]{data['SPECIES']}[/b][/blue]\n"
        sku = f"[b][blue]{data['SKU']}[/b][/blue]\n"
        desc = self.add_linebreaks_to(data['DESCRIPTION'], 20, True)
        inv = f"[yellow]Stock: [/yellow]{data['INVENTORY']}\n"
        price = f"[green][b]${data['PRICE']}"
        if data['TYPE'] == 'BOARD':
            woodtype = '/board[/b][/green]'
        else:
            woodtype = '/bdft[/b][/green]'
        return species+sku+desc+inv+price+woodtype


        

    def add_linebreaks_to(self, s, chars_per_line, ending_linebreak=False):
        outputstr = ''
        for word in s.split():
            newline_index = outputstr.find('\n')
            if len(outputstr) - newline_index + len(word) > chars_per_line:
                outputstr += '\n'
            outputstr += word+' '
        if ending_linebreak: outputstr += '\n'
        return outputstr      



if __name__ == '__main__':
    main()




# TODO: add a "return to the previous page" button
# TODO: show wood type output