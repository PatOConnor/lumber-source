from rocklerscraper import RocklerScraper
from rich.columns import Columns
from rich.panel import Panel
from rich.layout import Layout
from rich import print
import os

def main():
    wood_filter = RocklerCLI()
    running = True
    while(running):
        #user-input where content-box displays stores
        storeID = wood_filter.get_store_id()
        running = wood_filter.get_wood_data(storeID)

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
        #setting layout of CLI widgets
        self.wood_layout = Layout(name="wrapper")
        self.wood_layout.split_column(
            Layout(name="buffer_box", size=1),
            Layout(name="disclaimer_box", size=4),
            Layout(name="content_box", size=26),
            Layout(name="infobox", size=4),
        )
        self.wood_layout["infobox"].split_row(
            Layout(name="message", size=100),
            Layout(name="title"),
        )
        self.wood_layout["buffer_box"].update(Panel(" "))
        self.wood_layout["disclaimer_box"].update(Panel("Lumber Source uses data scraped from the Rockler Woodworking website and is no way affiliated with Rockler woodworking or any of its parents, siblings or subsidiaries"))
        self.wood_layout["title"].update(Panel("Lumber Sourcing Tool", expand=False))
        self.wood_layout['message'].update("Loading...")
        self.wood_layout['content_box'].update("Loading...")
        self.display_ui()        
        self.scraper = RocklerScraper()
        #creating panels for the stores at initialization:
        #wrapping the city names and numbers in styling and linebreaks:
        panel_strings = [f'[b]{self.add_linebreaks_to(x, 16)}\t [yellow]#{rockler_stores[x]}[/yellow][/b]' for x in rockler_stores]
        #chopping into two pages for placability
        self.store_panels_1 = [Panel(x) for x in panel_strings[:24]]
        self.store_panels_2 = [Panel(x) for x in panel_strings[24:]]
        self.store_panel_state = 2#its 2 so it swaps to state 1
        #will be filled in with a 2d list of Panels
        self.data_panels = []
        
    """Updates the infobox and content panels with the list of stores"""
    def get_store_id(self)->str:
        self.wood_layout["message"].update(Panel('which store # would you like to go to? Press Enter for next page.'))
        self.update_stores()
        good_input = False
        while(not good_input):
            os.system("cls" if os.name=='nt' else 'clear')
            self.display_ui()
            chosen_store = input('\t:')
            if chosen_store.lower().strip() == '':
                self.update_stores()
                print(self.store_panel_state)
            #catching single-digit inputs 
            if len(chosen_store) == 1: chosen_store = '0'+chosen_store
            #checking if its a valid input
            if chosen_store in rockler_stores.values():
                return chosen_store


    """Updates content panel with the other page"""        
    def update_stores(self):        
        if self.store_panel_state == 2:
            self.wood_layout["content_box"].update(Columns(self.store_panels_1))
            self.store_panel_state = 1
        else:
            self.wood_layout["content_box"].update(Columns(self.store_panels_2))
            self.store_panel_state = 2

    """Main method to be ran over and over"""        
    def get_wood_data(self, storeID):    
        #getting data from chosen store, applying loading screen
        self.wood_layout['message'].update("Loading...")
        self.wood_layout['content_box'].update("Getting Data...")
        self.display_ui()
        self.scraper.get_table(webpage=self.scraper.get_page(storeID))
        #user-input where message box is overwritten with these messages
        search_text = self.get_wood_types()
        min_inv  = self.get_value(default=1.0, msg="Enter the minimum inventory count of what you're looking for: ")
        min_price = self.get_value(default=0.0, msg="Enter the lower bound for the price range: ")
        max_price = self.get_value(default=100.0, msg="Enter the upper bound for the price range: ")
        board_search = self.get_bool(default=True, msg="Are you searching for Boards? Input 'y' if so. ")
        boardfeet_search = self.get_bool(default=True, msg="Are you searching for Board Feet? Input 'y' if so. ")
        #filtering data
        self.wood_data = self.scraper.filter_table(search_text, min_inv, min_price, max_price, 
                        board_search, boardfeet_search)
        #user-input loop where user can cycle through pages of collected data
        self.wood_data_page_num = 0
        self.create_data_panels()
        self.print_data()
        #ask for another search
        self.wood_layout["infobox"]["message"].update(Panel('Would you like to search again?', expand=False))
        self.display_ui()
        run_again = input('\t:')
        if run_again.lower() in  ['y', 'yes']: 
            return True
        return False



    def display_ui(self):
        os.system("cls" if os.name=='nt' else 'clear')
        print(self.wood_layout)




    """Updates content panel with the pages of data"""
    def print_data(self, page_num=0)->None:
        self.wood_layout["message"].update(Panel('Here are your results! Press enter to cycle through, enter "back" to go back one page, "quit" to exit results.'))
        while(True):
            if (len(self.data_panels) == 0):
                self.wood_layout["content_box"].update(Panel("No matching items were found. "))
            else:
                self.wood_layout["content_box"].update(Columns(self.data_panels[page_num]))
            self.display_ui()
            scroll = input('\t:').lower().strip()
            if scroll == '':
                #+= and -= operators are avoided to make the 1-line if/else loop the pages
                page_num = page_num + 1 if page_num != len(self.data_panels)-1 else 0
            elif scroll == 'back':
                page_num = page_num - 1 if page_num != 0 else len(self.data_panels)-1
            elif scroll == 'quit':
                break

    """Takes the list of dicts and creates a nested list of panels"""
    def create_data_panels(self):
        panels = [Panel(self.get_data_string(x)) for x in self.wood_data]
        self.data_panels = [panels[i:i+10] for i in range(0, len(panels), 10)]

    """Formats a wood dictionary entry into the text markup for a panel"""            
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




        #TODO: Gotta merge these methods into one complex one
    """I need to incorporate this into the function below"""
    def get_wood_types(self):
        self.wood_layout["message"].update(Panel("Enter Types of Wood You are Searching for, separated by commas.\nPress Enter with no text to see all species of wood in stock.", expand=False))
        self.display_ui()
        woods = input('\t:')
        return woods.strip()

    """Displays msg in the message box and returns the default value if input is bad"""
    def get_value(self, default:float, msg:str)->float:
        self.wood_layout["infobox"]["message"].update(Panel(msg, expand=False))
        self.display_ui()
        val = input('\t:').strip()
        try:
            val = float(val)
        except ValueError:
            val = default
        return val

    """this also needs to get merged into the function above"""
    def get_bool(self, default, msg:str)->bool:
        self.wood_layout["infobox"]["message"].update(Panel(msg, expand=False))
        self.display_ui()
        val = input('\t:').lower().strip()
        if val == 'y':
            return True
        elif val == '':
            return default
        return False


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




#todo: merge the 3 input functions into one
# keypress input to go backwards?
# page numbers
# finalize disclaimers
# final formatting on city cards
