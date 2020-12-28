
import unittest
import pktypes
from pktypes import *
from pkhands import *
import random


#create Table
t = Table(10,'test')
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

i=9
for player in t.playersInLobby:
    i-=1
    player.sitDown(i)
    
class TestSim1(unittest.TestCase):
    
    def test_sim1(self):
        """
        Test if sim1 works
        """
        #create Table
        t = Table(10,'test')
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

        i=9
        for player in t.playersInLobby:
            player.sitDown(i)
            i-=1
        print(t)
        t.startGame()
        pot, small, big = t.startNewHand()
        Player.TEST_runSim(Player, "./testsims/sim1.csv")
        t.beginBetting(pot, small, big)
        self.assertEqual(pot.potValueInRound, 1410)  # Test that the total pot value is $1,410
        self.assertEqual(t.seatedPlayersDict[4].stack, 1000)  #test Patty's stack
        self.assertEqual(t.seatedPlayersDict[5].stack, 700)  #test Lucy's stack
  
    def test_sim2(self):
        """
        Test if sim2 works
        """
        t2 = Table(10,'test')
        joe = Player('sdff', 'Joe', bank=44, stack=1000)
        fred = Player('sdf2', 'Fred', bank=44, stack=1000)
        willis = Player('sdf3', 'willis', bank=44, stack=1000)
        sally = Player('sdf9', 'Sally', bank=44, stack=1000)
        lucy = Player('sdf8', 'Lucy', bank=44, stack=1000)
        patty = Player('sdf7', 'Patty', bank=44, stack=1000)

        t2.addPlayerToLobby(joe)
        t2.addPlayerToLobby(fred)
        t2.addPlayerToLobby(willis)
        t2.addPlayerToLobby(sally)
        t2.addPlayerToLobby(lucy)
        t2.addPlayerToLobby(patty)
        i=9
        for player in t2.playersInLobby:
            player.sitDown(i) 
            i-=1
        print(t2)
        t2.startGame()
        pot2, small2, big2 = t2.startNewHand()
        print(pot2)
        Player.TEST_runSim(Player, "./testsims/sim2.csv")
        t2.beginBetting(pot2, small2, big2)
        self.assertEqual(pot2.potValueInRound, 80)  # Test that the total pot value is $80
        self.assertEqual(t2.seatedPlayersDict[4].stack, 980)  #test Patty's stack
        self.assertEqual(t2.seatedPlayersDict[5].stack, 980)  #test Lucy's stack
        self.assertEqual(t2.startingPlayer, t2.seatedPlayersDict[6])  #confirm its Sally
             
    def test_valueInRnd(self):
        t3 = Table(10,'test')
        joe = Player('sdff', 'Joe', bank=44, stack=1000)
        fred = Player('sdf2', 'Fred', bank=44, stack=1000)
        willis = Player('sdf3', 'willis', bank=44, stack=1000)
        sally = Player('sdf9', 'Sally', bank=44, stack=1000)
        lucy = Player('sdf8', 'Lucy', bank=44, stack=1000)
        patty = Player('sdf7', 'Patty', bank=44, stack=1000)

        t3.addPlayerToLobby(joe)
        t3.addPlayerToLobby(fred)
        t3.addPlayerToLobby(willis)
        t3.addPlayerToLobby(sally)
        t3.addPlayerToLobby(lucy)
        t3.addPlayerToLobby(patty)

        i=9
        for player in t3.playersInLobby:
            player.sitDown(i)  
            i-=1
        print(t3)
        t3.startGame()
        pot3, small3, big3 = t3.startNewHand()
        print(t3.smallBlindPlayer)
        print(t3)
        self.assertEqual(t3.smallBlindPlayer.valueInRnd, 10)  #test BB VIH
        self.assertEqual(t3.bigBlindPlayer.valueInRnd, 20)  #test BB VIH
        self.assertEqual(t3.smallBlindPlayer.stack, 990)  
        self.assertEqual(t3.bigBlindPlayer.stack, 980)  
        t3.seatedPlayers[-1].Raise(100, pot3)
        self.assertEqual(t3.seatedPlayers[-1].stack, 900)  
        self.assertEqual(t3.seatedPlayers[-1].valueInRnd, 100)
        print(t3)
       
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

    def test_allin(self):
        """
        Test if all in sim works  - ALL INS
        """
        t1 = Table(10,'test')
        joe = Player('sdff', 'Joe', bank=44, stack=500)
        fred = Player('sdf2', 'Fred', bank=44, stack=100)
        willis = Player('sdf3', 'willis', bank=44, stack=1000)
        sally = Player('sdf9', 'Sally', bank=44, stack=800)
        lucy = Player('sdf8', 'Lucy', bank=44, stack=600)
        patty = Player('sdf7', 'Patty', bank=44, stack=1000)

        t1.addPlayerToLobby(joe)
        t1.addPlayerToLobby(fred)
        t1.addPlayerToLobby(willis)
        t1.addPlayerToLobby(sally)
        t1.addPlayerToLobby(lucy)
        t1.addPlayerToLobby(patty)

        i=9
        for player in t1.playersInLobby:
            player.sitDown(i)
            i-=1
        print(t)
        t1.startGame()
        pot2, small, big = t1.startNewHand()
        Player.TEST_runSim(Player, "./testsims/allin2.csv")
        t1.beginBetting(pot2, small, big)
        self.assertTrue(lucy.allIn)
        self.assertTrue(joe.allIn)
        self.assertTrue(sally.allIn)
        self.assertEqual(pot2.potValueInRound, 2800)
        self.assertEqual(patty.valueInRnd, 0)
        self.assertEqual(lucy.valueInRnd, 600)
        self.assertEqual(sally.valueInRnd, 800)
        self.assertEqual(willis.valueInRnd, 800)
        self.assertEqual(fred.valueInRnd, 100)
        self.assertEqual(joe.valueInRnd, 500)
        pot2.collapseBets()
        self.assertEqual(pot2.prevRoundBets[1][0].amount, 100)

            

              
if __name__ == '__main__':
    unittest.main()


