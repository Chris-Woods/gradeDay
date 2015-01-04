from PySide.QtGui import *
from PySide.QtCore import *
import sys
import os
import mechanize
import cookielib
import time


class GetGrades(QThread):
    loginPage = 'https://horizon.mcgill.ca/pban1/twbkwbis.P_WWWLogin'
    logoutPage = 'https://horizon.mcgill.ca/pban1/twbkwbis.P_Logout'
    transcriptPage = 'https://horizon.mcgill.ca/pban1/bzsktran.P_Display_Form?user_type=S&tran_type=V'
    br = mechanize.Browser()
    cj = cookielib.CookieJar()
    br.set_cookiejar(cj)

    tick = Signal(dict)
    seconds = 0

    def __init__(self, parent=None):
        super(GetGrades, self).__init__(parent)

    def check(self):

        self.tick.emit({"console":"Checking..."})
        # init transcript
        grades = getTranscript()

        newGrades = getTranscript()
        if 'UNOFFICIAL Transcript' not in newGrades:
            # probably problem with minerva/internet
            self.tick.emit({"console":"<font color='red'>ERROR: Unable to fetch grades</font>"})
        if newGrades != grades:
            grades = newGrades
            print "OMG GRADES ARE UP"
            time.sleep(1800)
        else:
            print "No new grades :("
            time.sleep(30)

    def run(self):
        i = self.seconds
        self.tick.emit({"console":"Polling has begun."})
        self.check()
        while(True):
            if (i > 0):
                minutes = (i/60)

                i -= 1
                #self.progress.setValue(seconds - i)
                self.tick.emit({"progress":self.seconds - i})
                if minutes % 5 == 0:
                    #self.log.append(str(minutes)+" minutes remaining")
                    self.tick.emit({"console":str(minutes)+" minutes until next check"})
                if i < 60 and minutes % 5:
                    #self.log.append(str(i)+" seconds remaining")
                    self.tick.emit({"console":str(i)+" seconds until next check"})

            else:
                self.check()
                i = self.seconds
            time.sleep(1)



class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)


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
        self.pollIntervalSpinBox.setValue(30)

        self.submit = QPushButton()
        self.submit.setText("Check My Grades!")
        self.submit.released.connect(self.poll)

        self.progress = QProgressBar()
        self.progress.setRange(0,(30*60))
        self.progress.setValue(self.pollIntervalSpinBox.value()*60)



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
        self.getGrades = GetGrades()
        self.getGrades.tick.connect(self.updateProgress, Qt.QueuedConnection)
        self.getGrades.seconds = self.pollIntervalSpinBox.value()*60
        self.getGrades.start()

    def updateProgress(self, data):
        if "console" in data:
            self.log.append(data["console"])
        if "progress" in data:
            self.progress.setValue(data["progress"])



app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
