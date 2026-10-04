
import sys, math, random, time, copy
from kaito_class import Kaito, Kaito_App
from PyQt6 import QtWidgets
import numpy as np
import matplotlib.pyplot as plt

from conversions import *
# from computer_player import * 

training_data = []
training_labels = []

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
    
    i = 0
    
    # for i in range(0):
    
    #     print(f"Play {i*2+1} training games ComputerPlayer vs. ComputerPlayer")
    #     siege_rot_schwarz = playGames(5, mode="train",verbose=1)
        
    #     print(len(training_data), len(training_labels))
    #     loss_history += estimator.fit(np.array(training_data), np.array(training_labels), epochs=4, verbose=1).history["loss"]
    #     estimator.save(estimator_path)
        
    # print(f"Play {i+1} evaluation games ComputerPlayer vs. RandomPlayer")   
    # siege_rot_schwarz = playGames(i+1,mode="evaluate")
    # print(siege_rot_schwarz)
    
    app = QtWidgets.QApplication(sys.argv)
    kaito_app = Kaito_App()
    # randomPlayer1 = FastComputerPlayer(kaito_app.kaitoGame,"schwarz")
        
    app.exec()