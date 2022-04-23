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
        layout = QVBoxLayout()
        self.label = QLabel("Search Results")
        layout.addWidget(self.label)
        

        wood_table = QTableWidget()
        wood_table.setColumnCount(5)
        size = len(filter_data)
        wood_table.setRowCount(size)
        for i in range(size):
            wood_table.setItem(i, 0, QTableWidgetItem(filter_data[i]['SPECIES']))
            wood_table.setItem(i, 1, QTableWidgetItem(filter_data[i]['SKU']))
            wood_table.setItem(i, 2, QTableWidgetItem(filter_data[i]['DESCRIPTION']))
            wood_table.setItem(i, 3, QTableWidgetItem(filter_data[i]['INVENTORY']))
            wood_table.setItem(i, 4, QTableWidgetItem(filter_data[i]['PRICE']))        
        self.setLayout(layout)





class MainWindow(QMainWindow):
    def __init__(self, username:str=None):
        self.scraper = RocklerScraper()
        
        super().__init__()
        self.setWindowTitle("Rockler Wood Filter")
        #getting style sheet   
        style_file = open(path.dirname(__file__)+'\\rocklerstyle.css')
        gui_style = style_file.read()
        self.setStyleSheet(gui_style)

        #creating widgets of top half
        self.stores_dropdown_widget = QComboBox()
        for store in self.scraper.rockler_stores:
            self.stores_dropdown_widget.addItem(store)
        
        load_data_button = QPushButton("Load Data")
        load_data_button.setDefault(True)
        load_data_button.clicked.connect(self.get_wood_data)

        #creating widgets of bottom half
        self.species_inputfield = QLineEdit("walnut, zebrawood")
        self.species_inputfield.setMaxLength(100)

        self.inventory_inputfield = QLineEdit("0")
        self.inventory_inputfield.setMaxLength(8)
        
        self.price_max_inputfield = QLineEdit("100")
        self.price_max_inputfield.setMaxLength(8)
        
        self.board_checkbox = QCheckBox("board")
        self.board_checkbox.setChecked(True)
        
        self.boardfeet_checkbox = QCheckBox("boardfeet")
        self.boardfeet_checkbox.setChecked(True)
        
        help_button = QPushButton("Help")
        help_button.setDefault(True)
        help_button.clicked.connect(self.display_help)
        
        filter_button = QPushButton("Filter Data")
        filter_button.setDefault(True)
        filter_button.clicked.connect(self.filter_data)

        #setting layout of window
        store_selector_layout = QHBoxLayout()
        store_selector_layout.addWidget(self.stores_dropdown_widget)
        store_selector_layout.addWidget(load_data_button)
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
        params_button_layout.addWidget(help_button)
        params_button_layout.addWidget(filter_button)
        params_button = QWidget()
        params_button.setLayout(params_button_layout)
        
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
        help_blurb = QLabel(""""How to use the software""")
        self.help_widget = QWidget()
        self.help_widget.addWidget(help_blurb)
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
            self.error_widget = QWidget()
            self.error_widget.addWidget(error_blurb)
            self.output_widget.show()
            print("invalid input")

        
        


if __name__=="__main__":
    main()