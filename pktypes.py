import random
import logging
import csv

logging.basicConfig(level=logging.DEBUG)


class Card:

    RANKS=['2','3','4','5','6','7','8','9','10','J', 'Q', 'K', 'A']
    SUITS=['h', 'c', 's', 'd']
    
    def __init__(self,rank, suit, faceup=True):
        self.rank=rank
        self.suit=suit
        self.value=(Card.RANKS.index(self.rank)+2)
        self.faceup=faceup
        self.rawval=rank+suit

    def __str__(self):
        if self.faceup:
            return str(self.rank)+str(self.suit)
        else:
            return 'XX'

class Pot:
    
    def __init__(self, table):
        self.potValue=0
        self.bets=[]   #Array of bet objects for given betting round, at end of betting rnd is checked for side pots then cleared
        self.sidePots=[]
        self.table=table
    
    def createSidePot(self):
        pass
    
    def clearBetsForRound(self):
        self.bets=[]  # Clear bet objects for this round of betting
        for p in self.table.seatedPlayers:
            p.valueInRnd=0  # reset the value in hand amt
        return
    
    def __str__(self):
        resp="Bets are :"
        for b in self.bets:
            resp+=" - "+str(b.amount)
            resp+=" raised by "+str(b.raiser.playname)
            resp+=" with callers "+str([x.playname for x in b.callers])+"\n "
        resp+=" \n. total pot value : "+str(self.potValue)
        resp+=" \n. STARTING PLAYER : "+str(self.table.startingPlayer.playname)
        return resp
    
    
class Bet:
    
    def __init__(self, player, amount, incrementAmt):
        self.raiser=player
        self.callers=[]
        self.closed=False
        self.amount=amount
        self.incrementAmt=incrementAmt
    
    def addCaller(self, caller):
        self.callers.append(caller)
        
    def removeCaller(self, callerToRemove):
        if callerToRemove in self.callers:
            self.callers.remove(callerToRemove)
        
class Deck:
    
    def __init__(self):
        self.cards=[]
        self.repopulate()
        self.shuffle()

    def repopulate(self):
        self.cards=[]
        for rank in Card.RANKS:
            for suit in Card.SUITS:
                card=Card(rank, suit)
                self.cards.append(card)
            
    def clear(self):
        self.cards=[]

    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal(self, numcards):
        cardsDealt=[]
        for _ in range(numcards):
            cardsDealt.append(self.cards.pop())
        return cardsDealt

    def print_cards(self):
        rep=''
        for card in self.cards:
            rep+=str(card)+' '
        print(rep)

              
class Player:
    
    TEST_simvals = None
    TEST_simulate= False
    def TEST_runSim(cls, fname):
        cls.TEST_simulate=True
        logging.debug("Loading simulation")
        with open(fname, newline='') as csvfile:
            cls.TEST_simvals = list(csv.reader(csvfile))
    
    def __init__(self, usrId, playname, bank, stack):
        self.usrId=usrId
        self.bank=bank
        self.stack=stack
        self.playname=playname
        self.atTable=False
        self.seated=False
        self.seatNum=None
        self.hand=[]
        self.folded=False
        self.valueInRnd=0 #For a given round of betting, how much the player has already invested
        self.allIn=False #Is the player all in?
                
    @property
    def humanReadableHand(self):
        readableHand=[]
        for card in self.hand:
            readableHand.append(card.rawval)
        return readableHand   
        
    def addCardToHand(self, card):
        self.hand.append(card)
        
    def clearHand(self):
        self.hand=[]
        self.folded=False
        self.allIn=False
    
    def getUpstreamBetAmt(self, pot):
        upstreamBetAmt = 0
        if pot.bets:
            upstreamBetAmt = pot.bets[0].amount
        return upstreamBetAmt  
    
    def getMinRaise(self, pot):
        if pot.bets:
            upstreamBet = pot.bets[0]
            upstreamBetAmt = upstreamBet.amount
            upstreamIncrementAmt = upstreamBet.incrementAmt
            minRaise = upstreamBetAmt + upstreamIncrementAmt
        else:
            minRaise = Table.BLINDS[1]
        return minRaise
    
    def getAllInAmt(self):
        return self.valueInRnd + self.stack
    
    def getAction(self, pot):
        if self.folded:
            logging.debug("Player "+self.playname+" has already folded")
            return
        amount=0
        noAction = False
        if not pot.bets:   # No previous bets
            noAction = True
            logging.info("Check to you, "+self.playname+". Raise or Check"+" all in amt is "+str(self.getAllInAmt()))
        else:
            minRaise = self.getMinRaise(pot)
            lgmsg = "Raised to "+self.playname+". Fold, Call or Raise. Min Raise is "+str(minRaise)+" all in amt is "+str(self.getAllInAmt())
            logging.info(lgmsg) 
        if Player.TEST_simulate:
            simact = tuple(Player.TEST_simvals.pop(0))
            action, amount = simact
        else:
            action, amount = input("Enter action and amount: ").split() 
        logging.info("\n\n"+self.playname+" decides to "+str(action)+" "+str(amount))
        decision = getattr(self, action)
        decision(int(amount), pot)
        logging.debug("\n STACK: "+str(self.stack)+"\n VALUE IN HAND: "+str(self.valueInRnd)+"\n******* POT *******\n")
        logging.debug(pot)
        return
        
    def Raise(self, betAmount, pot):
        self.Call(0, pot)  # Call previous bets
        upstreamBetAmt = self.getUpstreamBetAmt(pot)
        logging.debug("RAISING")
        incrementalBet = betAmount - upstreamBetAmt
        if incrementalBet >= self.stack:
            logging.debug("\n+++++++++\nPLAYER IS ALL IN")
            incrementalBet = self.stack
            betAmount = upstreamBetAmt + self.stack
            self.allIn=True
        newbet = Bet(self, betAmount, incrementalBet)
        newbet.addCaller(self)
        self.stack -= incrementalBet
        self.valueInRnd += incrementalBet
        logging.debug("Reducing stack by"+str(incrementalBet))
        pot.bets.insert(0,newbet)
        pot.potValue+=incrementalBet
        self.atTable.startingPlayer = self
        return 
        
    def Call(self, _, pot):
        upstreamBetAmt = 0
        if pot.bets:
            for idx in range(len(pot.bets)):
                upstreamBet = pot.bets[idx]
                if self not in upstreamBet.callers:
                    upstreamBetAmt += upstreamBet.incrementAmt
                    upstreamBet.addCaller(self)
            pot.potValue+=upstreamBetAmt
        else:
            logging.debug("NO PREV BET")
        self.stack -= upstreamBetAmt
        self.valueInRnd += upstreamBetAmt
        logging.debug("CALL - Reducing stack by"+str(upstreamBetAmt))
        return 
    
    def Check(self, amount, pot):
        logging.debug("CHECKING")
        return
    
    def Fold(self, amount, pot):
        self.folded=True
        for bet in pot.bets:
            if self in bet.callers:
                bet.removeCaller(self)
        for bet in pot.sidePots:  #Since player folded they can't get action from side pots
            bet.removeCaller(self)
        return
        
    def RaiseAllIn(self, amount, pot):
        pass
    
    def CallAllIn(self, amount, pot):
        pass

    def callUpstreamBets(self, pot):
        for bet in pot.bets:
            if self not in bet.callers:
                bet.addCaller(self)
    
    def sitDown(self):
        if self.atTable:
            self.seated=True
            seatNum = self.atTable.seatPlayer(self)
            self.seatNum = seatNum
        else:
            logging.warning("Need to be in the lobby first")
        return
        
    def standUp(self):
        self.atTable.unSeatPlayer(self)
        self.seated=False
        self.seatNum=None
        return
        
    def joinLobby(self):
        pass
    
    def leaveLobby(self):
        if self.seated:
            self.standUp()
        self.atTable.removePlayerFromLobby(self)
        self.atTable=False
        return
        
    def __str__(self):
        resp = self.playname+" is the player and they have "+str(self.stack)+" chips"
        return resp

    
class Table:
    
    BLINDS=[10,20]
    
    def __init__(self, maxseats):
        self.tableId=1
        self.online=False
        self.MINPLAYERS = 3 #min number of seated players
        self.deck=Deck()
        self.playersInLobby=[]
        self.totalPot=0  # Value of pot from previous betting rounds for a given hand
        self.seatedPlayersDict={} #key is seatnumber, value is player object
        self.maxseats=maxseats
        self.openSeatNums=list(range(maxseats))  #Unordered list of open seat numbers. Starts at 0
        self.buttonSeatNum=None     # Seat number for button
        self.numHands=0
        self.startingPlayer=None  
        self.bettingRound=0 #1 = preflop, 2=flop, 3=turn, 4=river
        self.communityCards=[]
      
    @property
    def occupiedSeatNums(self):
        seatnums = list(self.seatedPlayersDict.keys())
        seatnums.sort()
        return seatnums    
     
    @property
    def seatedPlayers(self):
        return list(self.seatedPlayersDict.values())  

    @property
    def buttonPlayer(self):
        return self.seatedPlayersDict[self.buttonSeatNum] 
    
    @property
    def smallBlindPlayer(self):
        return self.getNextSeatedPlayer(self.buttonPlayer) 
      
    @property
    def bigBlindPlayer(self):
        return self.getNextSeatedPlayer(self.smallBlindPlayer) 
        
    def startGame(self):
        self.online=True
        if(len(self.occupiedSeatNums))<self.MINPLAYERS:
            logging.info("Need at least 3 seated players to start")
            return
        self.buttonSeatNum = self.occupiedSeatNums[-1]  #Button will move to first seat when round is reset
        return
        
    def pauseGame(self):
        pass
        
    def endGame(self):
        pass
    
    def addPlayerToLobby(self, playerToAdd):
        if playerToAdd in self.playersInLobby:
            logging.error("Error Player already at table")
        else:
            self.playersInLobby.append(playerToAdd)
            playerToAdd.atTable = self
            
    def seatPlayer(self, playerToSeat):
        if self.openSeatNums:
            seatNum = self.openSeatNums.pop()
            self.seatedPlayersDict[seatNum] = playerToSeat
            return seatNum
        else:
            logging.info("No more seats at the table")
            return

    def unSeatPlayer(self, playerToUnSeat):
        openSeatNum=playerToUnSeat.seatNum
        self.seatedPlayersDict.pop(openSeatNum)
        self.openSeatNums.append(openSeatNum)
        pass
    
    def removePlayerFromLobby(self, playerToRemove):
        if playerToRemove.seated:
            playerToRemove.standUp()
        newLobbyList = [p for p in self.playersInLobby if not p.usrId == playerToRemove.usrId]
        self.playersInLobby = newPlayerList
        
    def clearPlayerHands(self):
        for player in self.seatedPlayers:
            player.clearHand()
    
    def startNewHand(self):
        logging.debug("New HAND")
        self.bettingRound=0
        if(len(self.occupiedSeatNums))<self.MINPLAYERS:
            logging.warning("Need at least 3 seated players to start")
            return
        self.numHands+=1
        self.clearPlayerHands()
        self.moveBtton()
        logging.info("Button is at seat Number: "+str(self.buttonSeatNum))
        self.deck.repopulate()
        self.deck.shuffle()
        pot=Pot(self)
        self.getAntes(pot, self.smallBlindPlayer, self.bigBlindPlayer)
        self.deal(self.smallBlindPlayer)
        return (pot, self.smallBlindPlayer, self.bigBlindPlayer)
   
    def getAntes(self, pot, smallBlindPlyr, bigBlindPlyr):
        smallBlindPlyr.Raise(Table.BLINDS[0], pot)
        bigBlindPlyr.Raise(Table.BLINDS[1], pot)   
         
    def deal(self, smallBlindPlyr):
        self.clearAllPlayerHands()
        cur_player = smallBlindPlyr
        for _ in range(2):
            for _ in range(len(self.seatedPlayers)):
                card = self.deck.deal(1)[0]
                cur_player.addCardToHand(card)
                logging.debug("Dealt "+card.rawval+" to "+cur_player.playname)
                cur_player = self.getNextSeatedPlayer(cur_player)
        self.printPlayerHands()
    
    def dealCommCards(self, numcards):
        for _ in range(numcards):
            card = self.deck.deal(1)[0]
            self.communityCards.append(card)
        logging.debug("Community Cards: "+str([c.rawval for c in self.communityCards]))
        return
    
    def clearAllPlayerHands(self):
        for p in self.seatedPlayers:
            p.clearHand()
        return
    
    def beginBetting(self, pot, smallBlindPlyr, bigBlindPlyr):
        self.bettingRound+=1
        if self.bettingRound == 1:
            self.startingPlayer = bigBlindPlyr #This is the player that started the action with their bet
            bettingPlayer = self.getNextSeatedPlayer(bigBlindPlyr)  #New betting starts to right of BB
        else:
            self.startingPlayer = bettingPlayer = smallBlindPlyr #Action & betting starts to right of button
        actionRemains = True
        logging.debug("Betting Round "+str(self.bettingRound)+"Action begins with "+bettingPlayer.playname)
        while actionRemains:
            bettingPlayer.getAction(pot)
            bettingPlayer = self.getNextSeatedPlayer(bettingPlayer)
            if bettingPlayer == self.startingPlayer:  #We have come back around to the starting action
                actionRemains = False
        logging.debug("Betting round complete + Pot details:\n")
        logging.debug(pot)
        #pot.clearBetsForRound()
        return
    
    def printPlayerHands(self):
        for _, player in self.seatedPlayersDict.items():
            print("Player "+player.playname+" hand is "+str(player.humanReadableHand))
            
    def moveBtton(self):
        self.buttonSeatNum = self.getNextSeatNum(self.buttonSeatNum)

    ## Get the player to the left of the current player
    def getNextSeatedPlayer(self, cur_player):
        cur_seat_num = cur_player.seatNum
        nextSeatNum = self.getNextSeatNum(cur_seat_num)
        return self.seatedPlayersDict[nextSeatNum]  
    
    ## Get the player to the left of the current player
    def getNextSeatNum(self, cur_seat_num):
        cur_seat_idx = self.occupiedSeatNums.index(cur_seat_num)
        if cur_seat_idx == len(self.occupiedSeatNums)-1:
            cur_seat_idx = 0
        else:
            cur_seat_idx+=1
        return self.occupiedSeatNums[cur_seat_idx]
    
    ## Get the player to the right of the current player
    def getPrevSeatedPlayer(self, cur_player):
        cur_seat_num = cur_player.seatNum
        prevSeatNum = self.getPrevSeatNum(cur_seat_num)
        return self.seatedPlayersDict[prevSeatNum]  
    
    ## Get the seat number to the right of the current seat number    
    def getPrevSeatNum(self, cur_seat_num):
        cur_seat_idx = self.occupiedSeatNums.index(cur_seat_num)
        if cur_seat_idx == 0:
            cur_seat_idx = len(self.occupiedSeatNums)-1
        else:
            cur_seat_idx-=1
        return self.occupiedSeatNums[cur_seat_idx]
      
    def __str__(self):
        resp = "Table online is "+str(self.online)+" Players in Lobby "+str([p.playname for p in self.playersInLobby])
        resp+="\n\n Open Seat nums"+str(self.openSeatNums)
        resp+="\nseated players:\n"
        for player in self.seatedPlayers:
            resp+=str(player.seatNum)+" - "+str(player.playname)+" STACK:"+str(player.stack)+"\n"
        return resp
    

    
    
                