from rocklerscraper import RocklerScraper
from rich import print, columns, panel

def main():
    print(panel.Panel("Lumber Sourcing Tool", expand=False))
    running = True
    while(running):
        get_wood_data()
        print(panel.Panel('Would you like to search again?', expand=False))
        run_again = input()
        if run_again.lower() != 'y': 
            running = False

    
def get_wood_data():    
    storeID = get_store_id()
    scraper = RocklerScraper(storeID)
    scraper.get_table(webpage=scraper.get_page(storeID))
    
    search_text = get_wood_types()
    min_inv  = get_value(default=1.0, msg="Enter the minimum inventory count of what you're looking for: ")
    min_price = get_value(default=0.0, msg="Enter the lower bound for the price range: ")
    max_price = get_value(default=100.0, msg="Enter the upper bound for the price range: ")
    board_search = get_bool(default=True, msg="Are you searching for Boards? Input 'y' if so. ")
    boardfeet_search = get_bool(default=True, msg="Are you searching for Board Feet? Input 'y' if so. ")
    #print(search_text, min_inv, min_price, max_price, board_search, boardfeet_search)
    #input()
    data = scraper.filter_table(search_text, min_inv, min_price, max_price, 
                    board_search, boardfeet_search)
    print_data(data)


def get_wood_types():
    print(panel.Panel("Enter Types of Wood You are Searching for, separated by commas.\nPress Enter with no text to see all species of wood in stock.", expand=False))
    woods = input('\t:')
    return woods.strip()

def get_store_id():
    print(panel.Panel("Would You Like to see the list of stores?\nEnter 'y' if so: ", expand=False))
    show_cities = input('\t:')
    if show_cities and show_cities.lower()=='y':
        print_stores()
    print(panel.Panel('which store # would you like to go to? ', expand=False))
    chosen_store = input('\t:')
    if len(chosen_store) == 1: 
        chosen_store = '0'+chosen_store
    print(panel.Panel(f'\nPlease wait while the webpage for store #{chosen_store} is accessed... ', expand=False))
    return chosen_store


"""this is a boilerplate around the input function to only provide perperly typed input"""
def get_value(default:float, msg:str)->float:
    print(panel.Panel(msg, expand=False))
    val = input('\t:').strip()
    try:
        val = float(val)
    except ValueError:
        val = default
    return val

def get_bool(default, msg:str)->bool:
    print(panel.Panel(msg, expand=False))
    val = input('\t:').lower().strip()
    if val == 'y':
        return True
    elif val == '':
        return default
    return False

def print_data(wood_data:list[dict])->None:
    panels = [panel.Panel(get_data_string(x)) for x in wood_data]
    print(columns.Columns(panels))
        
def get_data_string(data:dict)->str:
    species = f"[b][blue]{data['SPECIES']}[/b][/blue]\n"
    sku = f"[b][blue]{data['SKU']}[/b][/blue]\n"
    desc = add_linebreaks_to(data['DESCRIPTION'], 20, True)
    inv = f"[yellow]Stock: [/yellow]{data['INVENTORY']}\n"
    price = f"[green][b]${data['PRICE']}"
    if data['TYPE'] == 'BOARD':
        woodtype = '/board[/b][/green]'
    else:
        woodtype = '/bdft[/b][/green]'
    return species+sku+desc+inv+price+woodtype

def print_stores():
    #wrapping the city names and numbers in styling and linebreaks:
    panel_strings = [f'[b]{add_linebreaks_to(x, 16)}\t [yellow]#{RocklerScraper.rockler_stores[x]}[/yellow][/b]' for x in RocklerScraper.rockler_stores]
    panels = [panel.Panel(x) for x in panel_strings]
    print(columns.Columns(panels))

    

def add_linebreaks_to(s, chars_per_line, ending_linebreak=False):
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
