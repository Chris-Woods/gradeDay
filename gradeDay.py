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

    username = ""
    password = ""

    def __init__(self, parent=None):
        super(GetGrades, self).__init__(parent)

    def validate(self):
        successful = False
        self.tick.emit({"console":"Validating your login, please wait..."})
        while not successful:
          self.br.open(self.loginPage)
          self.br.select_form(nr=1)
          self.br.form['sid'] = self.username
          self.br.form['PIN'] = self.password
          self.br.submit()
          response = self.br.response().read()
          if (self.username=="") or (self.password=="") or ("You have entered an invalid McGill Username" in response):
            self.tick.emit({"console":"<font color='red'><b>That user/pass combination is invalid. Please try again.</b></font>"})
            return False
          else:
            self.tick.emit({"console":"<font color='green'><b>You have sucessfully logged in.</b></font>"})
            successful = True
            return True

    def getTranscript(self):
      #login
      self.br.open(self.loginPage)
      self.br.select_form(nr=1)
      self.br.form['sid'] = self.username
      self.br.form['PIN'] = self.password
      self.br.submit()
      #fetch transcript
      self.br.open(self.transcriptPage)
      grades = self.br.response().read()
      self.br.open(self.logoutPage)
      return grades



    def check(self,grades):

        self.tick.emit({"console":"Checking..."})

        newGrades = self.getTranscript()
        if 'UNOFFICIAL Transcript' not in newGrades:
            # probably problem with minerva/internet
            self.tick.emit({"console":"<font color='red'><b>[ERROR] Unable to fetch grades</b></font>"})
        if newGrades != grades:
            self.tick.emit({"console":"<font color='green'><b>GRADES ARE UP (OMG!) - Best of luck!</b></font>"})
        else:
            self.tick.emit({"console":"<font color='red'><b>No new grades :(</b></font>"})

    def run(self):
        if self.validate() == False:
          return False
        i = self.seconds
        self.tick.emit({"console":"Polling has begun."})

        # init transcript
        grades = self.getTranscript()
        self.check(grades)
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
                self.check(grades)
                i = self.seconds
            time.sleep(1)



class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.seconds = 0
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
        self.pollIntervalSpinBox.setMinimum(15)
        self.pollIntervalSpinBox.setValue(30)


        self.submit = QPushButton()
        self.submit.setText("Check My Grades!")
        self.submit.released.connect(self.poll)

        self.progress = QProgressBar()
        self.progress.setRange(0,(30*60))
        self.progress.setValue(self.pollIntervalSpinBox.value()*60)

        self.pollIntervalSpinBox.valueChanged.connect(self.changeProgressMaximum)


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

    def changeProgressMaximum(self):
      self.progress.setMaximum(self.pollIntervalSpinBox.value()*60)
      self.progress.setValue(self.pollIntervalSpinBox.value()*60)

    def poll(self):
        self.getGrades = GetGrades()
        self.getGrades.tick.connect(self.updateProgress, Qt.QueuedConnection)
        self.getGrades.seconds = self.pollIntervalSpinBox.value()*60
        self.seconds = self.pollIntervalSpinBox.value()*60
        self.getGrades.username = self.userTextBox.text()
        self.getGrades.password = self.passTextBox.text()
        self.getGrades.start()

    def updateProgress(self, data):
        if "console" in data:
            self.log.append(data["console"])
        if "progress" in data:
            self.progress.setValue(data["progress"])
            rem = self.seconds - data["progress"]
            if rem < 60:
              self.progress.setFormat(str(rem)+"s rem.")
            else:
              minutes = rem/60
              self.progress.setFormat(str(minutes)+"min rem.")



app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
