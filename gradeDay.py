from PySide.QtGui import *
from PySide.QtCore import *
import sys
import os
import mechanize
import cookielib
import time

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.loginPage = 'https://horizon.mcgill.ca/pban1/twbkwbis.P_WWWLogin'
        self.logoutPage = 'https://horizon.mcgill.ca/pban1/twbkwbis.P_Logout'
        self.transcriptPage = 'https://horizon.mcgill.ca/pban1/bzsktran.P_Display_Form?user_type=S&tran_type=V'
        self.br = mechanize.Browser()
        self.cj = cookielib.CookieJar()
        self.br.set_cookiejar(cj)


        self.setWindowTitle("gradeDay")
        self.setWindowIcon(QIcon('alarm.ico'))
        if os.name == 'nt':
            # This is needed to display the app icon on the taskbar on Windows 7
            import ctypes
            myappid = 'JosephSzymborski.gradeDay.1.0.0' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.userLabel = QLabel(self)
        self.userLabel.setText("McGill Username:")
        self.userLabel.setAlignment(Qt.AlignRight)

        self.userTextBox = QLineEdit()

        self.passLabel = QLabel(self)
        self.passLabel.setText("McGill Password:")
        self.passLabel.setAlignment(Qt.AlignRight)

        self.passTextBox = QLineEdit()
        self.passTextBox.setEchoMode(QLineEdit.Password)

        self.pollIntervalLabel = QLabel(self)
        self.pollIntervalLabel.setText("Poll Interval (minutes)")
        self.pollIntervalLabel.setAlignment(Qt.AlignRight)
        self.pollIntervalSpinBox = QSpinBox()
        self.pollIntervalSpinBox.setMinimum(30)

        self.submit = QPushButton()
        self.submit.setText("Check My Grades!")
        self.submit.returnPressed.connect(self.poll)

        self.progress = QProgressBar()
        self.progress.setRange(0,(30*60))
        self.progress.setValue(30)
        #self.progress.setFormat("0")

        self.log = QTextBrowser()
        self.log.append("Enter your user and pass and hit the button")



        layout = QGridLayout()
        layout.addWidget(self.userLabel, 0,0)
        layout.addWidget(self.userTextBox, 0,1)
        layout.addWidget(self.passLabel, 1,0)
        layout.addWidget(self.passTextBox, 1,1)
        layout.addWidget(self.pollIntervalLabel,2,0)
        layout.addWidget(self.pollIntervalSpinBox,2,1)
        layout.addWidget(self.submit, 3,0,2,0)
        layout.addWidget(self.progress, 5,0,2,0)
        layout.addWidget(self.log, 7,0,2,0)
        self.setLayout(layout)


   def poll(self):
     pass



app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
