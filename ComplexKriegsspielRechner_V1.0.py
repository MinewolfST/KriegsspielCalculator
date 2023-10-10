import numpy as np
import random
import PySimpleGUI as sg

sg.theme("DarkAmber")

#Word Stuff
sizeDict = {1:"Squad", 2:"Platoon", 4:"Vehicle Platoon", 6:"Heavy Weapons/Tank Platoon"}
expDict = {0:"Green",1:"Unexperienced",2:"Trained",3:"Elite"}
sizeDictBack = {"Squad":1, "Platoon":2, "Vehicle Platoon":4, "Heavy Weapons/Tank Platoon":6}
expDictBack = {"Green":0,"Unexperienced":1,"Trained":2,"Elite":3}
exps = ["Green","Unexperienced","Trained","Elite"]
sizes = ["Squad","Platoon","Vehicle Platoon","Heavy Weapons/Tank Platoon"]

#Calculations
class Unit:
    def __init__(self,name,size,experience,manpower,condition,armour,penetration,isVehicle,hasMG):
        self.name = name
        self.size = size
        self.experience = experience
        self.manpower = manpower
        self.condition = condition
        self.armour = armour
        self.penetration = penetration
        self.states = {"isFlanked":False,"inShock":False,"hasMoved":False,"inForest":False,"inRange":False,"isVehicle":isVehicle,"hasMG":hasMG}
        print("Unit created: " + self.name + " with attributes: " + sizeDict[self.size] + " " + expDict[self.experience] + " " + str(self.manpower) + " " + str(self.condition) + " " + str(self.armour) + " " + str(self.penetration))
        
    def __str__(self):
        return self.name
    
    def basicCombatPower(self):
        modifiers = 0
        if self.states["inShock"]:
            modifiers -= 20
        if self.states["hasMoved"]:
            modifiers -= 2
        if self.states["inRange"]:
            modifiers += 2
        else:
            modifiers -= 5
        combatPower = (self.manpower * self.size) + self.condition + self.experience + modifiers
        if combatPower < 0:
            return 0
        else:
            return combatPower
        
    def probabilityOfGettingHit(self,enemyUnits):
        probability = (self.manpower * self.size) + self.condition + self.experience
        if self.states["isFlanked"]:
            probability *= 2
        if self.states["inForest"]:
            probability *= 0.5
        if not self.states["inRange"]:
            probability *= 0.1
        if self.states["hasMoved"]:
            probability *= 0.8
        if self.states["inShock"]:
            probability *= 2
        penetrationToggle = False
        for u in enemyUnits:
            if u.penetration > self.armour:
                probability *= 1.2
            if u.penetration < self.armour:
                penetrationToggle = True
        if penetrationToggle:
            probability = 1
        return int(probability)
        
class Volley:
    def __init__(self,unitsFiring,unitsTargeted):
        self.unitsFiring = unitsFiring
        self.unitsTargeted = unitsTargeted
        self.combatReport = []
        
    def evaluatePenetration(self):
        combatPowerChange = 0
        for u in self.unitsFiring:
            for t in self.unitsTargeted:
                if t.states["isVehicle"]:
                    if u.penetration > (t.armour*2):
                        combatPowerChange += ((u.penetration - t.armour) * u.manpower)
                        print("             Penetrated!")
                    if u.penetration < t.armour:
                        combatPowerChange -= (abs((u.penetration - t.armour) * u.manpower))
                        print("             not penetrated!")
        print("            Combat Power change due to penetration and Armour: " + str(combatPowerChange))
        return combatPowerChange
    
    def evaluateTanks(self):
        combatPowerChange = 0
        tankTrigger = False
        MGTrigger = False
        for t in self.unitsTargeted:
            if not t.states["isVehicle"]:
                MGTrigger = True
            if t.states["isVehicle"]:
                tankTrigger = True
        for u in self.unitsFiring:
            if MGTrigger and u.states["hasMG"]:
                combatPowerChange += 5
        if tankTrigger:
            combatPowerChange -= 20
        return combatPowerChange
    
    def determineDamage(self):
        Rolls = [0,1,1,2,2,2,3,3,3,3,4,4,4,4,4,5,5,5,5,5,5,6,6,6,6,6,7,7,7,7,8,8,8,9,9,10]
        damageList = [33,30,27,24,21,18,15,12,9,6,3]
        diceRoll = random.choice(Rolls)
        print("Dice Roll: " + str(diceRoll))
        damage = np.floor(self.combatPower / damageList[diceRoll])
        if damage > 5:
            return 5
        if damage < 1:
            return 0
        else:
            return damage
    
    def createCombatReportColumn(self):
        column = []
        for r in self.combatReport:
            column.append([sg.Text("Unit " + self.unitsTargeted[self.combatReport.index(r)].name + " suffers " + str(r[0]) + " damage and looses " + str(r[1]) + " condition")])
        if len(self.combatReport) == 0:
            column.append([sg.Text("No Units damaged")])
        return sg.Column(column)
    
    def applyDamage(self):
        damageRegister = [0 for u in self.unitsTargeted]
        hitProbabilities = []
        for u in self.unitsTargeted:
            for i in range(max(u.probabilityOfGettingHit(self.unitsFiring),1)):
                hitProbabilities.append(self.unitsTargeted.index(u))
        while self.damageDealt > 0:
            damageRegister[random.choice(hitProbabilities)] += 1
            self.damageDealt -= 1
        for d in damageRegister:
            if d > 0:
                self.unitsTargeted[damageRegister.index(d)].manpower -= d
                if d >= 5:
                    conditionChange = 3
                if d == 3 or d ==4 :
                    conditionChange = 2
                if d == 1 or d == 2:
                    conditionChange = 1
                self.unitsTargeted[damageRegister.index(d)].condition -= conditionChange
                print("            Unit: " + self.unitsTargeted[damageRegister.index(d)].name + " suffers " + str(d) + " damage and looses " + str(conditionChange) + " condition.")
                self.combatReport.append([d,conditionChange])
            else:
                print("            Unit: " + self.unitsTargeted[damageRegister.index(d)].name + " suffers no damage.")
                self.combatReport.append([0,0])
                
    def resolve(self,holdDamage):
        self.combatPower = 0
        for u in self.unitsFiring:
            self.combatPower += u.basicCombatPower()
        self.combatPower += self.evaluatePenetration()
        self.combatPower += self.evaluateTanks()
        print("        Total Combat Power: " + str(self.combatPower))
        self.damageDealt = self.determineDamage()
        if not holdDamage:
            self.applyDamage()

class Combat:
    def __init__(self,game,ambush,isVolley=False):
        self.game = game
        self.ambush = ambush
        self.isVolley = isVolley
    
    def updateStates(self,values):
        for u in self.game.unitsBlue:
            index = self.game.unitsBlue.index(u)
            u.states["isFlanked"] = values["isFlankedB" + str(index)]
            u.states["inShock"] = values["inShockB" + str(index)]
            u.states["hasMoved"] = values["hasMovedB" + str(index)]
            u.states["inForest"] = values["inForestB" + str(index)]
            u.states["inRange"] = values["inRangeB" + str(index)]
        for u in self.game.unitsRed:
            index = self.game.unitsRed.index(u)
            u.states["isFlanked"] = values["isFlankedR" + str(index)]
            u.states["inShock"] = values["inShockR" + str(index)]
            u.states["hasMoved"] = values["hasMovedR" + str(index)]
            u.states["inForest"] = values["inForestR" + str(index)]
            u.states["inRange"] = values["inRangeR" + str(index)]
        
    def readGUI(self,values):
        involvedBlue = []
        for u in self.game.unitsBlue:
            index = self.game.unitsBlue.index(u)
            if values["involvedB" + str(index)] == True:
                involvedBlue.append(u)
        involvedRed = []
        for u in self.game.unitsRed:
            index = self.game.unitsRed.index(u)
            if values["involvedR" + str(index)] == True:
                involvedRed.append(u)
        return involvedBlue,involvedRed
    
    def runCombatReportWindow(self,columnBlue,columnRed):
        for u in self.game.unitsBlue:
            if u.manpower < 1:
                sg.Popup("KIA","Killed in action: " + u.name)
                self.game.unitsBlue.pop(self.game.unitsBlue.index(u))
        for u in self.game.unitsRed:
            if u.manpower < 1:
                sg.Popup("KIA","Killed in action: " + u.name)
                self.game.unitsRed.pop(self.game.unitsRed.index(u))
        CRlayout = [[sg.T("Combat Results:")],[columnRed,columnBlue],[sg.Button("Close")]]
        CRevent,CRvalues = sg.Window("Combat Report",CRlayout).read(close=True)
        
    def fight(self,values):
        self.updateStates(values)
        fightingUnitsBlue, fightingUnitsRed = self.readGUI(values)
        if (len(fightingUnitsBlue) == 0 or len(fightingUnitsRed) == 0):
            sg.popup("No enemy units selected")
        else:
            volleyBlue = Volley(fightingUnitsBlue,fightingUnitsRed)
            volleyRed = Volley(fightingUnitsRed,fightingUnitsBlue)
            if self.ambush == "none":
                volleyBlue.resolve(True)
                volleyRed.resolve(True)
                volleyBlue.applyDamage()
                volleyRed.applyDamage()
            if self.ambush == "blue":
                volleyBlue.resolve(False)
                if not self.isVolley:
                    volleyRed.resolve(False)
            if self.ambush == "red":
                volleyRed.resolve(False)
                if not self.isVolley:
                    volleyBlue.resolve(False)
            self.runCombatReportWindow(volleyBlue.createCombatReportColumn(),volleyRed.createCombatReportColumn())
class Game:
    def __init__(self,unitsBlue,unitsRed):
        self.unitsBlue = unitsBlue
        self.unitsRed = unitsRed

#GUI
def runStartUpWindow():
    startupWindowLayout = [
                    [sg.Text("Start a new Game?")],
                    [sg.Button("Start"),sg.Button("Quit")]]
    startupWindow = sg.Window("KriegsspielCalculator Start",startupWindowLayout)

    while True:
        event, values = startupWindow.read()
        if event == sg.WIN_CLOSED or event == "Quit":
            break
        elif event == "Start":
            startNewGame = True
            startupWindow.close()
    return(startNewGame)

def createUnits(colour):
    quitToggle = False
    units = []
    
    while True:
        event, values = sg.Window('Unit Creator',
                        [[sg.T("Number of " + colour + " units:"), sg.In(key="-num-")],
                        [sg.B('OK'),sg.B("Quit")]]).read(close=True)
        if event == sg.WIN_CLOSED or event == "Quit":
            quitToggle = True
            break
        if (str(values["-num-"]).isnumeric()):
            break
        else:
            sg.popup("Input Error","Not a valid input")
    if not quitToggle:
        for i in range(int(values["-num-"])):
            namesColumn = sg.Column([[sg.T("Name:")],[sg.T("Size:")],[sg.T("Manpower:")],[sg.T("Condition:")],[sg.T("Armour:")],[sg.T("Penetration:")],[sg.T("Experience:")],[sg.T("Vehicle: ")]])
            inputColumn = sg.Column([[sg.In(key='-name-',default_text="Alpha")],
                            [sg.Combo(sizes, default_value="Platoon", s=(35,35), enable_events=False, readonly=True, k='-size-')],
                            [sg.Spin([i for i in range(11)], initial_value=10, size=3, key='-manpower-')],
                            [sg.Spin([i for i in range(7)], initial_value=6, size=3, key='-condition-')],
                            [sg.Spin([i for i in range(11)], initial_value=0, size=3, key='-armour-')],
                            [sg.Spin([i for i in range(11)], initial_value=0, size=3, key='-penetration-')],
                            [sg.Combo(exps, default_value="Trained", s=(15,22), enable_events=False, readonly=True, k='-experience-')],
                            [sg.Checkbox("",key="-isVehicle-"), sg.Checkbox("has MG: ",key="-hasMG-")]
                            ])
            event, values = sg.Window('Stats ' + str(i+1) + ". unit",
                        [[namesColumn,inputColumn],
                        [sg.B('OK')]]).read(close=True)
            units.append(Unit(values["-name-"],sizeDictBack[values["-size-"]],expDictBack[values["-experience-"]],int(values["-manpower-"]),int(values["-condition-"]),int(values["-armour-"]),int(values["-penetration-"]),values["-isVehicle-"],values["-hasMG-"]))
            print("Unit added successfully")
        return(units)


#constructing state columns, not nice but works
def createMainGuiColumns(Game):

    namesBlue = [i for i in Game.unitsBlue]    # "names" is wrong here but i just copied it over from the first version and am to lazy to change it
    namesRed = [i for i in Game.unitsRed]
    columnSize = max(len(namesBlue),len(namesRed)) * 50 + 20

    colUnitsBlue = sg.Column([[sg.Frame("Blue Units",[[sg.Listbox(namesBlue,enable_events=True,key="-ListBlue-",size=(15,20))]],size=(150,columnSize))]])
    colUnitsRed = sg.Column([[sg.Frame("Red Units",[[sg.Listbox(namesRed,enable_events=True,key="-ListRed-",size=(15,20))]],size=(150,columnSize))]])

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


    colStatesBlue = sg.Column([[sg.Frame("Unit States",[[sg.Column([[sg.Frame("Flanked",colBFlanked,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("In Shock",colBinShock,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("Has Moved",colBhasMoved,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("in Forest",colBinForest,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("within Range",colBinRange,size=(100,columnSize))]])
                                                    ]],size=(600,columnSize+20))]])

    colInvolvedBlue = sg.Column([[sg.Frame("Involved in Combat",colBInvolved,size=(150,columnSize))],[sg.Button("Blue Volley")],[sg.Button("Blue Ambush")]],size=(200,columnSize+100))

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

    colStatesRed = sg.Column([[sg.Frame("Unit States",[[sg.Column([[sg.Frame("Flanked",colRFlanked,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("In Shock",colRinShock,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("Has Moved",colRhasMoved,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("in Forest",colRinForest,size=(100,columnSize))]]),
                                                    sg.Column([[sg.Frame("within Range",colRinRange,size=(100,columnSize))]])
                                                    ]],size=(600,columnSize+20))]])

    colInvolvedRed = sg.Column([[sg.Frame("Involved in Combat",colRInvolved,size=(150,columnSize))],[sg.Button("Red Volley")],[sg.Button("Red Ambush")]],size=(200,columnSize+100))
    Layout = [colStatesBlue,colUnitsBlue,colInvolvedBlue,colInvolvedRed,colUnitsRed,colStatesRed]
    return Layout

def runEditWindow(unit):
    Layout = [[sg.Text(unit.name)],[sg.Text(sizeDict[unit.size])],[sg.Text(expDict[unit.experience])],
                [sg.Text("Manpower: "),sg.Spin([i for i in range(11)], initial_value=unit.manpower, size=3, key='-spinManpower-')],
                [sg.Text("Condition: "),sg.Spin([i for i in range(7)], initial_value=unit.condition, size=3, key='-spinCondition-')],
                [sg.Text("Armour: " + str(unit.armour))],
                [sg.Text("Penetration: " + str(unit.penetration))],
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


#run
startNew = runStartUpWindow()
if startNew:
    MainGame = Game(createUnits("Blue"),createUnits("Red"))
    quitTrigger = False
    combatLog = []
else:
    quitTrigger = True

while not quitTrigger:
    mainLayout = [createMainGuiColumns(MainGame),
                [sg.Button("Quit"),sg.Button("Resolve Equal Combat")]]
    mainWindow = sg.Window("KriegsspielCalculator",mainLayout)
    while True:
        event, mainValues = mainWindow.read()
        if event == sg.WIN_CLOSED or event == "Quit":
            quitTrigger = True
            break
        if event == '-ListBlue-' and len(mainValues['-ListBlue-']):
            runEditWindow(mainValues['-ListBlue-'][0])
        if event == '-ListRed-' and len(mainValues['-ListRed-']):
            runEditWindow(mainValues['-ListRed-'][0])
        if event == "Resolve Equal Combat":
            combatLog.append(Combat(MainGame,"none"))
            combatLog[-1].fight(mainValues)
            break
        if event == "Blue Ambush":
            combatLog.append(Combat(MainGame,"blue"))
            combatLog[-1].fight(mainValues)
            break
        if event == "Red Ambush":
            combatLog.append(Combat(MainGame,"red"))
            combatLog[-1].fight(mainValues)
            break
        if event == "Blue Volley":
            combatLog.append(Combat(MainGame,"blue",isVolley=True))
            combatLog[-1].fight(mainValues)
            break
        if event == "Red Volley":
            combatLog.append(Combat(MainGame,"red",isVolley=True))
            combatLog[-1].fight(mainValues)
            break
    mainWindow.close()        
