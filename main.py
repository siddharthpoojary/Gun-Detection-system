from PyQt5.QtWidgets import QApplication
import sys
#from login_window import LoginWindow
from settings_window import SettingsWindow




app = QApplication(sys.argv)
mainwindow = SettingsWindow()



try:
    sys.exit(app.exec_())
except:
    print("Exiting")
    #print("Recipient Email: " ,reci_email) 