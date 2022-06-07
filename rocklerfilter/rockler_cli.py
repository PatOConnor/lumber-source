from rocklerscraper import RocklerScraper, rockler_stores
from rich.columns import Columns
from rich.panel import Panel
from rich.layout import Layout
from rich import print
from time import sleep
import keyboard
import os

def main():
    wood_filter = RocklerCLI()
    running = True
    while(running):
        #user-input where content-box displays stores
        storeID = wood_filter.get_store_id()
        running = wood_filter.get_wood_data(storeID)



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
        self.wood_layout["disclaimer_box"].update(Panel("Lumber Source uses data scraped from the Rockler Woodworking website and is no way affiliated with Rockler woodworking or any of its affiliates. Lumber Source is a free and open-source application."))
        self.wood_layout["title"].update(Panel("Lumber Sourcing Tool", expand=False))
        self.wood_layout['message'].update("Loading...")
        self.wood_layout['content_box'].update("Loading...")
        self.display_ui()        
        self.scraper = RocklerScraper()
        #creating panels for the stores at initialization:
        #wrapping the city names and numbers in styling and linebreaks:
        panel_strings = [f'[b]{self.add_linebreaks_to(x, 16)} \n[yellow]Store #: {rockler_stores[x]}[/yellow][/b]' for x in rockler_stores]
        #chopping into two pages for placability
        self.store_panels = [[Panel(x) for x in panel_strings[:24]], [Panel(x) for x in panel_strings[24:]]]
        self.store_panel_state = 2#its 2 so it swaps to state 1
        #will be filled in with a 2d list of Panels
        self.data_panels = []
        self.page_num = 0
    
    """Binding a screen clear to the write layout method"""
    def display_ui(self):
        os.system("cls" if os.name=='nt' else 'clear')
        print(self.wood_layout)
        
    """Updates the infobox and content panels with the list of stores"""
    def get_store_id(self)->str:
        self.update_stores()
        while(True):
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
        self.store_panel_state = 1 if self.store_panel_state == 0 else 0
        self.wood_layout["content_box"].update(Columns(self.store_panels[self.store_panel_state]))
        self.wood_layout["message"].update(Panel('which store # would you like to go to? Press Enter for next page.'))

    """Main method to be ran over and over"""        
    def get_wood_data(self, storeID):    
        #getting data from chosen store, applying loading screen
        self.wood_layout['message'].update("Loading...")
        self.wood_layout['content_box'].update("Getting Data...")
        city_name = list(rockler_stores.keys())[list(rockler_stores.values()).index(storeID)]
        self.wood_layout["title"].update(Panel(city_name))
        self.display_ui()
        self.scraper.get_table(webpage=self.scraper.get_page(storeID))
        #user-input where message box is overwritten with these messages
        search_text = self.get_value(default='', input_type=str, 
                        msg="Enter Types of Wood You are Searching for, separated by commas.\nPress Enter with no text to see all species of wood in stock.")
        min_inv  = self.get_value(default=1.0, input_type=float,
                        msg="Enter the minimum inventory count of what you're looking for: ")
        min_price = self.get_value(default=0.0, input_type=float,
                        msg="Enter the lower bound for the price range: ")
        max_price = self.get_value(default=2000.0, input_type=float,
                        msg="Enter the upper bound for the price range: ")
        board_search = self.get_value(default=True, input_type=bool,
                        msg="Are you searching for Boards? Input 'y' if so. ")
        boardfeet_search = self.get_value(default=True, input_type=bool,
                        msg="Are you searching for Board Feet? Input 'y' if so. ")
        #filtering data
        self.wood_data = self.scraper.filter_table(search_text, min_inv, min_price, max_price, 
                        board_search, boardfeet_search)
        #user-input loop where user can cycle through pages of collected data
        self.create_data_panels()
        self.print_data()
        #ask for another search
        self.wood_layout["infobox"]["message"].update(Panel('Would you like to search again?', expand=False))
        self.display_ui()
        run_again = input('\t:')
        if run_again.lower() in  ['y', 'yes']: 
            return True
        return False


    """Updates content panel with the pages of data"""
    def print_data(self, page_num=0)->None:
        self.viewing_data = True
        while(self.viewing_data):
            #arrow keys message
            #self.wood_layout["message"].update(Panel(f'Here are your results! ({page_num}/{len(self.data_panels)})\nUse arrow keys to page forward and back. press ESC to stop viewing.'))
            
            #typed input message
            self.wood_layout["message"].update(Panel(f'Here are your results! ({page_num}/{len(self.data_panels)})\nPress Enter to page forward, input "back" to page backward, and "quit" to stop viewing data.'))

            if (len(self.data_panels) == 0):
                self.wood_layout["content_box"].update(Panel("No matching items were found. "))
            else:
                self.wood_layout["content_box"].update(Columns(self.data_panels[page_num]))
            self.display_ui()
            

            scroll = input('\t:').lower().strip()
            if scroll == '':
                self.page_up()
            elif scroll == 'back':
                self.page_down()
            elif scroll == 'quit':
                self.exit_view()

    # += and -= operators are not used to enable the one line ternary conditional
    """Move foward in data output"""
    def page_up(self): 
        self.page_num = self.page_num + 1 if self.page_num != len(self.data_panels)-1 else 0
    """Move Backward in data output"""
    def page_down(self): 
        self.page_num = self.page_num - 1 if self.page_num != 0 else len(self.data_panels)-1
    """Exit viewing oof data output to perform another search"""
    def exit_view(self): self.viewing_data = False

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


    def get_value(self, default, input_type:type, msg:str):
        self.wood_layout["message"].update(Panel(msg, expand=False))
        self.display_ui()
        val = input('\t:')
        #preventing empty string from casting as false:
        if val == '' and input_type==bool:
            val = True
        #item gets casted to the intended type    
        try:
            val = input_type(val)
        #val is set to default if casting is unavailable
        except ValueError:
            val = default
        return val


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
