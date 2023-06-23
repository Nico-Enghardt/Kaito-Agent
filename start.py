
import sys, math, random, time, copy
from kaito_class import Kaito, Kaito_App
from PyQt6 import QtWidgets
import tensorflow as tf
import numpy as np

from conversions import *

estimator = tf.keras.models.Sequential(layers=[
        tf.keras.layers.Flatten(input_shape=[3,6]),
        tf.keras.layers.Dense(5,activation="sigmoid"),
        tf.keras.layers.Dense(1,activation="sigmoid")
    ])

estimator.build(input_shape=[None,3,6])
estimator.compile(optimizer="sgd",loss="mse")

estimator.summary()

def matrix_2_to_3(eigene_fremde_steine):
    
    # Eingegeben in das Neuronale Netzwerk werden (nach Zeilen): Zahl Katanas, Kabutos, 1 Mon, 2 Mon, 3 Mon, Mon-Kontostand
    # Diese Werte werden nach Spalten eingebenen: eigene Steine, gegnerische Steine, eigene - fremde Steine
    
    differenz = eigene_fremde_steine[1] - eigene_fremde_steine[0]
    
    return np.concatenate((eigene_fremde_steine,np.expand_dims(differenz,axis=0)),axis=0)

def evalNN(eigene_fremde_steine):
    
    input = matrix_2_to_3(eigene_fremde_steine)
    
    evaluation = estimator(np.expand_dims(input,axis=0))
    
    return evaluation.numpy()[0,0]

class Random_Player():
    
    def __init__(self,game,which_player_str="rot",):
        
        self.kaitoGame = game
        self.which_player = self.kaitoGame.s_r_to_binary(which_player_str[0]),which_player_str[0]
        self.kaitoGame.players[self.which_player[0]] = self
    
    def play_randomMove(self):
        
        possible_moves = self.kaitoGame.all_legal_moves()
        
        move_count = random.choice(possible_moves)
        
        self.kaitoGame.updatePosition(move_count)
        
    def your_turn(self):
        
        # Function is called by self.kaitoGame
        
        self.play_randomMove()

class Computer_Player:
    
    def __init__(self,game,which_player_str="rot",):
        
        self.kaitoGame = game
        self.which_player = self.kaitoGame.s_r_to_binary(which_player_str[0]),which_player_str[0]
        self.kaitoGame.players[self.which_player[0]] = self
        
    def your_turn(self):
        
        # Function is called by self.kaitoGame
        
        self.calculate_best_move()

    def calculate_best_move(self,iterations=1):
        
        # Initialisiere Matrix
        
        move_to_play,evaluation = self.calculate_best_move_recursive(copy.deepcopy(self.kaitoGame.spielstand),iterations)
        
        #print("Evaluated my position as:", evaluation)
        
        self.kaitoGame.updatePosition(move_to_play)
        
        
    def calculate_best_move_recursive(self,spielstand,iterations=10,maximize=1):
        
        quality_of_this_move = []
        
        # wenn self.kaitoGame.all_legal_moves [] empty dann füge einen Sieg für den Gegner ein
        
        for next_move in self.kaitoGame.all_legal_moves(spielstand):
            
            ## move is in [0,36]
            
            ## Durchsuche alle möglichen Züge, die der Spieler hat
            
            #print("Move:",next_move,"   Iteration:",iterations)
            
            next_spielstand = self.kaitoGame.project_move(copy.deepcopy(spielstand),next_move)
                
            if iterations > 0:
                
                # Verwende als Evaluation nur Max oder Min der Evaluations aller nachfolgenden Züge
                
                best_next_move, next_move_evaluation = self.calculate_best_move_recursive(next_spielstand,iterations - 1,maximize + 1)
                
                quality_of_this_move.append(next_move_evaluation)
            
            else: 
                
                evaluation = evalNN(self.kaitoGame.matrix_from_spielstand(next_spielstand,self.which_player[0]))
                
                quality_of_this_move.append(evaluation)
            
                
        # If quality_of_opponent_move [] empty dann füge einen Sicheren Sieg  ein

        if len(quality_of_this_move) == 0:
            
            return -1,-100
        else: 
        
            min_or_max = np.max if maximize % 2 == 1 else np.min
            # if (maximize % 2) == 1:
                    
            #         print("Maximized")
            # else: print("Minimized")
            
            best_evaluation = min_or_max(quality_of_this_move)
        
        best_own_move = self.kaitoGame.all_legal_moves(spielstand)[quality_of_this_move.index(best_evaluation)]
        
        return best_own_move,best_evaluation
             
    def calculate_best_move_recursive_double(self,spielstand,iterations):

        quality_of_own_move = []
        
        # wenn self.kaitoGame.all_legal_moves [] empty dann füge einen Sieg für den Gegner ein
        
        for move_1 in self.kaitoGame.all_legal_moves(spielstand):
            
            ## move is in [0,36]
            
            ## Durchsuche alle möglichen Züge, die der Spieler hat
            
            #print("Legaler Zug?!:",self.kaitoGame.is_move_legal(spielstand,move_1))
            
            spielstand_1 = self.kaitoGame.project_move(spielstand.deepcopy(),move_1)
            
            eval_to_be_maximized = evalNN(self.kaitoGame.matrix_from_spielstand(spielstand_1,self.which_player[0]))
            
            quality_of_own_move.append(eval_to_be_maximized)
            
            quality_of_opponent_move = []
            
            for (k,move_2) in enumerate(self.kaitoGame.all_legal_moves(spielstand_1)):
                
                ## Durchsuche alle möglichen Züge seines Gegners
                
                spielstand_2 = self.kaitoGame.project_move(spielstand_1.deepcopy(),move_2)
                
                if iterations > 0:
                    
                    best_move,eval_to_be_minimized = self.calculate_best_move_recursive(spielstand_2,iterations - 1)
                
                else: eval_to_be_minimized = evalNN(self.kaitoGame.matrix_from_spielstand(spielstand_2,self.which_player[0]))
                
                quality_of_opponent_move.append(eval_to_be_minimized)
                
            # If quality_of_opponent_move [] empty dann füge einen Sicheren Sieg für den Spieler ein
                
            if len(quality_of_opponent_move) == 0:
                
                quality_of_opponent_move.append(100)
                
            else: 
                
                worst_opponent_score = np.max(quality_of_opponent_move)
                
                quality_of_own_move.append(worst_opponent_score)
            
                best_opponent_move = quality_of_opponent_move.index(worst_opponent_score)
                
            ## Zug mit minimaler Bewertung finden
        
        if len(quality_of_own_move) == 0:
            
            return -1,-100
        
        evaluation = np.max(quality_of_own_move)
        best_own_move = quality_of_own_move.index(evaluation)
        
        return best_own_move,evaluation
        
def playGames(number,mode="train"):
    
    games = []
    
    training_data = []
    training_labels = []
    
    for i in range(number):
        
        game = Kaito()
            
        games.append(game)
        
        randomPlayer1 = Computer_Player(game,"schwarz")
        
        if mode == "evaluate":
        
            randomPlayer0 = Random_Player(game,"rot")
            
        else: randomPlayer0 = Computer_Player(game,"rot")
            
        game.start_game()
        
    siege_rot_schwarz = [0,0]
    
    for game in games:
        
        if game.spielstand["game_finished_winner"][1] == "r":
            
            siege_rot_schwarz[0] += 1
    
        if game.spielstand["game_finished_winner"][1] == "s":
            
            siege_rot_schwarz[1] += 1
        
        victory_for_AI = game.spielstand["game_finished_winner"][1] == "s"

        for spiel_zug in game.move_history:
        
            spielstand = spiel_zug[0]
            next_move  = spiel_zug[1]
            
            evaluation_should_be = spielstand["spielzug_count"] /game.spielstand["spielzug_count"] * 100
            
            matrix = game.matrix_from_spielstand(spielstand,player=1)
            matrix = matrix_2_to_3(matrix)
            
            if not victory_for_AI:
                
                evaluation_should_be *= -1
                
            training_data.append(matrix)
            training_labels.append(evaluation_should_be)
    
    training_data,training_labels = np.array(training_data), np.array(training_labels)
    
    print("siege_rot_schwarz",siege_rot_schwarz)

    return siege_rot_schwarz,training_data,training_labels

if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    surface = Kaito_App()
    randomPlayer1 = Computer_Player(surface.kaitoGame,"schwarz")
    
    for i in range(10):
    
        siege_rot_schwarz,training_data,training_labels = playGames(30)
        
        estimator.fit(training_data,training_labels)
        
        siege_rot_schwarz,training_data,training_labels = playGames(10,mode="evaluate")
        
    app.exec()