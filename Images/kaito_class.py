from PyQt6 import QtWidgets,QtGui,uic, QtCore
import numpy as np
from conversions import *
import copy

anzahlen = np.array([7,3,2,2,3])
steine = ["Kat","Kab","Mon3","Mon2","Mon1"]

class Kaito:
    
    def __init__(self,graphical_surface=None):
        
        self.players = [None,None] # Enthält Objekt der digitalen Spieler [rot,schwarz]
        
        self.spielstand = {
            
            "anzahlen": np.stack((anzahlen,anzahlen)),
            "spielsteine": [],
            "spielzug_count": 0,
            "konto_R_S": [0,0],
            "cursor": -1,
            "game_finished_winner": (False,"Nobody")
        }
        self.move_history = [] # Always contains objects of (spielstand(spielzug_count),move after t=spielzug_count)
    
        self.view = graphical_surface

        for i,stone in enumerate(steine):
            for p in ("r","s"):
                players_stone = p + stone
                
                for j in range(anzahlen[i]):
                    
                    self.spielstand["spielsteine"].append(players_stone)
                    
        self.spielstand["spielsteine"].append("empt")
        self.spielstand["spielsteine"].append("empt")
        
        np.random.shuffle(self.spielstand["spielsteine"])
        
        self.spielstand["cursor"] = self.spielstand["spielsteine"].index("empt")
             
    def start_game(self):
        
        if self.players[0]:
        
            self.players[0].your_turn()
    
    def all_legal_moves(self,spielstand=None):
        
        if not spielstand:
            #print("Used self.spielstand")
            
            spielstand = self.spielstand
        
        legalMoves = []
        
        for count in range(36):
            
            if self.is_move_legal(spielstand,count):
                
                legalMoves.append(count) #,position_from_count(count)))
                
        return legalMoves # list of all possible moves with respective (count,(spalte,reihe))
        
    def is_move_legal(self,spielstand,move_count):
        
        moveSpalte,moveReihe = position_from_count(move_count)
        cursorSpalte,cursorReihe = position_from_count(spielstand["cursor"])
        
        typ = spielstand["spielsteine"][move_count][1:]
        
        return ((moveSpalte == cursorSpalte) != (moveReihe == cursorReihe)) and not typ == "mpt"
                  
    def whooseTurn(self):
        
        r_s_binary = self.spielstand["spielzug_count"] % 2
        
        if r_s_binary == 0:
        
            return (0,"r")
        
        return (1,"s")
 
    def put(self,type):
    
        player = self.whooseTurn()
        
        self.spielstand["spielsteine"][self.spielstand["cursor"]] = player[1] + type
        
        if type == "Kab":
            
            kosten = 5
            
        if type == "Kat":
            
            kosten = 4
        
        self.spielstand["konto_R_S"][self.spielstand["spielzug_count"] % 2] -= kosten
        self.spielstand["anzahlen"][player[0],steine.index(type)] +=1 
        
        if self.view:
            
            self.view.draw()

    def s_r_to_binary(self,input):
        
        if input == "s":
            return 1
        
        if input == "r":
            return 0
        
        else: return 10000
    
    def name_from_count(self,count):
        
        spalte,reihe = position_from_count(count)
        return "feld"+str(spalte)+"_"+str(reihe)
    
    def updatePosition(self,suggested_move_count):
        
        if self.is_move_legal(self.spielstand,suggested_move_count):
            self.move_history.append([copy.deepcopy(self.spielstand),suggested_move_count])
    
        # entfernterStein = self.spielstand["spielsteine"][suggested_move_count]
        # besitzer,typ = entfernterStein[0],entfernterStein[1:] # Schneidet das e von empty ab
        
        #print(self.spielstand)
        projected_spielstand = self.project_move(self.spielstand,suggested_move_count)
        
        if not projected_spielstand:
            
            return
        
        else: self.spielstand = projected_spielstand
        
        #print("Spielzug_count",self.spielstand["spielzug_count"])
    
        spieler_am_zug = self.players[self.whooseTurn()[0]]
        
        self.whoLost()
    
        if self.view:
            
            self.view.draw()
        
        if spieler_am_zug and not self.spielstand["game_finished_winner"][0]:
            
            spieler_am_zug.your_turn()
    
        
    
    def countMon(self,besitzer,typ,spielstand=None):
        
        if not spielstand:
        
            spielstand = self.spielstand
            
        new_Konto_R_S = spielstand["konto_R_S"].copy()
        
        if self.whooseTurn()[1] == besitzer and typ[:3] == "Mon":
            
            anzahl = int(typ[3])
            
            new_Konto_R_S[self.whooseTurn()[0]] += anzahl
        
        return new_Konto_R_S
        
    def whoLost(self,spielstand = None):
        
        if spielstand == None:
            
            spielstand = self.spielstand
        
        def somebodyLost(vector):
            
           # if  vector[0] <= 0:
                
                #print("All Katanas were lost.")
                
            #if  vector[1] <= 0:
                
                #print("All Kabutos were lost.")
            
            return vector[0] <= 0 or vector[1] <= 0
        
        if somebodyLost(self.spielstand["anzahlen"][0]):
            
            self.spielstand["game_finished_winner"] = (True,"s")
            print("Schwarz hat gewonnen.")
            
        if somebodyLost(self.spielstand["anzahlen"][1]):
            
            self.spielstand["game_finished_winner"] = (True,"r")
            print("Rot hat gewonnen.")

        if len(self.all_legal_moves()) == 0:
            
            winner_bin = (self.whooseTurn()[0] + 1) % 2
            
            winner = "r" if winner_bin == 0 else "s"
            
            self.spielstand["game_finished_winner"] = (True,winner)
            
            print("Game was finished by no available move.")

    def project_move(self,spielstand,suggested_move):
        
        # Ziehe Zug, Berechne neue Matrix
        
        entfernterStein = spielstand["spielsteine"][suggested_move]
        besitzer,typ = entfernterStein[0],entfernterStein[1:] # Schneidet das e von empty ab
        
        if not self.is_move_legal(spielstand,suggested_move):
            
            print("Suggested move to play was illegal!")
            
            return False # Gibt Falsch aus, anstatt des Spielstand-Objektes, sofern der Zug widerrechtlich war

        spielstand["konto_R_S"] = self.countMon(besitzer,typ,spielstand)
        
        if not typ == "mpt":
        
            spielstand["anzahlen"][self.s_r_to_binary(besitzer),steine.index(typ)] -= 1

        spielstand["spielsteine"][suggested_move] = "empt"
        spielstand["cursor"] = suggested_move
        
        spielstand["spielzug_count"] += 1
            
        return spielstand

    def matrix_from_spielstand(self,spielstand = None, player = 0):
        
        if not spielstand:
            
            spielstand = self.spielstand
        
        matrix = np.concatenate((spielstand["anzahlen"],np.expand_dims(spielstand["konto_R_S"],axis=1)),axis=1)
        
        if player != 0:
            
            matrix = np.stack((matrix[1],matrix[0]),axis=0)
            
        return matrix

class Kaito_App(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(Kaito_App,self).__init__()
        uic.loadUi("./Spielfeld.ui",self)
        
        self.show()
        
        self.kaitoGame = Kaito(graphical_surface=self)
        
        
        self.newKabuto.clicked.connect(lambda : self.kaitoGame.put("Kab"))
        self.newKatana.clicked.connect(lambda : self.kaitoGame.put("Kat"))
        
       
                
        for count in range(36):
                        
            variableName = self.kaitoGame.name_from_count(count)
                
            exec("self.%s.setText('')" % (variableName,))
            exec("self.%s.setIconSize(QtCore.QSize(76,76))" % (variableName,))
            
            def updatePositionFunction(this_count):
                self.kaitoGame.updatePosition(this_count)
                self.draw()
                
            exec("self.%s.clicked.connect(lambda: updatePositionFunction(count))" % (variableName),{"count":count,"self":self,"updatePositionFunction":updatePositionFunction})
            
            count += 1     

        self.rMonCount.setStyleSheet(" color: red")
        self.rMonCountLabel.setStyleSheet(" color: red")
        
        self.draw()

    
    def draw(self):
        
        cursorPosition = position_from_count(self.kaitoGame.spielstand["cursor"])
        
        self.rMonCount.setText(str(self.kaitoGame.spielstand["konto_R_S"][0]))
        self.sMonCount.setText(str(self.kaitoGame.spielstand["konto_R_S"][1]))
        
        kontostand = self.kaitoGame.spielstand["konto_R_S"][self.kaitoGame.whooseTurn()[0]]
        
        if kontostand >= 4: self.newKatana.setEnabled(True)
        else: self.newKatana.setEnabled(False)
            
        if kontostand >= 5: self.newKabuto.setEnabled(True)
        else: self.newKabuto.setEnabled(False)
        
        if self.kaitoGame.spielstand["game_finished_winner"][0]:
            
            print("Game is finished.")
            
            if self.kaitoGame.spielstand["game_finished_winner"][1] == "r":
                
                self.endingMessage.setText("Rot hat gewonnen!")
                
            elif self.kaitoGame.spielstand["game_finished_winner"][1] == "s":
                
                self.endingMessage.setText("Schwarz hat gewonnen!")
                
            else: self.endingMessage.setText("Fehler!")
            

        for count in range(36):

            spalte,reihe = position_from_count(count)

            variableName = "feld"+str(spalte)+"_"+str(reihe)
            
            exec("self.%s.setIcon(QtGui.QIcon('./Icons/%s.jpg'))" % (variableName,self.kaitoGame.spielstand["spielsteine"][count]))

            if self.kaitoGame.whooseTurn()[1] == "r":
                
                color = "red"
            else:
                color = "darkgray"
                
            if ((cursorPosition[0] == spalte) ^ (cursorPosition[1] == reihe)) and not self.kaitoGame.spielstand["spielsteine"][count] == "empt":
                
                exec("self.%s.setStyleSheet(':active{background-color: %s} :hover {  background-color: white}')" % (variableName,color))                
                
            else:
                
                exec("self.%s.setStyleSheet(' background-color: rgb(240,240,240)')" % (variableName))  

            if self.kaitoGame.spielstand["spielsteine"][count] == "empt":
                
                exec("self.%s.hide()" % (variableName,))
                
            else: exec("self.%s.show()" % (variableName,))
            
            if self.kaitoGame.spielstand["game_finished_winner"][0]:
                
                exec("self.%s.hide()" % (variableName,))
                 
            count+=1
    