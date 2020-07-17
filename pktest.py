
import unittest
import pktypes
from pktypes import *
from pkhands import *
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
    
class TestSim1(unittest.TestCase):
    
    def test_sim1(self):
        """
        Test if sim1 works
        """
        #print(t)
        t.startGame()
        pot, small, big = t.startNewHand()
        ##t.deal(small)  Now in th start new hand func
        #print(pot)
        Player.TEST_runSim(Player, "./testsims/sim1.csv")
        t.beginBetting(pot, small, big)
        self.assertEqual(pot.potValue, 1410)  # Test that the total pot value is $1,410
        self.assertEqual(t.seatedPlayersDict[4].stack, 1000)  #test Patty's stack
        self.assertEqual(t.seatedPlayersDict[5].stack, 700)  #test Lucy's stack
  
    def test_sim2(self):
        """
        Test if sim2 works
        """
        for player in t.playersInLobby:
            player.stack=1000
        print(t)
        t.startGame()
        pot, small, big = t.startNewHand()
        print(pot)
        Player.TEST_runSim(Player, "./testsims/sim2.csv")
        t.beginBetting(pot, small, big)
        self.assertEqual(pot.potValue, 80)  # Test that the total pot value is $30
        self.assertEqual(t.seatedPlayersDict[4].stack, 980)  #test Patty's stack
        self.assertEqual(t.seatedPlayersDict[5].stack, 980)  #test Lucy's stack
        self.assertEqual(t.startingPlayer, t.seatedPlayersDict[6])  #confirm its Sally
        t.beginBetting(pot, small, big)
        self.assertEqual(t.seatedPlayersDict[5].stack, 980)  #test Lucy's stack
        
    def test_valueInHand(self):
        for player in t.playersInLobby:
            player.stack=1000
        t.startGame()
        pot, small, big = t.startNewHand()
        self.assertEqual(t.smallBlindPlayer.valueInHand, 10)  #test BB VIH
        self.assertEqual(t.bigBlindPlayer.valueInHand, 20)  #test BB VIH
        self.assertEqual(t.smallBlindPlayer.stack, 990)  
        self.assertEqual(t.bigBlindPlayer.stack, 980)  
        t.seatedPlayers[-1].Raise(100, pot)
        self.assertEqual(t.seatedPlayers[-1].stack, 900)  
        self.assertEqual(t.seatedPlayers[-1].valueInHand, 100)
       
    def test_standup(self):
        Lucy = t.seatedPlayersDict[5]
        self.assertIn(Lucy, t.seatedPlayers)
        Lucy.standUp()
        self.assertNotIn(Lucy, t.seatedPlayers)
        
        
if __name__ == '__main__':
    unittest.main()


