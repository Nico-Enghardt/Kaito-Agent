
import sys, os, math, random, time, copy
from kaito_class import Kaito, Kaito_App
from PyQt6 import QtWidgets
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

from conversions import *

estimator_path = 'Tensors/estimator.keras'

if os.path.isfile(estimator_path):
    
    estimator = tf.keras.models.load_model(estimator_path)
    print("Used pretrained estimator.")

else: 

    estimator = tf.keras.models.Sequential(layers=[
            tf.keras.layers.Flatten(input_shape=[3,6]),
            tf.keras.layers.Dense(5,activation="sigmoid"),
            tf.keras.layers.Dense(1,activation="linear")
        ])

    estimator.build(input_shape=[None,3,6])
    
    adam = tf.keras.optimizers.Adam(learning_rate=1)

    estimator.compile(optimizer=adam, loss="mse")

estimator.summary()

training_data = []
training_labels = []

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
        self.iterations = 2
        
    def your_turn(self):
        
        # Function is called by self.kaitoGame
        
        self.calculate_best_move()

    def calculate_best_move(self):

        self.total_iterations = 0
        
        move_to_play, evaluation = self.calculate_best_move_recursive(self.kaitoGame.spielstand, self.iterations)
        
        print(f"Total iterations needed for tree search: {self.total_iterations}")
        
        #print("Evaluated my position as:", evaluation)
        
        self.kaitoGame.updatePosition(move_to_play)
        
    def calculate_best_move_recursive(self,spielstand,iterations,maximize=1):
        
        self.total_iterations += 1
        
        quality_of_this_move = []
        
        # wenn self.kaitoGame.all_legal_moves [] empty dann füge einen Sieg für den Gegner ein
        
        min_or_max = np.max if maximize % 2 == 1 else np.min
        
        for next_move in self.kaitoGame.all_legal_moves(spielstand):
            
            ## move is in [0,36]
            
            ## Durchsuche alle möglichen Züge, die der Spieler hat
            
            if iterations > 1:
                print("Move:", next_move,"   Iteration:", iterations, "Spielzug Nr.", spielstand["spielzug_count"])
            
            next_spielstand = self.kaitoGame.project_move(copy.deepcopy(spielstand), next_move)
                
            if iterations > 0:
                
                # Verwende als Evaluation nur Max oder Min der Evaluations aller nachfolgenden Züge
                
                best_next_move, next_move_evaluation = self.calculate_best_move_recursive(copy.deepcopy(next_spielstand), iterations - 1,maximize + 1)               
                    
                
                
                quality_of_this_move.append(next_move_evaluation)
            
            else:
                
                evaluation = evalNN(self.kaitoGame.matrix_from_spielstand(next_spielstand,self.which_player[0]))
                
                quality_of_this_move.append(evaluation)
            
        # If quality_of_opponent_move [] empty dann füge einen Sicheren Sieg  ein

        if len(quality_of_this_move) == 0:
            
            return -1,-100
        else: 
            
            best_evaluation = min_or_max(quality_of_this_move)
        
        best_own_move = self.kaitoGame.all_legal_moves(spielstand)[quality_of_this_move.index(best_evaluation)]
        
        return best_own_move,best_evaluation
             
        
def playGames(number,mode="train",verbose=0):
    
    games = []
    
    for i in range(number):
        
        game = Kaito()
            
        games.append(game)
        
        player1 = Computer_Player(game,"schwarz")
        
        if mode == "evaluate":
        
            player0 = Random_Player(game,"rot")
            
        else: player0 = Computer_Player(game,"rot")
        
        if mode == "random":
            
            player0 = Random_Player(game,"rot")
            player1 = Random_Player(game,"schwarz")
            
        if verbose == 1:
            print(f"Started Game Nr. {i}")
        game.start_game()
        
    siege_rot_schwarz = [0,0]
    
    for game in games:
        
        if game.spielstand["game_finished_winner"][1] == "r":
            
            siege_rot_schwarz[0] += 1
    
        if game.spielstand["game_finished_winner"][1] == "s":
            
            siege_rot_schwarz[1] += 1
        
        victory_for_AI = game.spielstand["game_finished_winner"][1] == "s"

        game.move_history.pop(0)

        for spiel_zug in game.move_history:
        
            spielstand = spiel_zug[0]
            next_move  = spiel_zug[1]
            
            evaluation_should_be = spielstand["spielzug_count"] / game.spielstand["spielzug_count"] * 100
            
            matrix = game.matrix_from_spielstand(spielstand,player=1)
            matrix = matrix_2_to_3(matrix)
            
            if not victory_for_AI:
                
                evaluation_should_be *= -1
                
            training_data.append(matrix)
            training_labels.append(evaluation_should_be) 
    
    if verbose == 1:
        print("siege_rot_schwarz",siege_rot_schwarz)

    return siege_rot_schwarz

if __name__ == "__main__":
    
    loss_history = []
    
    for i in range(4):
    
        print(f"Play {i*2+1} training games ComputerPlayer vs. ComputerPlayer")
        siege_rot_schwarz = playGames(100, mode="random",verbose=1)
        
        print(len(training_data), len(training_labels))
        loss_history += estimator.fit(np.array(training_data), np.array(training_labels), epochs=30, verbose=1).history["loss"]
        estimator.save(estimator_path)
        
    print(f"Play {i+1} evaluation games ComputerPlayer vs. RandomPlayer")   
    siege_rot_schwarz = playGames(i+1,mode="evaluate")
    
    app = QtWidgets.QApplication(sys.argv)
    surface = Kaito_App()
    randomPlayer1 = Computer_Player(surface.kaitoGame,"schwarz")
    randomPlayer1.iterations = 5
    
    plt.plot(loss_history)
    plt.show()
        
    app.exec()