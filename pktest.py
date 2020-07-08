
import unittest
import pktypes
from pktypes import *
import random


#create Table
t = Table(10)
joe = Player('sdff', 'Joe', bank=44, stack=1000)
fred = Player('sdf2', 'Fred', bank=44, stack=1000)
willis = Player('sdf3', 'willis', bank=44, stack=1000)
sally = Player('sdf9', 'Sally', bank=44, stack=1000)
lucy = Player('sdf8', 'Lucy', bank=44, stack=1000)
patty = Player('sdf7', 'Patty', bank=44, stack=1000)

t.addPlayerToLobby(joe)
t.addPlayerToLobby(fred)
t.addPlayerToLobby(willis)
t.addPlayerToLobby(sally)
t.addPlayerToLobby(lucy)
t.addPlayerToLobby(patty)

for player in t.playersInLobby:
    player.sitDown()
    
print(t)
t.startGame()
pot, small, big = t.startNewHand()
t.deal(small)
print(pot)

class TestSim1(unittest.TestCase):
    
    Player.TEST_runSim(Player, "./testsims/sim1.csv")
    t.beginBetting(pot, small, big)
    
    def test_list_int(self):
        """
        Test that it can sum a list of integers
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)


        
        
if __name__ == '__main__':
    unittest.main()


