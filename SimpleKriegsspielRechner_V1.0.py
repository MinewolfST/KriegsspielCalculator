import numpy as np
import random
import PySimpleGUI as sg


sg.theme("DarkAmber")
#classes and functions for calculations
"""
damageTable = [
                [33,66,99,132,165],
                [30,60,90,120,150],
                [27,54,81,108,135],
                [24,48,72,96,120],
                [21,42,63,84,105],
                [18,36,54,72,90],
                [15,30,45,60,75],
                [12,24,36,48,60],
                [9,18,27,36,45],
                [6,12,18,24,30],
                [3,6,9,12,15]
            ]
"""
sizeDict = {1:"Squad", 2:"Platoon", 3:"Vehicle Platoon", 4:"Heavy Weapons/Tank Platoon"}
expDict = {0:"Green",1:"Unexperienced",2:"Trained",3:"Elite"}

def determineDamage(combatPower):
    allowedRolls = [0,1,2,3,4,5,6,7,8,9,10]
    damageList = [33,30,27,24,21,18,15,12,9,6,3]
    diceRoll = random.choice(allowedRolls)
    return(np.floor(combatPower / damageList[diceRoll]))

class SimpleUnit:                                                       #most infantry
    def __init__(self,name,size,manpower,condition,experience):
        self.name = name
        self.size = size
        self.manpower = manpower
        self.condition = condition
        self.experience = experience
        self.ammunition = 4
        self.isFlanked = False
        self.inShock = False
        self.hasMoved = False
        self.inForest = False
        self.inRange = False
    
    def basicCombatValue(self):
        modifiers = 0
        if(self.inShock):
            modifiers = modifiers -20
        if(self.hasMoved):
            modifiers = modifiers -2
        if(self.inRange):
            modifiers = modifiers +2
        else: modifiers = modifiers -5
        
        if self.ammunition == 0:
            return 0
        else:
            return((self.manpower * self.size) + self.condition + self.experience + modifiers)
    
    def probabilityOfGettingHit(self):
        probability = (self.manpower * self.size) + self.condition + self.experience
        if self.isFlanked:
            probability *= 2
        if self.inForest:
            probability *= 0.5
        if not self.inRange:
            probability *= 0.1
        if self.hasMoved:
            probability *= 0.8
        if self.inShock:
            probability *= 2
        return int(probability)
        
        
    
"""
class ComplexUnit:            #tanks and vehicles
    def __init__(self,size,manpower,condition,experience,armour,penetration,hasMG,isFlanked,inShock,hasMoved,inForest,inRange):
        self.size = size
        self.manpower = manpower
        self.condition = condition
        self.experience = experience
        self.isFlanked = isFlanked
        self.inShock = inShock
        self.hasMoved = hasMoved
        self.inForest = inForest
        self.inRange = inRange
        self.armour = armour
        self.penetration = penetration
        self.hasMG = hasMG
"""
        
class SimpleGame:
    unitsKIA = []
    
    def __init__(self,unitsBlue,unitsRed):
        self.unitsBlue = unitsBlue
        self.unitsRed = unitsRed
    
    def assignHit(self,isBlue):
        pool = []
        if isBlue:
            for u in self.unitsBlue:
                prob = u.probabilityOfGettingHit()
                for i in range(prob):
                    pool.append(u)
        else:
            for u in self.unitsRed:
                prob = u.probabilityOfGettingHit()
                for i in range(prob):
                    pool.append(u)
        return random.choice(pool)

    def applyDamage(self,isBlue,damage):
        combatReport = []
        if not isBlue:
            damageRegister = [0 for u in self.unitsRed]
            while(damage > 0):
                unitHit = self.assignHit(isBlue)
                damageRegister[self.unitsRed.index(unitHit)] += 1
                damage -= 1
            for i in damageRegister:
                if i>0:
                    print("Red Unit " + self.unitsRed[damageRegister.index(i)].name + " has suffered " + str(i) + " damage.")
                    self.unitsRed[damageRegister.index(i)].manpower -= i
                    if i >= 5:
                        conditionChange = 3
                    if i == 3 or i == 4:
                        conditionChange = 2
                    if i == 1 or i == 2:
                        conditionChange = 1
                    combatReport.append([i,conditionChange])
                    self.unitsRed[damageRegister.index(i)]. condition -= conditionChange
                    if self.unitsRed[damageRegister.index(i)].manpower < 1:
                        self.unitsKIA.append(self.unitsRed[damageRegister.index(i)].name)
                else:   
                    combatReport.append([i,0])
        
        else:
            damageRegister = [0 for u in self.unitsBlue]
            while(damage > 0):
                unitHit = self.assignHit(isBlue)
                damageRegister[self.unitsBlue.index(unitHit)] += 1
                damage -= 1
            for i in damageRegister:
                if i>0:
                    print("Blue Unit " + self.unitsBlue[damageRegister.index(i)].name + " has suffered " + str(i) + " damage.")
                    self.unitsBlue[damageRegister.index(i)].manpower -= i
                    if i >= 5:
                        conditionChange = 3
                    if i == 3 or i == 4:
                        conditionChange = 2
                    if i == 1 or i == 2:
                        conditionChange = 1
                    combatReport.append([i,conditionChange])
                    self.unitsBlue[damageRegister.index(i)]. condition -= conditionChange
                    if self.unitsBlue[damageRegister.index(i)].manpower < 1:
                        self.unitsKIA.append(self.unitsBlue[damageRegister.index(i)].name)
                else:
                    combatReport.append([i,0])          
        return combatReport

    def runCombatReportWindow(self,repBlue,repRed):
        layout1 = []
        trigger1 = False
        for i in repBlue:
            if i[0] > 0:
                layout1.append([sg.Text("Blue Unit " + self.unitsBlue[repBlue.index(i)].name + " suffers " + str(i[0]) + " damage and looses " + str(i[1]) + " condition")])
                trigger1 = True
        layout2 = []
        trigger2 = False
        for i in repRed:
            if i[0] > 0:
                layout2.append([sg.Text("Red Unit " + self.unitsRed[repRed.index(i)].name + " suffers " + str(i[0]) + " damage and looses " + str(i[1]) + " condition")])
                trigger2 = True
        if not trigger1:
            layout1.append([sg.Text("No Damage to Blue Units")])
        if not trigger2:
            layout2.append([sg.Text("No Damage to Red Units")])
        
        if len(self.unitsKIA) != 0:
            listKIA = [[sg.Text(u)] for u in self.unitsKIA]
            sg.Popup("KIA Report",listKIA)
            self.unitsKIA.clear()
            
        event,values = sg.Window("Combat Report",[[sg.Text("Combat Resolved")],[sg.Column(layout1,size=(500,(len(repBlue)+1)*10+15)),sg.Column(layout2,size=(500,(len(repRed)+1)*10+5))],[sg.Button("Ok")]]).read(close=True)
        
        

    def resolveCombat(self,involvedBlue,involvedRed):
        
        combatPowerBlue = 0
        combatPowerRed = 0
        
        for u in involvedBlue:
            combatPowerBlue = combatPowerBlue + self.unitsBlue[u].basicCombatValue()
            if(self.unitsBlue[u].inForest):
                combatPowerRed = combatPowerRed -2
            
        
        for u in involvedRed:
            combatPowerRed= combatPowerRed + self.unitsRed[u].basicCombatValue()
            if(self.unitsRed[u].inForest):
                combatPowerBlue = combatPowerBlue -2
            
        print("Blue Combat Power: " + str(combatPowerBlue))
        print("Red Combat Power: " + str(combatPowerRed))
        damageBlue = determineDamage(combatPowerBlue)
        damageRed = determineDamage(combatPowerRed)
        
        reportBlue = self.applyDamage(True,damageRed)
        reportRed = self.applyDamage(False,damageBlue)
        self.runCombatReportWindow(reportBlue,reportRed)
        
        

#other functions
def createSimpleUnits(colour):
    units = []
    event, values = sg.Window('Unit Creator',
                    [[sg.T("Number of " + colour + " units:"), sg.In(key="-num-")],
                    [sg.B('OK')]]).read(close=True)
    for i in range(int(values["-num-"])):
        event, values = sg.Window('Stats ' + str(i+1) + ". unit",
                    [[sg.T("Name:"), sg.In(key='-name-')],
                    [sg.T("Size:"), sg.In(key='-size-')],
                    [sg.T("Manpower:"), sg.In(key='-manpower-')],
                    [sg.T("Condition:"), sg.In(key='-condition-')],
                    [sg.T("Experience:"), sg.In(key='-experience-')],
                    [sg.B('OK')]]).read(close=True)
        units.append(SimpleUnit(values["-name-"],int(values["-size-"]),int(values["-manpower-"]),int(values["-condition-"]),int(values["-experience-"])))
        print("Unit added succesfully")
    return(units)
    
#testing
testB1 = SimpleUnit("TAlpha",2,10,6,3)
testR1 = SimpleUnit("TBeta",2,10,6,2)

testGame = SimpleGame([testB1],[testR1])
testGame.resolveCombat([0],[0])
    
#GUI Stuff


#gui functions and classes
def runStartUpWindow():
    startupWindowLayout = [
                    [sg.Text("Start a new Simple or Complex game")],
                    [sg.Button("Simple"),sg.Button("Complex")]
                    ]
    startupWindow = sg.Window("KriegsspielCalculator Start",startupWindowLayout)

    while True:
        event, values = startupWindow.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "Simple":
            isSimpleGame = True
            startupWindow.close()
        elif event == "Complex":
            isSimpleGame = False
            sg.popup("Not supported yet")
    return(isSimpleGame)


def createMainGuiColumns(Game):

    namesBlue = [i.name for i in Game.unitsBlue]
    namesRed = [i.name for i in Game.unitsRed]

    colUnitsBlue = sg.Column([[sg.Frame("Blue Units",[[sg.Listbox(namesBlue,enable_events=True,key="-ListBlue-",size=(15,20))]],size=(150,400))]])
    colUnitsRed = sg.Column([[sg.Frame("Red Units",[[sg.Listbox(namesRed,enable_events=True,key="-ListRed-",size=(15,20))]],size=(150,400))]])

#constructing state columns, not nice but works
    colBInvolved = []
    colBFlanked = []
    colBinShock = [] 
    colBhasMoved = []
    colBinForest = []
    colBinRange =  []
    for i in namesBlue:
        colBFlanked.append([sg.CBox("",key="isFlankedB" + str(namesBlue.index(i)))])
        colBinShock.append([sg.CBox("",key="inShockB" + str(namesBlue.index(i)))])
        colBhasMoved.append([sg.CBox("",key="hasMovedB" + str(namesBlue.index(i)))])
        colBinForest.append([sg.CBox("",key="inForestB" + str(namesBlue.index(i)))])
        colBinRange.append([sg.CBox("",key="inRangeB" + str(namesBlue.index(i)))])
        colBInvolved.append([sg.CBox("",key="involvedB" + str(namesBlue.index(i)))])


    colStatesBlue = sg.Column([[sg.Frame("Unit States",[[sg.Column([[sg.Frame("Flanked",colBFlanked,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("In Shock",colBinShock,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("Has Moved",colBhasMoved,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("in Forest",colBinForest,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("within Range",colBinRange,size=(100,400))]])
                                                    ]],size=(600,400))]])

    colInvolvedBlue = sg.Column([[sg.Frame("Involved in Combat",colBInvolved,size=(150,400))]],size=(150,450))

    colRInvolved = []
    colRFlanked = []
    colRinShock = [] 
    colRhasMoved = []
    colRinForest = []
    colRinRange =  []
    for i in namesRed:
        colRFlanked.append([sg.CBox("",key="isFlankedR" + str(namesRed.index(i)))])
        colRinShock.append([sg.CBox("",key="inShockR" + str(namesRed.index(i)))])
        colRhasMoved.append([sg.CBox("",key="hasMovedR" + str(namesRed.index(i)))])
        colRinForest.append([sg.CBox("",key="inForestR" + str(namesRed.index(i)))])
        colRinRange.append([sg.CBox("",key="inRangeR" + str(namesRed.index(i)))])
        colRInvolved.append([sg.CBox("",key="involvedR" + str(namesRed.index(i)))])

    colStatesRed = sg.Column([[sg.Frame("Unit States",[[sg.Column([[sg.Frame("Flanked",colRFlanked,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("In Shock",colRinShock,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("Has Moved",colRhasMoved,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("in Forest",colRinForest,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("within Range",colRinRange,size=(100,400))]])
                                                    ]],size=(600,400))]])

    colInvolvedRed = sg.Column([[sg.Frame("Involved in Combat",colRInvolved,size=(150,400))]],size=(150,450))
    Layout = [colStatesBlue,colUnitsBlue,colInvolvedBlue,colInvolvedRed,colUnitsRed,colStatesRed]
    return Layout
    
def createUnitTranslator(game):
    Translator = {}
    for u in game.unitsBlue:
        Translator[u.name] = u
    for u in game.unitsRed:
        Translator[u.name] = u
    return Translator
        
        
def runEditWindow(unit):
    Layout = [[sg.Text(unit.name)],[sg.Text(sizeDict[unit.size])],[sg.Text(expDict[unit.experience])],
                [sg.Text("Manpower: "),sg.Spin([i for i in range(11)], initial_value=unit.manpower, size=3, key='-spinManpower-')],
                [sg.Text("Condition: "),sg.Spin([i for i in range(7)], initial_value=unit.condition, size=3, key='-spinCondition-')],
                [sg.Button("Cancel"),sg.Button("Confirm Changes")]]
    editWindow = sg.Window("Edit Unit",Layout)
    while True:
        event, values = editWindow.read()
        if event == sg.WIN_CLOSED or event == "Cancel":
            break
        if event == 'Confirm Changes':
            unit.manpower = values['-spinManpower-']
            unit.condition = values['-spinCondition-']
            break
    editWindow.close()

def updateStates(game,values):
    for u in game.unitsBlue:
        index = game.unitsBlue.index(u)
        u.isFlanked = values["isFlankedB" + str(index)]
        u.inShock = values["inShockB" + str(index)]
        u.hasMoved = values["hasMovedB" + str(index)]
        u.inForest = values["inForestB" + str(index)]
        u.inRange = values["inRangeB" + str(index)]
    for u in game.unitsRed:
        index = game.unitsRed.index(u)
        u.isFlanked = values["isFlankedR" + str(index)]
        u.inShock = values["inShockR" + str(index)]
        u.hasMoved = values["hasMovedR" + str(index)]
        u.inForest = values["inForestR" + str(index)]
        u.inRange = values["inRangeR" + str(index)]

def readGUI(game,values):
    involvedBlue = []
    for u in game.unitsBlue:
        index = game.unitsBlue.index(u)
        if values["involvedB" + str(index)] == True:
            involvedBlue.append(index)
    involvedRed = []
    for u in game.unitsRed:
        index = game.unitsRed.index(u)
        if values["involvedR" + str(index)] == True:
            involvedRed.append(index)
    return involvedBlue,involvedRed

#run
isSimpleGame = runStartUpWindow()

#unit creation
MainGame = SimpleGame(createSimpleUnits("Blue"),createSimpleUnits("Red"))
Translator = createUnitTranslator(MainGame)
mainLayout = [createMainGuiColumns(MainGame),
                [sg.Button("Quit"),sg.Button("Resolve Combat")]]

mainWindow = sg.Window("KriegsspielCalculator",mainLayout)

#main Window loop

while True:
    event, mainValues = mainWindow.read()
    if event == sg.WIN_CLOSED or event == "Quit":
        break
    if event == '-ListBlue-' and len(mainValues['-ListBlue-']):
        runEditWindow(Translator[mainValues['-ListBlue-'][0]])
    if event == '-ListRed-' and len(mainValues['-ListRed-']):
        runEditWindow(Translator[mainValues['-ListRed-'][0]])
    if event == "Resolve Combat":
        updateStates(MainGame,mainValues)
        invB,invR = readGUI(MainGame,mainValues)
        MainGame.resolveCombat(invB,invR)

mainWindow.close()