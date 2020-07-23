
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

### potValueInRound: 
This stores the aggregate amount in the pot for a given Hand. It is incremented in real time during betting rounds

## Bet: 
An object that represents a bet made by a player. If the bet is re-raised, then a new bet object is created. For example:
<br>
Bets are :AMOUNT - 200INCREMENTAL AMT - 100 raised by willis with callers ['willis'] <br>
AMOUNT - 100INCREMENTAL AMT - 80 raised by Fred with callers ['Fred', 'willis']  <br>
AMOUNT - 20INCREMENTAL AMT - 10 raised by Sally with callers ['Sally', 'willis', 'Fred']  <br>
AMOUNT - 10INCREMENTAL AMT - 10 raised by Lucy with callers ['Lucy', 'Sally', 'willis', 'Fred']  <br>

In this case, the highest (most recent bet) was $200 by Willis. The action is going to the next person. Prior to that bet
Fred had raised it up to 100. Prior to that Sally had raised 20. When someone calls a higher level bet, the bets underneath 
are all automatically called. 

In addition, Fred is all in (not visible here), so he won't be able to call Willis' bet. However he can win the "main pot"
which is the 100 Bet and related callers

   