# Kaito-Agent
Developing an intelligent player for the chess-like board game Kaito

![User interface for Kaito](User_Interface.png "User interface for Kaito")

## Development Steps

1. Create a game field with the rules implemented
2. Create a user interface for 2 players
3. Enable the development of an intelligent agent by implementing a random player first
4. Define neural network which evaluates the game state (number of remaining Kabutos, Katanas and Mon tiles)
6. Implement depth search for the best move
7. Let the intelligent player train by playing against itself
8. Evaluate the intelligent player

## Kaito Rules

There are 2 opponent players, red and black, and every tile is visible at all times. Red and black move the same game stone in an alternating manner, either horizontally or vertically. A tile is put out of game as soon as the game stone lands on it.

A player wins the game by removing all opponent Katanas (7 swords) or all Kabutos (3 Helmets) from the playing field. Players can also buy back a Kabuto or Katana at the cost of "Mon", which is collected by removing a tile with the Mon symbol, either 1, 2 or 3, either black or red. 

A player can also win, if he puts the other player in a position with no legal move available.

## Results

The intelligent player is significantly better than the random player, but can be easily defeated by a human. The intelligent player doesn't yet understand which moves lead to a loss at the next turn of the opponent.