
# Description of Objects and Definitions

## Lobby: 
This is not an object. It is a staging area for players who are waiting to sit at a Table. TBD - whether you can have more players in the Lobby than you have seats. 

## Player: 
Object representing a player. 

## Table: 
Object representing the table

## Hand: 
A cycle of poker that starts with the button moving, deal, and then ends with a player winning. Within a Hand there are 4 betting rounds (or stages) - Preflop, post flop, Turn, River

## Betting Round: 
A round of betting for a given stage of a hand. It starts the right of the button (or right of BB for preflop). Continues until everyone has called or folded. At any given time, the player's investment is defined by "value in round" attribute. This is reset after a given betting round is complete

## Pot: 
Object representing a pot for a given Hand. Once the Hand is complete, the pot is discarded and a new instance is created. During the Hand, for a given betting round there Bets made. Each Bet is stored in an array under the Pot instance. At the end of the Betting Round, the array of Bet of cleared. 
### potValue: 
This stores the aggregate amount in the pot for a given Hand. It is incremented in real time during betting rounds

## Bet: 
An object that represents a bet made by a player. If the bet is re-raised, then a new bet object is created. 


sdfds


    def test_allin(self):
        """
        Test if all in sim works  - ALL INS
        """
        for player in t.playersInLobby:
            player.stack=1000
        print(t)
        t.startGame()
        pot, small, big = t.startNewHand()
        Player.TEST_runSim(Player, "./testsims/allin.csv")
        t.beginBetting(pot, small, big)
        self.assertTrue(t.seatedPlayersDict[5].allIn)
        pot.clearBetsForRound()
        ####. ADDDO SOME ASSERTS HERE ************
        #self.assertEqual(pot.potValue, 1410)    
        #self.assertEqual(pot.potValue, 1410)    