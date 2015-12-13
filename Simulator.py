
__author__ = 'Seyed Arian Hosseini 92521105'
import os
import sys
from PyQt4 import QtCore,QtGui
from PyQt4.QtWebKit import *
from PyQt4.QtSvg import QSvgWidget
import pygal

class Simulator:
    def __init__(self,inputTaskFile="inputs.txt"):
        self.inputTaskFile = inputTaskFile
        self.processes = []
        self.maxExecTime = 0
        self.currentProc = None
        self.doneTasks = []
        self.quantomSpent = 0
        self.avgWaitTime = 0
        self.avgResponseTime = 0
        self.avgTurnAroundTime = 0
        self.ganttList = []
        self.labelDict = {}
        self.idleGanttList=[]
        # tempTaskInfoFile = open(os.getcwd()+"/"+self.inputTaskFile,'r')
        # counter = 0
        # for proc in tempTaskInfoFile.readlines():
        #     info = proc.split(" ")
        #     print info
        #     temp = Process(info[0],int(info[1]),int(info[2]))
        #     self.labelDict[info[0]] = counter
        #     counter += 1
        #     self.processes.append(temp)
        #     if temp.execTime > self.maxExecTime:
        #         self.maxExecTime = temp.execTime
        # self.labelDict['idle'] = counter
        # print "maximum exec time: ",self.maxExecTime
        # self.taskQueue = []
        # self.tik = 0
        # self.HRNN()
    def loadInput(self,inputText):
        self.processes = []
        self.maxExecTime = 0
        self.currentProc = None
        self.doneTasks = []
        self.quantomSpent = 0
        self.avgWaitTime = 0
        self.avgResponseTime = 0
        self.avgTurnAroundTime = 0
        self.ganttList = []
        self.labelDict = {}
        self.idleGanttList=[]
        counter = 0
        inputText = inputText.strip()
        for proc in inputText.split("\n"):

            info = proc.split(" ")
            print info
            temp = Process(info[0],int(info[1]),int(info[2]))
            self.labelDict[info[0]] = counter
            counter += 1
            self.processes.append(temp)
            if temp.execTime > self.maxExecTime:
                self.maxExecTime = temp.execTime
        self.labelDict['idle'] = counter
        print "maximum exec time: ",self.maxExecTime
        self.taskQueue = []
        self.tik = 0

    def stepGantt(self,otherProc=None):
        for proc in self.processes:
            if proc == self.currentProc or proc == otherProc:
                proc.ganttList.append(self.labelDict[proc.name])
            else:
                proc.ganttList.append(None)
        if otherProc == 'idle':
            self.idleGanttList.append(self.labelDict['idle'])
        else:
            self.idleGanttList.append(None)

    def drawChart(self):
        line_chart = pygal.Line(show_x_labels=True)
        line_chart.x_labels = map(str,range(len(self.idleGanttList)))
        line_chart.y_labels =[]
        for proc in self.processes:
            line_chart.y_labels.append({'label':proc.name,'value':self.labelDict[proc.name]})
        line_chart.y_labels.append({'label':'idle','value':self.labelDict['idle']})
        for proc in self.processes:
            line_chart.add(proc.name,proc.ganttList)
        line_chart.add('idle',self.idleGanttList)
        line_chart.render_to_file(os.getcwd()+'/chart.svg')

    def FIFO(self):

        while True:
            for proc in self.processes:
                if proc.arrivalTime == self.tik:
                    self.taskQueue.append(proc)
                    print "process ",proc.name," arrived"
            if self.currentProc:
                self.stepGantt() # steping
                self.currentProc.remainingTime -= 1
                self.quantomSpent += 1
                if self.currentProc.remainingTime == 0: #task Done
                    print "process ", self.currentProc.name," done..."
                    self.currentProc.finishTime = self.tik + 1
                    self.doneTasks.append(self.currentProc)
                    self.currentProc = None
            else: #no process
                if len(self.taskQueue) > 0:
                    self.currentProc = self.taskQueue.pop(0) #new task comming in
                    if len(self.doneTasks) > 0 :
                        self.stepGantt(self.doneTasks[-1])
                    else:
                        self.stepGantt()
                    self.ganttList.append(self.labelDict[self.currentProc.name])
                    self.currentProc.startTime = self.tik
                    self.currentProc.remainingTime -= 1
                    self.quantomSpent += 1
                    if self.currentProc.remainingTime == 0:
                        print "process ", self.currentProc.name," done..."
                        self.currentProc.finishTime = self.tik + 1
                        self.doneTasks.append(self.currentProc)
                        self.currentProc = None
                else:
                    if len(self.doneTasks) == len(self.processes): # all processes done
                        print "all processes done..."
                        self.tik += 1
                        break
                    else:
                        self.stepGantt('idle')
            self.tik += 1

        for proc in self.doneTasks:
            print proc.name," ",proc.arrivalTime," ",proc.startTime," ",proc.finishTime
        self.stepGantt(self.doneTasks[-1])
        self.calcResults()
        self.drawChart()

    def LIFO(self):
        while True:
            for proc in self.processes:
                if proc.arrivalTime == self.tik:
                    self.taskQueue.insert(0,proc) # last in first out
                    print "process ",proc.name," arrived"
            if self.currentProc:
                self.stepGantt()
                self.currentProc.remainingTime -= 1
                self.quantomSpent += 1
                if self.currentProc.remainingTime == 0: #task Done
                    print "process ", self.currentProc.name," done..."
                    self.currentProc.finishTime = self.tik + 1
                    self.doneTasks.append(self.currentProc)
                    self.currentProc = None
            else: #no process
                if len(self.taskQueue) > 0:
                    self.currentProc = self.taskQueue.pop(0) #new task comming in
                    if len(self.doneTasks) > 0 :
                        self.stepGantt(self.doneTasks[-1])
                    else:
                        self.stepGantt()
                    self.currentProc.startTime = self.tik
                    self.currentProc.remainingTime -= 1
                    self.quantomSpent += 1
                    if self.currentProc.remainingTime == 0:
                        print "process ", self.currentProc.name," done..."
                        self.currentProc.finishTime = self.tik + 1
                        self.doneTasks.append(self.currentProc)
                        self.currentProc = None
                else:
                    if len(self.doneTasks) == len(self.processes): # all processes done
                        print "all processes done..."
                        self.tik += 1
                        break
                    else:
                        self.stepGantt('idle')
            self.tik += 1

        self.stepGantt(self.doneTasks[-1])
        self.drawChart()
        for proc in self.doneTasks:
            print proc.name," ",proc.arrivalTime," ",proc.startTime," ",proc.finishTime
        self.calcResults()

    def SJF(self):
        while True:
            for proc in self.processes:
                if proc.arrivalTime == self.tik:
                    count = 0
                    while len(self.taskQueue) > count and proc.execTime > self.taskQueue[count].execTime: # the = makes it choose the former rather than latter
                        count += 1
                    self.taskQueue.insert(count,proc)
                    print "process ",proc.name," arrived, putting it in: ", count
            if self.currentProc:
                self.stepGantt()
                self.currentProc.remainingTime -= 1
                self.quantomSpent += 1
                if self.currentProc.remainingTime == 0: #task Done
                    print "process ", self.currentProc.name," done..."
                    self.currentProc.finishTime = self.tik + 1
                    self.doneTasks.append(self.currentProc)
                    self.currentProc = None
            else: #no process
                if len(self.taskQueue) > 0:
                    self.currentProc = self.taskQueue.pop(0) #new task comming in
                    if len(self.doneTasks) > 0 :
                        self.stepGantt(self.doneTasks[-1])
                    else:
                        self.stepGantt()
                    self.currentProc.startTime = self.tik
                    self.currentProc.remainingTime -= 1
                    self.quantomSpent += 1
                    if self.currentProc.remainingTime == 0:
                        print "process ", self.currentProc.name," done..."
                        self.currentProc.finishTime = self.tik + 1
                        self.doneTasks.append(self.currentProc)
                        self.currentProc = None
                else:
                    if len(self.doneTasks) == len(self.processes): # all processes done
                        print "all processes done..."
                        self.tik += 1
                        break
                    else:
                        self.stepGantt('idle')
            self.tik += 1
        for proc in self.doneTasks:
            print proc.name," ",proc.arrivalTime," ",proc.startTime," ",proc.finishTime
        self.stepGantt(self.doneTasks[-1])
        self.drawChart()
        self.calcResults()
    def RoundRobin(self,quantom):
        stateForChart='begining'
        lastProc = None
        self.quantomSpent = 0
        while True:
            for proc in self.processes:
                if proc.arrivalTime == self.tik:
                    self.taskQueue.append(proc)
                    print "process ",proc.name," arrived"
            if self.currentProc:
                self.stepGantt()
                self.currentProc.remainingTime -= 1
                self.quantomSpent += 1
                if self.currentProc.remainingTime == 0: #task Done
                    print "process ", self.currentProc.name," done..."
                    self.currentProc.finishTime = self.tik + 1
                    self.doneTasks.append(self.currentProc)
                    self.currentProc = None
                    self.quantomSpent = 0
                    stateForChart = 'done'
                elif self.quantomSpent == quantom:
                    self.taskQueue.append(self.currentProc)
                    print "process ",self.currentProc.name," going to the end of line..."
                    self.quantomSpent = 0
                    lastProc = self.currentProc
                    self.currentProc = None
                    stateForChart = 'quantom'


            else: #no process
                if len(self.taskQueue) > 0:
                    self.currentProc = self.taskQueue.pop(0) #new task comming in
                    if stateForChart == 'done':
                        if len(self.doneTasks) > 0:
                            self.stepGantt(self.doneTasks[-1])
                        else:
                            self.stepGantt()
                    elif stateForChart == 'quantom':
                        print "last proc: ",lastProc.name
                        self.stepGantt(lastProc)
                        lastProc= None
                    elif stateForChart == 'begining':
                        self.stepGantt()
                    else:
                        print "error", lastProc
                    if self.currentProc.startTime == None:
                        self.currentProc.startTime = self.tik
                    self.currentProc.remainingTime -= 1
                    self.quantomSpent += 1
                    if self.currentProc.remainingTime == 0:
                        stateForChart = 'done'
                        print "process ", self.currentProc.name," done..."
                        self.currentProc.finishTime = self.tik + 1
                        self.doneTasks.append(self.currentProc)
                        self.currentProc = None
                        self.quantomSpent = 0
                    elif self.quantomSpent == quantom:
                        stateForChart = 'quantom'
                        lastProc = self.currentProc
                        self.taskQueue.append(self.currentProc)
                        print "process ",self.currentProc.name," going to the end of line..."
                        self.quantomSpent = 0
                        self.currentProc = None
                else:
                    if len(self.doneTasks) == len(self.processes): # all processes done
                        print "all processes done..."
                        self.tik += 1
                        break
                    else:
                        self.stepGantt('idle')

            self.tik += 1
        self.stepGantt(self.doneTasks[-1])
        self.drawChart()
        for proc in self.doneTasks:
            print proc.name," ",proc.arrivalTime," ",proc.startTime," ",proc.finishTime
        self.calcResults()
    def SRT(self):
        self.currentProc = None
        self.tik = 0
        preemted = False
        while True:
            for proc in self.processes:
                if proc.arrivalTime == self.tik:
                    count = 0
                    while len(self.taskQueue) > count and proc.execTime > self.taskQueue[count].execTime: # the = makes it choose the former rather than latter
                        count += 1
                    self.taskQueue.insert(count,proc)
                    print "process ",proc.name," arrived, putting it in: ", count
                    if self.currentProc != None and self.currentProc.remainingTime > self.taskQueue[count].execTime:
                        preemted = True
                        temp = self.currentProc
                        self.currentProc = self.taskQueue.pop(0)
                        if self.currentProc.startTime == None:
                            print self.currentProc.name, " preemted and start changing"
                            self.currentProc.startTime = self.tik
                        self.taskQueue.insert(0,temp)
                        print "process ",self.currentProc.name," preemted ",self.taskQueue[0].name
            if self.currentProc:
                if preemted:
                    self.stepGantt(self.taskQueue[0])
                    preemted = False
                else:
                    self.stepGantt()
                self.currentProc.remainingTime -= 1
                self.quantomSpent += 1
                if self.currentProc.remainingTime == 0: #task Done
                    print "process ", self.currentProc.name," done..."
                    self.currentProc.finishTime = self.tik + 1
                    self.doneTasks.append(self.currentProc)
                    self.currentProc = None
            else: #no process
                if len(self.taskQueue) > 0:
                    self.currentProc = self.taskQueue.pop(0) #new task comming in
                    if len(self.doneTasks) > 0 :
                        self.stepGantt(self.doneTasks[-1])
                    else:
                        self.stepGantt()
                    if self.currentProc.startTime == None:
                        self.currentProc.startTime = self.tik
                    self.currentProc.remainingTime -= 1
                    self.quantomSpent += 1
                    if self.currentProc.remainingTime == 0:
                        print "process ", self.currentProc.name," done..."
                        self.currentProc.finishTime = self.tik + 1
                        self.doneTasks.append(self.currentProc)
                        self.currentProc = None
                else:
                    if len(self.doneTasks) == len(self.processes): # all processes done
                        print "all processes done..."
                        self.tik += 1
                        break
                    else:
                        self.stepGantt("idle")
            self.tik += 1
        self.stepGantt(self.doneTasks[-1])
        for proc in self.doneTasks:
            print proc.name," ",proc.arrivalTime," ",proc.startTime," ",proc.finishTime
        self.calcResults()
        self.drawChart()

    def stepWaitTime(self):
        for proc in self.taskQueue:
            if proc != self.currentProc:
                proc.waitTime += 1

    def HRNN(self):
        while True:
            for proc in self.processes:
                if proc.arrivalTime == self.tik:
                    #count = 0
                    #while len(self.taskQueue) > count and proc.execTime > self.taskQueue[count].execTime: # the = makes it choose the former rather than latter
                    #    count += 1
                    #self.taskQueue.insert(count,proc)
                    #print "process ",proc.name," arrived, putting it in: ", count
                    self.taskQueue.append(proc)

            if self.currentProc:
                self.stepGantt()
                self.stepWaitTime()
                self.currentProc.remainingTime -= 1
                self.quantomSpent += 1
                if self.currentProc.remainingTime == 0: #task Done
                    print "process ", self.currentProc.name," done..."
                    self.currentProc.finishTime = self.tik + 1
                    self.doneTasks.append(self.currentProc)
                    self.currentProc = None
            else: #no process
                if len(self.taskQueue) > 0:
                    #self.currentProc = self.taskQueue.pop(0) #new task comming in
                    candidateProc = self.taskQueue[0]
                    index = 0
                    candidateIndex = 0
                    for proc in self.taskQueue:
                        temp = 1 + (float(proc.waitTime) / float(proc.execTime))
                        candidateRate = float(1.0) + (candidateProc.waitTime / candidateProc.execTime)
                        if temp >= candidateRate:
                            candidateProc = proc
                            candidateIndex = index
                        index += 1
                    self.currentProc = self.taskQueue.pop(candidateIndex)
                    print "and the winner is: ", self.currentProc.name
                    if len(self.doneTasks) > 0 :
                        self.stepGantt(self.doneTasks[-1])
                    else:
                        self.stepGantt()
                    self.stepWaitTime()
                    self.currentProc.startTime = self.tik
                    self.currentProc.remainingTime -= 1
                    self.quantomSpent += 1
                    if self.currentProc.remainingTime == 0:
                        print "process ", self.currentProc.name," done..."
                        self.currentProc.finishTime = self.tik + 1
                        self.doneTasks.append(self.currentProc)
                        self.currentProc = None
                else:
                    if len(self.doneTasks) == len(self.processes): # all processes done
                        print "all processes done..."
                        self.tik += 1
                        break
                    else:
                        self.stepGantt('idle')
            self.tik += 1
        for proc in self.doneTasks:
            print proc.name," ",proc.arrivalTime," ",proc.startTime," ",proc.finishTime," ",proc.waitTime
        self.stepGantt(self.doneTasks[-1])
        self.drawChart()
        self.calcResults()
    def calcResults(self):
        count = len(self.doneTasks)
        for proc in self.doneTasks:
            temp = (proc.finishTime - proc.execTime - proc.arrivalTime)
            self.avgWaitTime += temp
            temp = proc.startTime - proc.arrivalTime
            self.avgResponseTime += temp
            temp = proc.finishTime - proc.arrivalTime
            self.avgTurnAroundTime += temp
        self.avgTurnAroundTime = float(self.avgTurnAroundTime) / float(count)
        self.avgWaitTime = float(self.avgWaitTime) / float(count)
        self.avgResponseTime = float(self.avgResponseTime) / float(count)
        print "avg waitTime: ", self.avgWaitTime
        print "avg Respose: ",self.avgResponseTime
        print "avg TurnAroundTime: ",self.avgTurnAroundTime

    def runProcess(self,quantom):
        pass


class Process:
    def __init__(self,name,arrivalTime,execTime):
        self.name = name
        self.arrivalTime = arrivalTime
        self.execTime = execTime
        self.startTime = None
        self.finishTime = None
        self.remainingTime = execTime
        self.ganttList=[]
        self.waitTime = 0.0


class LineEdit(QtGui.QLineEdit):
    def __init__(self,name=''):
        super(LineEdit,self).__init__()
        self.name = name

    def focusInEvent(self,e):
        if self.text() == self.name:
            self.setText('')
    def focusOutEvent(self,e):
        if not self.text():
            self.setText(self.name)


class ListWidg(QtGui.QListWidget):
    def __init__(self):
        super(ListWidg,self).__init__()

class Button(QtGui.QToolButton):
    def __init__(self,text,parent=None):
        super(Button,self).__init__(parent)
        self.setText(text)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)

class TextEdit(QtGui.QTextEdit):
    def __init__(self,text,parent=None):
        super(TextEdit,self).__init__(parent)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())
class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.simulator = Simulator()

        self.initUI()

    def fifoFunc(self):
        text = str(self.input.toPlainText())
        print text
        self.simulator.loadInput(text)
        self.simulator.FIFO()
        self.showResults()
    def lifoFunc(self):
        text = str(self.input.toPlainText())
        print text
        self.simulator.loadInput(text)
        self.simulator.LIFO()
        self.showResults()
    def srtFunc(self):
        text = str(self.input.toPlainText())
        print text
        self.simulator.loadInput(text)
        self.simulator.SRT()
        self.showResults()
    def sjfFunc(self):
        text = str(self.input.toPlainText())
        print text
        self.simulator.loadInput(text)
        self.simulator.SJF()
        self.showResults()
    def rrFunc(self):
        text = str(self.input.toPlainText())
        print text
        self.simulator.loadInput(text)
        try:
            quantom = int(str(self.rrQuantom.text()))
        except:
            quantom = 2
        self.simulator.RoundRobin(quantom)
        self.showResults()
    def hrrnFunc(self):
        text = str(self.input.toPlainText())
        print text
        self.simulator.loadInput(text)
        self.simulator.HRNN()
        self.showResults()

    def showResults(self):
        self.result.clear()
        text = "avg waitTime: "+ str(self.simulator.avgWaitTime)+ "\navg Respose: "+ str(self.simulator.avgResponseTime)+"\navg TurnAroundTime: "+str(self.simulator.avgTurnAroundTime)
        self.result.insertPlainText(text)
    def showChart(self):
        newwindow = QtGui.QWidget()
        newwindow.resize(1000,700)
        item = QGraphicsWebView()
        item.load(QtCore.QUrl().fromLocalFile(QtCore.QString(os.getcwd()+"/chart.svg")))
        view = QtGui.QGraphicsView()
        scene = QtGui.QGraphicsScene(newwindow)
        view.resize(800,610)
        scene.addItem(item)
        view.setScene(scene)
        view.show()
        # #widget = QSvgWidget(os.getcwd()+"/bar_chart.svg")
        # #widget.show()
        newwindow.resize(item.size())
        newwindow.show()

    def initUI(self):

        #QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        #self.setToolTip('This is a <b>QWidget</b> widget')
        self.input = TextEdit("",self)
        self.input.insertPlainText("""p1 0 3
p2 2 3
p3 3 5
p4 4 2
p5 8 3""")
        self.fifoBtn = Button("FIFO",self)
        self.fifoBtn.clicked.connect(lambda:self.fifoFunc())
        self.sjfBtn = Button("SJF",self)
        self.sjfBtn.clicked.connect(lambda:self.sjfFunc())
        self.srtBtn = Button("SRT",self)
        self.srtBtn.clicked.connect(lambda:self.srtFunc())
        self.lifoBtn = Button("LIFO",self)
        self.lifoBtn.clicked.connect(lambda:self.lifoFunc())
        self.rrBtn = Button("RR",self)
        self.rrQuantom = LineEdit("Quantom")
        self.rrQuantom.setText("Quantom")
        self.rrBtn.clicked.connect(lambda:self.rrFunc())
        self.hrrnBtn = Button("HRRN",self)
        self.hrrnBtn.clicked.connect(lambda:self.hrrnFunc())
        self.drawChart = Button("Gantt Chart")
        self.drawChart.clicked.connect(lambda:self.showChart())
        self.result = TextEdit("result",self)
        self.result.setReadOnly(True)
        self.result.insertPlainText("result will be here")

        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(4)
        self.layout.addWidget(self.input,0,0,8,2)
        self.layout.addWidget(self.fifoBtn,0,2,1,1)
        self.layout.addWidget(self.lifoBtn,0,3,1,1)
        self.layout.addWidget(self.sjfBtn,1,2,1,1)
        self.layout.addWidget(self.srtBtn,1,3,1,1)
        self.layout.addWidget(self.rrBtn,2,2,1,1)
        self.layout.addWidget(self.rrQuantom,2,3,1,1)
        self.layout.addWidget(self.hrrnBtn,3,2,1,1)
        self.layout.addWidget(self.drawChart,3,3,1,1)
        self.layout.addWidget(self.result,4,2,4,2)
        self.setLayout(self.layout)



        self.setGeometry(300, 300, 550, 450)
        self.setWindowTitle('OS scheduling simulator')
        self.show()


def main():
    #sim = Simulator("inputs.txt")
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

