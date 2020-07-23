
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
        for player in t.playersInLobby:
            player.stack=1000
        print(t)
        t.startGame()
        pot, small, big = t.startNewHand()
        Player.TEST_runSim(Player, "./testsims/sim1.csv")
        t.beginBetting(pot, small, big)
        self.assertEqual(pot.potValueInRound, 1410)  # Test that the total pot value is $1,410
        self.assertEqual(t.seatedPlayersDict[4].stack, 1000)  #test Patty's stack
        self.assertEqual(t.seatedPlayersDict[5].stack, 700)  #test Lucy's stack
        pot.clearBetsForRound()
  
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
        self.assertEqual(pot.potValueInRound, 80)  # Test that the total pot value is $30
        self.assertEqual(t.seatedPlayersDict[4].stack, 980)  #test Patty's stack
        self.assertEqual(t.seatedPlayersDict[5].stack, 980)  #test Lucy's stack
        self.assertEqual(t.startingPlayer, t.seatedPlayersDict[6])  #confirm its Sally
        pot.clearBetsForRound()
        t.beginBetting(pot, small, big)
        self.assertEqual(t.seatedPlayersDict[5].stack, 980)  #test Lucy's stack
        
        
    def test_valueInRnd(self):
        for player in t.playersInLobby:
            player.stack=1000
        t.startGame()
        pot, small, big = t.startNewHand()
        print(t.smallBlindPlayer)
        print(t)
        self.assertEqual(t.smallBlindPlayer.valueInRnd, 10)  #test BB VIH
        self.assertEqual(t.bigBlindPlayer.valueInRnd, 20)  #test BB VIH
        self.assertEqual(t.smallBlindPlayer.stack, 990)  
        self.assertEqual(t.bigBlindPlayer.stack, 980)  
        t.seatedPlayers[-1].Raise(100, pot)
        self.assertEqual(t.seatedPlayers[-1].stack, 900)  
        self.assertEqual(t.seatedPlayers[-1].valueInRnd, 100)
        print(t)
       
    def test_standup(self):
        Lucy = t.seatedPlayersDict[5]
        self.assertIn(Lucy, t.seatedPlayers)
        Lucy.standUp()
        self.assertNotIn(Lucy, t.seatedPlayers)
        
    def testFlush(self):
        allCards = [Card('J','h'), Card('3','s'), Card('4','s'), Card('8','s'), 
                    Card('2','d'), Card('2','s'), Card('A','s')]
        hand = getHand(allCards)
        self.assertEqual(hand[3], "Flush")
        
    def testShowdown(self):
        allCards1 = [Card('J','s'), Card('4','s'), Card('10','s'), Card('8','h'), 
                    Card('2','d'), Card('K','s'), Card('2','s')]
        allCards2 = [Card('J','s'), Card('A','d'), Card('10','s'), Card('8','h'), 
                    Card('2','d'), Card('K','s'), Card('Q','s')]
        hand1 = getHand(allCards1)
        hand2 = getHand(allCards2)
        self.assertGreater(hand1[2], hand2[2])
        self.assertEqual(hand1[3], "Flush")
        self.assertEqual(hand2[3], "Straight")
        
    def testFull(self):
        allCards = [Card('J','h'), Card('J','s'), Card('4','s'), Card('J','d'), 
                    Card('2','d'), Card('2','s'), Card('A','s')]
        hand = getHand(allCards)
        self.assertEqual(hand[3], "Full House")  
            
    def testTwoPair(self):
        allCards = [Card('A','h'), Card('A','s'), Card('4','s'), Card('J','d'), 
                    Card('2','d'), Card('2','s'), Card('K','c')]
        hand = getHand(allCards)
        self.assertEqual(hand[3], "Pair_s")
        self.assertEqual(len(hand[1]), 2)

    def testShowdown2(self):
        allCards1 = [Card('J','s'), Card('J','d'), Card('2','s'), Card('2','h'), 
                    Card('A','d'), Card('K','s'), Card('7','s')]
        allCards2 = [Card('8','s'), Card('8','d'), Card('3','s'), Card('3','h'), 
                    Card('A','d'), Card('K','s'), Card('7','s')]
        hand1 = getHand(allCards1)
        hand2 = getHand(allCards2)
        self.assertGreater(hand1[2], hand2[2])
        self.assertEqual(hand1[3], "Pair_s")
        self.assertEqual(hand2[3], "Pair_s")

'''    def test_allin(self):
        """
        Test if all in sim works  - ALL INS
        """
        for player in t.playersInLobby:
            player.stack=1000
        print(t)
        t.startGame()
        pot2, small, big = t.startNewHand()
        Player.TEST_runSim(Player, "./testsims/allin.csv")
        t.beginBetting(pot2, small, big)
        self.assertTrue(t.seatedPlayersDict[5].allIn)
        pot2.clearBetsForRound()
        ####. ADDDO SOME ASSERTS HERE ************
        #self.assertEqual(pot.potValue, 1410)            
'''
              
if __name__ == '__main__':
    unittest.main()


