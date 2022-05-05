from re import S
from rocklerscraper import RocklerScraper
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from os import path
import sys

def main(username:str=None):
    app = QApplication(sys.argv)
    window = MainWindow(username)
    window.show()
    app.exec()

class OutputWidget(QWidget):
    def __init__(self, filter_data):
        super().__init__()
        self.setWindowTitle("Search Results")
        layout = QVBoxLayout()
        wood_table = QTableWidget()
        wood_table.setColumnCount(5)
        size = len(filter_data)
        wood_table.setRowCount(size)
        wood_table.setHorizontalHeaderLabels("Species;SKU;Description;Inventory;Price".split(";"))
        for i in range(size):
            wood_table.setItem(i, 0, QTableWidgetItem(filter_data[i]['SPECIES']))
            wood_table.setItem(i, 1, QTableWidgetItem(filter_data[i]['SKU']))
            wood_table.setItem(i, 2, QTableWidgetItem(str(filter_data[i]['DESCRIPTION'])))
            wood_table.setItem(i, 3, QTableWidgetItem(str(filter_data[i]['INVENTORY'])))
            price = self.price_format(filter_data[i]['PRICE'], filter_data[i]['TYPE'])
            wood_table.setItem(i, 4, QTableWidgetItem(price))
        layout.addWidget(wood_table)
        self.setLayout(layout)


    def price_format(self, price_data, unit_data):
        # returns formatted string of the price of the given type of wood
        unit_str = '/board' if unit_data == 'BOARD' else '/board foot'
        price_str = '$'+str(price_data)+unit_str
        return price_str








class MainWindow(QMainWindow):
    def __init__(self, username:str=None):
        self.scraper = RocklerScraper()
        
        super().__init__()
        self.setWindowTitle("Rockler Wood Filter")
        #getting style sheet   
        style_file = open(path.dirname(__file__)+'\\rocklerstyle.css')
        gui_style = style_file.read()
        self.setStyleSheet(gui_style)
        self.create_search_widgets()
        self.create_input_widgets()
        self.set_window_layout()

    def create_search_widgets(self):
        #creating widgets of top half
        self.stores_dropdown_widget = QComboBox()
        for store in self.scraper.rockler_stores:
            self.stores_dropdown_widget.addItem(store)
        
        self.load_data_button = QPushButton("Load Data")
        self.load_data_button.setDefault(True)
        self.load_data_button.clicked.connect(self.get_wood_data)

    def create_input_widgets(self):
        #creating widgets of bottom half
        self.species_inputfield = QLineEdit("cherry, maple, walnut")
        self.species_inputfield.setMaxLength(100)

        self.inventory_inputfield = QLineEdit("Min. # In Stock")
        self.inventory_inputfield.setMaxLength(16)
        
        self.price_max_inputfield = QLineEdit("Max Price")
        self.price_max_inputfield.setMaxLength(16)
        
        self.board_checkbox = QCheckBox("board")
        self.board_checkbox.setChecked(True)
        
        self.boardfeet_checkbox = QCheckBox("boardfeet")
        self.boardfeet_checkbox.setChecked(True)
        
        self.help_button = QPushButton("Help")
        self.help_button.setDefault(True)
        self.help_button.clicked.connect(self.display_help)
        
        self.filter_button = QPushButton("Filter Data")
        self.filter_button.setDefault(True)
        self.filter_button.clicked.connect(self.filter_data)

    def set_window_layout(self):
        store_selector_layout = QHBoxLayout()
        store_selector_layout.addWidget(self.stores_dropdown_widget)
        store_selector_layout.addWidget(self.load_data_button)
        store_selector_widget = QWidget()
        store_selector_widget.setLayout(store_selector_layout)
        
        input_params_layout = QHBoxLayout()
        input_params_layout.addWidget(self.inventory_inputfield)
        input_params_layout.addWidget(self.price_max_inputfield)
        input_params_layout.addWidget(self.board_checkbox)
        input_params_layout.addWidget(self.boardfeet_checkbox)
        input_params = QWidget()
        input_params.setLayout(input_params_layout)
        
        params_button_layout = QHBoxLayout()
        params_button_layout.addWidget(self.help_button)
        params_button_layout.addWidget(self.filter_button)
        params_button = QWidget()
        params_button.setLayout(params_button_layout)
        #wrapper of the two buttons
        filter_input_layout = QVBoxLayout()
        filter_input_layout.addWidget(self.species_inputfield)
        filter_input_layout.addWidget(input_params)
        filter_input_layout.addWidget(params_button)
        filter_input_widget = QWidget()
        filter_input_widget.setLayout(filter_input_layout)

        all_widgets_layout = QVBoxLayout()
        all_widgets_layout.addWidget(store_selector_widget)
        all_widgets_layout.addWidget(filter_input_widget)
        all_widgets = QWidget()
        all_widgets.setLayout(all_widgets_layout)
        self.setCentralWidget(all_widgets)

    def get_wood_data(self):
        storeID = str(self.stores_dropdown_widget.currentText())[:2]
        webpage = self.scraper.get_page(storeID=storeID)
        self.scraper.get_table(webpage)

    def display_help(self):
        help_blurbs = [QLabel("How to use the software:"),
                       QLabel("1. Select a store from the dropdown menu and click Load Data"),
                       QLabel("2. Write the species of wood in the text box, separated by commas"),
                       QLabel("3. Input the minimum quantity and maximum price"),
                       QLabel("4. Click Filter Data and see the results in a pop-up window")
                       ]
        help_layout = QVBoxLayout()
        for blurb in help_blurbs:
            help_layout.addWidget(blurb)
        self.help_widget = QWidget()
        self.help_widget.setLayout(help_layout)
        self.help_widget.show()
        
    def filter_data(self):
        try:
            filter_data = self.scraper.filter_table(
                 search_text=self.species_inputfield.text(),
                 min_inv=float(self.inventory_inputfield.text()),
                 max_price=float(self.price_max_inputfield.text()),
                 board_search= self.board_checkbox.isChecked(),
                 boardfeet_search= self.boardfeet_checkbox.isChecked())
            self.output_widget = OutputWidget(filter_data)
            self.output_widget.show()
        except ValueError:
            error_blurb = QLabel("There was improper data submitted in the text fields.")
            error_layout = QVBoxLayout()
            self.error_widget = QWidget()
            error_layout.addWidget(error_blurb)
            self.error_widget.setLayout(error_layout)
            self.error_widget.show()
            print("invalid input")

        
        


if __name__=="__main__":
    main()




    