import os
# import tensorflow as tf
import copy
import numpy as np

estimator_path = 'Tensors/estimator.keras'
import matplotlib.pyplot as plt

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
        self.iterations = 6
        
    def your_turn(self):
        
        # Function is called by self.kaitoGame
        
        self.calculate_best_move()

    def calculate_best_move(self):

        self.total_iterations = 0
        
        move_to_play, evaluation = self.calculate_best_move_recursive(self.kaitoGame.spielstand)
        
        print(f"Total iterations needed for tree search: {self.total_iterations}")
        
        #print("Evaluated my position as:", evaluation)
        
        self.kaitoGame.updatePosition(move_to_play)
        
    def calculate_best_move_recursive(self,spielstand,depth=0,primary=-np.inf,secondary=np.inf):
        
        self.total_iterations += 1
        
        # wenn self.kaitoGame.all_legal_moves [] empty dann füge einen Sieg für den Gegner ein
        
        
        min_or_max = [np.max, np.min] if depth % 2 == 0 else [np.min, np.max]
        
        bestval = min_or_max[1]([np.inf,-np.inf])
        best_move = None
        
        all_legal_moves = self.kaitoGame.all_legal_moves(spielstand)
        
        for next_move in all_legal_moves:
            
            ## move is in [0,36]
            
            ## Durchsusche alle möglichen Züge, die der Spieler hat
            
            #if depth >= 0:
                #print("Move:", next_move,"   Depth:", depth, "Spielzug Nr.", spielstand["spielzug_count"])
            
            next_spielstand = self.kaitoGame.project_move(copy.deepcopy(spielstand), next_move)
                
            if depth < self.iterations:
                
                _, next_move_evaluation = self.calculate_best_move_recursive(copy.deepcopy(next_spielstand), depth + 1, secondary, primary)               
            
            else:
                
                next_move_evaluation = evalNN(self.kaitoGame.matrix_from_spielstand(next_spielstand, self.which_player[0]))
                
            bestval = min_or_max[0]([bestval, next_move_evaluation])
                
            if bestval == next_move_evaluation:
                
                best_move = next_move
            
            primary = min_or_max[0]([primary, bestval])
            
            if min_or_max[0]([primary,secondary]) == primary:
                #print(f"Cut out branch at depth {depth} of {self.iterations}")
                break
        
        self.kaitoGame.whoLost(spielstand)
        
        game_over, winner = spielstand["game_finished_winner"]
        
        i_am_winner = winner is self.which_player[1]

        if game_over and i_am_winner:
            
            if depth == 0:
                
                print("Found winning strategy for winner")
            
            return -1, np.inf if i_am_winner else -np.inf
        
        return best_move, bestval

class FastComputerPlayer:
    
    def __init__(self, game, which_player_str="rot",):
        
        self.iterations = 4
        self.kaitoGame = game
        
        self.which_player = game.s_r_to_binary(which_player_str[0]) # schwarz = +1, rot = -1
        game.players[1] = self
        
        # Initialize game state matrix
        # Diagonal entries represent type of stone
        # Nondiagonal entries represent connection (either 0 or 1)
        
        game_matrix = np.zeros((36,36), dtype="int")
        
        def stone2number(name):
            
            if name=="empt": return 0
            
            sign = +1 if name[0] == "s" else -1
            
            if name[1:] == "Mon1": return sign*1
            if name[1:] == "Mon2": return sign*2
            if name[1:] == "Mon3": return sign*3
            if name[1:] == "Kat":  return sign*4
            if name[1:] == "Kab":  return sign*5
            
            return 1000
        
        spielstand = game.spielstand.copy()

        for cursor in range(36):
            spielstand["cursor"] = cursor
            game_matrix[cursor, game.all_legal_moves(spielstand)] = 1
            game_matrix[cursor, cursor] = stone2number(game.spielstand["spielsteine"][cursor])
        
        
        self.game_state = [game_matrix, cursor] 
        
        plt.imsave("game_matrix.png", game_matrix)
        
    def refresh_game_matrix(self):
        
        for i in range(36):
            
            if self.kaitoGame.spielstand["spielsteine"][i] == "empt":
                
                self.game_state[0][:, i] = np.zeros((36))
                
        self.game_state[1] = self.kaitoGame.spielstand["cursor"]
        
        plt.imsave("game_matrix.png", self.game_state[0])

    def your_turn(self):
        
        # Function is called by self.kaitoGame
        
        self.total_iterations = 0
        
        self.refresh_game_matrix()
        
        move_to_play, evaluation = self.calculate_best_move_recursive(self.game_state, depth=0)
        
        print(f"Decided on move {move_to_play} capturing a {self.kaitoGame.spielstand['spielsteine'][move_to_play]}")
        
        print(f"Total iterations needed for tree search: {self.total_iterations}")
        
        print("Evaluated my position as:", evaluation)
        
        self.kaitoGame.update_evaluation(evaluation)
        
        self.kaitoGame.updatePosition(move_to_play)
        
    def calculate_score(self, game_state):

        return (np.trace(game_state[0]) + np.sign(game_state[1])*2) *  self.which_player
    
    def who_wins(self, game_state, all_legal_moves):
        
        if len(all_legal_moves) == 0:
            
            return np.sign(game_state[1])
        
        all_stones = [game_state[0][i,i] for i in range(36)]
        
        if not (4 in all_stones and 5 in all_stones):
        
            # Black lost, Red won
            return - 1
        
        if not (-4 in all_stones and -5 in all_stones):
        
            # Red loses, Black wins
            return + 1
        
        return 0
    
    def calculate_best_move_recursive(self, game_state, depth=0, primary=-np.inf, secondary=np.inf):
        game_matrix = game_state[0] # Just for debugging
        
        self.total_iterations += 1
        
        min_or_max = [np.max, np.min] if depth % 2 == 0 else [np.min, np.max]
        
        bestval = min_or_max[1]([np.inf,-np.inf])
        best_move = None
    
        all_legal_moves = np.nonzero(game_state[0][abs(game_state[1])])[0]
        
        for next_move in all_legal_moves:
            
            if game_state[1] == next_move: continue
            
            ## move is in [0,36]
            
            ## Durchsusche alle möglichen Züge, die der Spieler hat
            
            next_game_state = [game_state[0].copy(), next_move]
            next_game_state[0][:, next_move] = np.zeros(36)
                
            if depth < self.iterations:
                
                _, next_move_evaluation = self.calculate_best_move_recursive(next_game_state, depth + 1, secondary, primary)               
            
            else:
                
                next_move_evaluation = self.calculate_score(next_game_state)
                
            if depth == 0:
                print("Move:", next_move,"   Depth:", depth, "Evaluation:", next_move_evaluation)
                
            bestval = min_or_max[0]([bestval, next_move_evaluation])
                
            if bestval == next_move_evaluation:
                
                best_move = next_move
            
            primary = min_or_max[0]([primary, bestval])
            
            if min_or_max[0]([primary,secondary]) == primary:
                #print(f"Cut out branch at depth {depth} of {self.iterations}")
                break
        
        winner = self.who_wins(game_state, all_legal_moves)
        
        game_over = abs(winner) == 1
        
        
        i_am_winner = winner * self.which_player
        
        if i_am_winner == 1:
            print("Found a winning strategy for me.")

        if game_over:
            
            print(f"Found winning strategy for {winner}")
            
            return -1, winner*np.inf
        
        return best_move, bestval

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
    
    