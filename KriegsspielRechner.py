import numpy as np
import random
import PySimpleGUI as sg

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

def determineDamage(combatPower):
    allowedRolls = [0,1,2,3,4,5,6,7,8,9,10]
    damageList = [33,30,27,24,21,18,15,12,9,6,3]
    diceRoll = random.choice(allowedRolls)
    return(np.floor(combatPower / damageList[diceRoll]))
    

class SimpleUnit:          #most infantry
    def __init__(self,name,size,manpower,condition,experience):
        self.name = name
        self.size = size
        self.manpower = manpower
        self.condition = condition
        self.experience = experience
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
        
        return((self.manpower * self.size) + self.condition + self.experience + modifiers)
    
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
    def __init__(self,unitsBlue,unitsRed):
        self.unitsBlue = unitsBlue
        self.unitsRed = unitsRed
        
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
            
        
        damageBlue = determineDamage(combatPowerBlue)
        damageRed = determineDamage(combatPowerRed)
        
        while(damageBlue > 0):
            unitHit = random.choice(involvedRed)
            self.unitsRed[unitHit].manpower = self.unitsRed[unitHit].manpower -1
            damageBlue = damageBlue -1
            print("Red Unit " + str(self.unitsRed[unitHit].name) + " Suffers 1 damage")
        
        while(damageRed > 0):
            unitHit = random.choice(involvedBlue)
            self.unitsBlue[unitHit].manpower = self.unitsBlue[unitHit].manpower -1
            damageRed = damageRed -1
            print("Blue Unit " + str(self.unitsBlue[unitHit].name) + " Suffers 1 damage")

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
sg.theme("DarkAmber")

#initial start window
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
        sg.popup("Not supportet yet")
        
#unit creation
MainGame = SimpleGame(createSimpleUnits("Blue"),createSimpleUnits("Red"))


#main gui

namesBlue = [i.name for i in MainGame.unitsBlue]
namesRed = [i.name for i in MainGame.unitsRed]

colBlue = sg.Column([[sg.Frame("Blue Units",[[sg.Listbox(namesBlue,enable_events=True,key="-ListBlue-",size=(15,20))]],size=(150,400))]])
colRed = sg.Column([[sg.Frame("Red Units",[[sg.Listbox(namesRed,enable_events=True,key="-ListRed-",size=(15,20))]],size=(150,400))]])


#constructing state columns, not nice but works
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


colStatesBlue = sg.Column([[sg.Frame("Unit States",[[sg.Column([[sg.Frame("Flanked",colBFlanked,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("In Shock",colBinShock,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("Has Moved",colBhasMoved,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("in Forest",colBinForest,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("within Range",colBinRange,size=(100,400))]])
                                                    ]],size=(600,400))]])

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


colStatesRed = sg.Column([[sg.Frame("Unit States",[[sg.Column([[sg.Frame("Flanked",colRFlanked,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("In Shock",colRinShock,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("Has Moved",colRhasMoved,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("in Forest",colRinForest,size=(100,400))]]),
                                                    sg.Column([[sg.Frame("within Range",colRinRange,size=(100,400))]])
                                                    ]],size=(600,400))]])


#main Window
mainLayout = [[colStatesBlue,colBlue,colRed,colStatesRed],
              [sg.Button("Quit")]]
mainWindow = sg.Window("KriegsspielCalculator",mainLayout)

while True:
    event, values = mainWindow.read()
    if event == sg.WIN_CLOSED or event == "Quit":
        break
    if event == '-ListBlue-' and len(values['-ListBlue-']):
        #selectedUnit = ????
        #sg.popup('Selected ', selectedUnit.name)
        sg.popup("Selected","Something")

mainWindow.close()