from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLineEdit
from PyQt5.uic import loadUi
from data_storage import DataStorage
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from detection import Detection
from detection_window import DetectionWindow
import configparser
import sys
from mime import send_email
import sqlite3









class SettingsWindow(QMainWindow):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        loadUi('UI/settings_window.ui', self )
        
        self.ui = DetectionWindow()
        self.detection_window = DetectionWindow()
        self.conn = sqlite3.connect('my_database.db')
        self.cursor = self.conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS email_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_email TEXT,
            subject TEXT
        );
        """

        self.cursor.execute(create_table_query)
        self.conn.commit()
        
        
        instance = Detection()
     
        self.sendTo_input.returnPressed.connect(self.update_email)
        #self.location_input.returnPressed.connect(self.update_subject)   
        
        self.pushButton.clicked.connect(self.go_to_detection)
       
        self.show()
    


    def update_email(self):
        recipient_email = self.sendTo_input.text()
        subject = self.location_input.text()

        self.insert_data(recipient_email, subject)

    def insert_data(self, recipient_email, subject):
        # Define SQL query to insert data into the database
        query = "INSERT INTO email_data (recipient_email, subject) VALUES (?, ?)"
        
        # Execute the query with the data
        self.cursor.execute(query, (recipient_email, subject))
        
        # Commit the changes to the database
        self.conn.commit()

     

    def go_to_detection(self):
        if self.detection_window.isVisible():
            print("Detection window is alerady open")
        else:
            
            self.detection_window = DetectionWindow()
            self.detection_window.create_detection_instance()
            self.detection_window.start_detection()

  

    def closeEvent(self, event):
        if self.detection_window.isVisible():
            self.detection_window.detection.running = False
            self.detection_window.close()
            event.accept()
            self.close()

