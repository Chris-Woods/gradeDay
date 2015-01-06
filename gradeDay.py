####################
#
# gradeDay by Joseph Szymborski
# a fork of Tina Latif's minervahacker/GetGrades
#
# This Source Code Form is subject to the
# terms of the Mozilla Public License, v.
# 2.0. If a copy of the MPL was not
# distributed with this file, You can
# obtain one at
# http://mozilla.org/MPL/2.0/.
#
# ##################

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
    gradesUpdated = Signal(int)
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
            self.sendEmailNotif()
            self.gradesUpdated.emit(True)
        else:
            self.tick.emit({"console":"<font color='red'><b>No new grades :(</b></font>"})

    def sendEmailNotif(self):
        import smtplib
        import random
        import re
        session = smtplib.SMTP("smtp.mcgill.ca",587)
        result  = session.ehlo()
        if result[0] != 250:
            return (False, "No response from server.")

        result = session.starttls()


        if result[0] != 220:
            return (False, "Couldn't start STARTTLS session.")

        result = session.login(self.username, self.password)
        if result[0] != 235:
            return (False, "Authentication failed.")

        if re.match("[\w,\.,\d,-]*@mail.mcgill.ca",self.username) == None:
            return (False, "Invalid email.")

        headers = ["from: "+self.username,
                    "subject: Your Grades Have Been Updated!",
                    "to: "+self.username,
                    "mime-version: 1.0",
                    "content-type: text"]
        headers = "\r\n".join(headers)

        tagPool = ["\"C's get degrees\" \r\n ~ McGill Proverb","PS: Stop e-mailing yourself, ya' crazy person", "PS: You may have won a free ice-cream at Frostbite", "PS: You'll feel better if you write an article for the McGill Daily about how your marks are a major cause of microagression/rape culture/gender binaries/race hate/priviledge/triggers"]
        tag = random.choice(tagPool)
        body = "Hi!\r\nDon't freak, but your grades have been updated (OMG!).\r\nWhat are you waiting for, rush to Minerva, mistype your password a billion times in nervous anticipation and find out what the damage is. \r\nLove, \r\nJoseph from gradeDay\r\n\r\n"+tag

        session.sendmail(self.username,self.username,headers+"\r\r\n"+body)
        return (True, "Success")

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
                minuteFloat = (float(i)/60.0)
                i -= 1
                #self.progress.setValue(seconds - i)
                self.tick.emit({"progress":self.seconds - i})
                if minuteFloat % 5 == 0:
                    #self.log.append(str(minutes)+" minutes remaining")
                    self.tick.emit({"console":"<font color='black'>"+str(minutes)+" minutes until next check</font>"})
                if i < 60 and minutes % 5:
                    #self.log.append(str(i)+" seconds remaining")
                    self.tick.emit({"console":"<font color='black'>"+str(i)+" seconds until next check</font>"})

            else:
                self.check(grades)
                i = self.seconds
            time.sleep(1)



class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.alertSound = None
        self.alarm = None
        self.app = None
        self.getGrades = None
        self.seconds = 0
        self.setWindowTitle("gradeDay")
        self.setWindowIcon(QIcon('alert-icon.png'))
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        if os.name == 'nt':
            # This is needed to display the app icon on the taskbar on Windows 7
            import ctypes
            myappid = 'JosephSzymborski.gradeDay.1.0.0' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


        self.appTitle = QLabel(self)
        self.appTitle.setText("<font size='58'><b>gradeDay</b></font>")
        self.appTitle.setAlignment(Qt.AlignCenter)

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
        self.pollIntervalSpinBox.setValue(30)
        self.pollIntervalSpinBox.setMinimum(15)

        self.submit = QPushButton()
        self.submit.setText("Check My Grades!")
        self.submit.released.connect(self.poll)

        self.progress = QProgressBar()
        self.progress.setRange(0,(30*60))
        self.progress.setFormat("0s rem.")
        self.progress.setValue(30*60)




        self.log = QTextBrowser()
        self.log.append("Enter your user and pass and hit the button")

        self.about = QPushButton()
        self.about.setIcon(QIcon("info.png"))

        self.about.released.connect(self.showAbout)

        layout = QGridLayout()
        layout.addWidget(self.appTitle, 0,0,2,0)
        layout.addWidget(self.userLabel, 2,0)
        layout.addWidget(self.userTextBox, 2,1)
        layout.addWidget(self.passLabel, 3,0)
        layout.addWidget(self.passTextBox, 3,1)
        layout.addWidget(self.pollIntervalLabel,4,0)
        layout.addWidget(self.pollIntervalSpinBox,4,1)
        layout.addWidget(self.submit, 5,0,2,0)
        layout.addWidget(self.progress, 7,0,2,0)
        layout.addWidget(self.log, 9,0,2,0)
        layout.addWidget(self.about, 9,3)
        self.setLayout(layout)


    def poll(self):
        if self.alarm == True:
            self.alertSound.stop()
            self.alarm = False
            self.submit.setText("Check My Grades!")
            self.submit.setIcon(QIcon())
            self.appTitle.setText("<font size='58'><b>gradeDay</b></font>")

        else:
            if self.getGrades is not None and self.getGrades.isRunning():
                self.getGrades.terminate()
                self.getGrades.wait()
            self.progress.setMaximum(self.pollIntervalSpinBox.value()*60)
            self.getGrades = GetGrades()
            self.getGrades.tick.connect(self.updateProgress, Qt.QueuedConnection)
            self.getGrades.gradesUpdated.connect(self.alert)
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


    def alert(self, status):
        if status == 1:
            self.appTitle.setText("<font size='58' color='red'><b>GRADES UP (OMG)</b></font>")
            self.submit.setText("Turn Off Alarm")
            self.submit.setIcon(QIcon("close.png"))
            self.alertSound = QSound("voicealert.wav")
            self.alertSound.play()
            self.alarm = True


    def closeEvent(self, event):
        self.alertSound.stop()


    def showAbout(self):
        about = About()
        about.exec_()



class About(QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon('alert-icon.png'))

        self.aboutTextBrowser = QTextBrowser()
        self.aboutTextBrowser.setSource("about.html")

        layout = QGridLayout()
        layout.addWidget(self.aboutTextBrowser, 0,0)
        self.setLayout(layout)




app = QApplication(sys.argv)
form = Form()
form.app = app
form.show()
app.exec_()
