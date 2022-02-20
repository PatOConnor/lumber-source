from lumber import Lumber
from sys import argv
from rich import print

if __name__ == '__main__':
    lumber_scraper = Lumber()
    #wood_types = input('Which types of wood? separate by comma. ').split(',')
    #wood_types = [x.strip().lower() for x in wood_types]
    wood_types = ['ash' , 'birch']
    dimensions = [0, 24, 72]
    selected_types = lumber_scraper.find_lumber(wood_types, boardlength=72)
    print(selected_types)
