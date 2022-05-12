from rocklerscraper import RocklerScraper
from rich import print, columns, panel

def main():
    print("\n********************\n*\n* Lumber Sourcing Tool\n*\n********************")
    running = True
    while(running):
        get_wood_data()
        run_again = input('Would you like to search again?')
        if run_again.lower() != 'y': 
            running = False

    
def get_wood_data():    
    storeID = get_store_id()
    scraper = RocklerScraper(storeID)
    scraper.get_table(webpage=scraper.get_page(storeID))
    
    search_text = get_wood_types()
    min_inv  = get_value(default=1.0, msg="\nEnter the minimum inventory count of what you're looking for: ")
    min_price = get_value(default=0.0, msg="\nEnter the lower bound for the price range: ")
    max_price = get_value(default=100.0, msg="\nEnter the upper bound for the price range: ")
    board_search = get_bool(default=True, msg="\nAre you searching for Boards? Input 'y' if so. ")
    boardfeet_search = get_bool(default=True, msg="\nAre you searching for Board Feet? Input 'y' if so. ")
    print(search_text, min_inv, min_price, max_price, board_search, boardfeet_search)
    input()
    data = scraper.filter_table(search_text, min_inv, min_price, max_price, 
                    board_search, boardfeet_search)
    print_data(data)


def get_wood_types():
    print("********************\n")
    print("Enter Types of Wood You are Searching for, separated by commas.")
    woods = input("Press Enter with no text to see all species of wood in stock. \n")
    return woods.strip()

def get_store_id():
    show_cities = input("\nWould You Like to see the list of stores?\nEnter 'y' if so: ")
    if show_cities and show_cities.lower()=='y':
        for store in RocklerScraper.rockler_stores:
            print(RocklerScraper.rockler_stores[store], store)
    chosen_store = input('which store # would you like to go to? ')
    if len(chosen_store) == 1: 
        chosen_store = '0'+chosen_store
    print('\nPlease wait while the webpage is accessed... ')
    return chosen_store


"""this is a boilerplate around the input function to only provide perperly typed input"""
def get_value(default:float, msg:str)->float:
    val = input(msg).strip()
    try:
        val = float(val)
    except ValueError:
        val = default
    return val

def get_bool(default, msg:str)->bool:
    val = input(msg)
    if val.lower().strip() == 'y':
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
    desc = add_linebreaks_to(data['DESCRIPTION'])
    #manually adding line-breaks at 20 chars per line
    if len(desc) > 20:
        desc = desc[:20]+'\n'+desc[20:]
    if len(desc) > 42:
        desc = desc[:41]+'\n'+desc[41:]
    inv = f"[yellow]Stock: [/yellow]{data['INVENTORY']}\n"
    price = f"[green][b]Price: ${data['PRICE']}"
    woodtype = '/board[/b][/green]' if data['TYPE'] == 'BOARD' else '/bdft[/b][/green]'

    return species+sku+desc+inv+price+woodtype

        # todo
def add_linebreaks_to(s):
    return s


if __name__ == '__main__':
    main()
