import random
import logging
import csv
from pkhands import *

logging.basicConfig(level=logging.ERROR)

myd = {'8s': '<div class="card-tiny"><p class="card-texttiny black">8</p><p class="card-imgtiny black">&spades;</p></div>',
       '8h': '<div class="card-tiny"><p class="card-texttiny red">8</p><p class="card-imgtiny red">&hearts;</p></div>',
       'facedown': '<div class="card-facedown"></div><div class="card-facedown"></div>'
      }
pTxt = lambda x : '<p class="player-text black">'+str(x)+'</p>'

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

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
        self.potValue=0      # Total pot across multiple rounds
        self.potValueInRound=0      # Size of pot for the given round of betting
        self.bets=[]   #Array of bet objects for given betting round, at end of betting rnd is checked for side pots then cleared
        self.prevRoundBets = {}  # dict of previous round collapsed bets. keys are number for betting round
        self.sidePots=[]
        self.table=table
    
    def createSidePotBet(self, higherBet, player):
        lowerBet = self.getLowerBet(higherBet)
        increment = player.stack  #Because player has already called lower bet
        betAmt = lowerBet.amount + increment 
        logging.debug("betamt="+str(betAmt)+ " increment = "+str(increment))
        assert increment >= 0
        sidePotBet = Bet(player, betAmt, increment)
        sidePotBet.addCaller(player)
        self.updatePotValueInRound()
        logging.debug(player.playname+" value in hand is "+str(player.valueInRnd))
        self.insertNewSidePotBet(sidePotBet)
        #Call the lower bets
        while lowerBet:
            lowerBet.addCaller(player)
            lowerBet = self.getLowerBet(lowerBet)
        # Update the "incremental amounts" for the higher bet
        higherBet.incrementAmt = (higherBet.amount - betAmt)
        return
    
    def getLowerBet(self, higherBet):
        lowerBet = None
        for idx, bet in enumerate(self.bets):
            if bet == higherBet:
                lowerBetIdx = idx+1
                if lowerBetIdx < len(self.bets):
                    lowerBet = self.bets[idx+1]
        return lowerBet
    
    def insertNewSidePotBet(self, newBet):
        for idx, bet in enumerate(self.bets):
            if newBet.amount > bet.amount:
                self.bets.insert(idx,newBet)
                for i in range(idx):   #Add players from higher bets to this pot
                    highestCallers = self.bets[i].callers
                    for caller in highestCallers:
                        if caller not in newBet.callers:
                            newBet.callers.append(caller)
                return
        return

    def updatePotValueInRound(self):
        players = self.table.seatedPlayers
        roundtotal = 0
        for p in players:
            roundtotal += p.valueInRnd
        self.potValueInRound = roundtotal
        logging.debug("pot value in round is "+str(roundtotal))
    
    ## Collapse bets to get side pots
    def collapseBets(self):
        sidebets = []
        if self.bets:
            prevbet = self.bets[-1]
            for bet in reversed(self.bets):
                names = [p.playname for p in bet.callers]
                if len(set(prevbet.callers)-set(bet.callers)) > 0:
                    sidebets.append(prevbet)
                prevbet = bet
            if self.bets[0] not in sidebets:
                sidebets.append(self.bets[0])  # The highest level bet will need to be evaluated
            for i in range(len(sidebets)):
                bet = sidebets[i]
                if i>0:
                    prevbet = sidebets[i-1]
                    bet.incrementAmt = bet.amount - prevbet.amount 
                else:
                    bet.incrementAmt = bet.amount
            self.prevRoundBets[self.table.bettingRound] = sidebets
            self.bets = []
            self.potValue += self.potValueInRound
            self.potValueInRound = 0
            players = self.table.seatedPlayers
            for p in players:  # Reset the players value in betting rnd since a new round is starting
                p.valueInRnd = 0
        return 
    
    ## Convert collapsed bets into showdowns to determine pot winners
    def getShowdowns(self):
        allbetlist = []
        for k in sorted(self.prevRoundBets.keys()):
            allbetlist.append(self.prevRoundBets[k])
        flat_list = [item for sublist in allbetlist for item in sublist]
        showdowns={}
        betnum=1
        curbet = flat_list.pop(0)
        curcallers = set(curbet.callers)
        bet_total = curbet.betTotalIncremental
        showdowns[betnum]= {'amt':bet_total, 'callers':curcallers}
        while flat_list:
            nextbet = flat_list.pop(0)
            nextcallers = set(nextbet.callers)
            if len(curcallers-nextcallers)>0:   #This determines if a new side pot has been hit
                showdowns[betnum]= {'amt':bet_total, 'callers':curcallers}
                bet_total = 0
                betnum+=1
            bet_total += nextbet.betTotalIncremental
            curcallers = nextcallers  
            showdowns[betnum]= {'amt':bet_total, 'callers':curcallers}
        return showdowns 
    
    def __str__(self):
        resp="Bets are :"
        for b in self.bets:
            resp+="AMOUNT - "+str(b.amount)
            resp+="INCREMENTAL AMT - "+str(b.incrementAmt)
            resp+=" raised by "+str(b.raiser.playname)
            resp+=" with callers "+str([x.playname for x in b.callers])+"\n "
        resp+=" \n. total pot value : "+str(self.potValue)
        resp+=" \n. total pot value IN ROUND : "+str(self.potValueInRound)
        resp+=" \n. STARTING PLAYER : "+str(self.table.startingPlayer.playname)
        return resp
    
    
class Bet:
    
    def __init__(self, player, amount, incrementAmt):
        self.raiser=player
        self.callers=[]
        self.amount=amount
        self.incrementAmt=incrementAmt
    
    def addCaller(self, caller):
        if caller not in self.callers:
            self.callers.append(caller)
            caller.stack -= self.incrementAmt
            caller.valueInRnd += self.incrementAmt
            assert caller.stack >= 0
            logging.debug(caller.playname+" calling bet total: "+str(self.amount)+" incremental amt: "+str(self.incrementAmt))
            logging.debug("\nvalue in round = "+str(caller.valueInRnd))
        
    def removeCaller(self, callerToRemove):
        if callerToRemove in self.callers:
            self.callers.remove(callerToRemove)
        
    @property
    def betTotal(self):
        return len(self.callers)*self.amount  
    
    @property
    def betTotalIncremental(self):
        return len(self.callers)*self.incrementAmt
    
    def __str__(self):
        resp = "BET OBJECT \n amount:"+str(self.amount)+" INCREMENT AMT: "+str(self.incrementAmt)
        resp += "\nCALLERS:"+str([c.playname for c in self.callers])
        return resp
    
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
        self.atTable=False  #Table object that player is at
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
    
    @property
    def handScore(self):
        return getHand(self.atTable.communityCards + self.hand)
    
    def addCardToHand(self, card):
        self.hand.append(card)
        
    def clearHand(self):
        self.hand=[]
        self.folded=False
        self.allIn=False
        self.valueInRnd=0
    
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
        if self.folded or self.allIn:
            logging.debug("Player "+self.playname+" has already folded or is all in")
            return
        amount=0
        noAction = False
        allInAmt = self.getAllInAmt()
        if not pot.bets:   # No previous bets
            noAction = True
            logging.info("Check to you, "+self.playname+". Raise or Check"+" all in amt is "+str(allInAmt))
        else:
            minRaise = self.getMinRaise(pot)
            lgmsg = "Raised to "+self.playname+". Fold, Call or Raise. Min Raise is "
            lgmsg+=str(minRaise)+" all in amt is "+str(self.getAllInAmt())
            logging.info(lgmsg) 
        if Player.TEST_simulate:
            simact = tuple(Player.TEST_simvals.pop(0))
            action, amount = simact
        else:
            action, amount = input("Enter action and amount: ").split() 
        logging.info("\n\n"+self.playname+" decides to "+str(action)+" "+str(amount))
        decision = getattr(self, action)
        decision(int(amount), pot)
        logging.debug("\n STACK: "+str(self.stack)+"\n VALUE IN HAND: "+str(self.valueInRnd)+"\n*** POT *****\n\n\n\n")
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
        logging.debug("Reducing stack by"+str(incrementalBet))
        pot.bets.insert(0,newbet)
        pot.updatePotValueInRound()
        self.atTable.startingPlayer = self
        return 
        
    def Call(self, _, pot):
        upstreamBetAmt = 0
        if pot.bets:
            for upstreamBet in reversed(pot.bets):
                if self not in upstreamBet.callers:
                    if upstreamBet.incrementAmt > self.stack:
                        logging.debug("CREATE SIDE POT")
                        logging.debug("Upstream Bet amt: "+str(upstreamBetAmt)+" stack: "+str(self.stack))
                        self.allIn=True
                        pot.createSidePotBet(upstreamBet, self)  
                        return
                    else:
                        upstreamBet.addCaller(self)
            pot.updatePotValueInRound()
        else:
            logging.debug("NO PREV BET")
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
        self.seatedPlayersDict={} #key is seatnumber, value is player object
        self.maxseats=maxseats
        self.openSeatNums=list(range(maxseats))  #Unordered list of open seat numbers. Starts at 0
        self.buttonSeatNum=None     # Seat number for button
        self.numHands=0
        self.socketio=None
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
        
    def startNewHand(self):
        logging.debug("New HAND")
        if self.socketio:
            self.socketio.emit('output', 'NEW HAND START')
        self.bettingRound=0
        if(len(self.occupiedSeatNums))<self.MINPLAYERS:
            logging.warning("Need at least 3 seated players to start")
            return
        self.numHands+=1
        self.clearAllPlayerHands()
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
            self.startingPlayer =  bettingPlayer = smallBlindPlyr  #Action & betting starts to right of button
        actionRemains = True
        logging.debug("Betting Round "+str(self.bettingRound)+"Action begins with "+bettingPlayer.playname)
        while actionRemains:
            bettingPlayer.getAction(pot)
            bettingPlayer = self.getNextSeatedPlayer(bettingPlayer)
            if bettingPlayer == self.startingPlayer:  #We have come back around to the starting action
                actionRemains = False
        logging.debug("Betting round complete + Pot details:\n")
        logging.debug(pot)
        return
    
    def settlePots(self, pot):
        pot.collapseBets()
        sdowns = pot.getShowdowns()
        for s in sdowns:
            logging.debug("SHOWDOWN "+str(s))
            callerList = list(sdowns[s]['callers'])
            callerList.sort(key=lambda x: x.handScore[2], reverse=True)
            logging.debug([p.playname for p in callerList])
            allscores=[x.handScore[2] for x in callerList] #Array of all the scores
            logging.debug(allscores)
            if allscores[0] in allscores[1:]:  #Someone else has the winning score
                logging.debug("CHOP POT")
                chopIdxs = [i for i, val in enumerate(allscores) if val==allscores[0]] 
                chopPlayers=[callerList[idx] for idx in chopIdxs]
                logging.debug("winners "+str([x.playname for x in chopPlayers])+" with "+callerList[0].handScore[3]+" "+str(allscores[0]))
            else:
                winnerPlayer = callerList[0]
                logging.debug("- winner- "+str(winnerPlayer.playname)+" w/ "+winnerPlayer.handScore[3]+" "+str(winnerPlayer.handScore[2]))
        return
    
    def printPlayerHands(self):
        rsp={'val1': 'WORKING'}
        for _, player in self.seatedPlayersDict.items():
            print("Player "+player.playname+" hand is "+str(player.humanReadableHand))
            pkey = "box"+str(player.seatNum)
            rsp[pkey] = myd['8h']+myd['8s']+pTxt('YYY')
        
        rsp2 = {'val1': 'NUM2', 
            'box1': myd['8h']+myd['8h']+pTxt('checQ'), 
            'box5': myd['facedown']+pTxt('check10Q'),
            'box4': myd['facedown']+pTxt('check2Q'),
             }
        self.socketio.emit('table_state', rsp, callback=messageReceived)
        self.socketio.emit('table_state', rsp2, room='sdf')  ## SEND SPECIFIC CARD VIEW TO DIFFERENT ROOMS
            
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
    


    
             