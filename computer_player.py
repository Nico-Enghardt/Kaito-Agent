import os
import tensorflow as tf
import copy
import numpy as np

estimator_path = 'Tensors/estimator.keras'

if os.path.isfile(estimator_path):
    
    estimator = tf.keras.models.load_model(estimator_path)
    print("Used pretrained estimator.")

else: 

    estimator = tf.keras.models.Sequential(layers=[
            tf.keras.layers.Flatten(input_shape=[3,6]),
            #tf.keras.layers.Dense(5,activation="sigmoid"),
            tf.keras.layers.Dense(1,activation="linear")
        ])

    estimator.build(input_shape=[None,3,6])
    
    adam = tf.keras.optimizers.Adam(learning_rate=0.01)

    estimator.compile(optimizer=adam, loss="mse")
    
    print("Created new estimator weights.")


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

def matrix_2_to_3(eigene_fremde_steine):
    
    # Eingegeben in das Neuronale Netzwerk werden (nach Zeilen): Zahl Katanas, Kabutos, 1 Mon, 2 Mon, 3 Mon, Mon-Kontostand
    # Diese Werte werden nach Spalten eingebenen: eigene Steine, gegnerische Steine, eigene - fremde Steine
    
    differenz = eigene_fremde_steine[1] - eigene_fremde_steine[0]
    
    return np.concatenate((eigene_fremde_steine,np.expand_dims(differenz,axis=0)),axis=0)

def evalNN(eigene_fremde_steine):
    
    input = matrix_2_to_3(eigene_fremde_steine)
    
    #print("Input_Summe:",np.sum(input))
    
    evaluation = estimator(np.expand_dims(input,axis=0))
    
    return evaluation.numpy()[0,0]
    
    