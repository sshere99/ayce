import random

class Card:

    RANKS=['2','3','4','5','6','7','8','9','10','J', 'Q', 'K', 'A']
    SUITS=['h', 'c', 's', 'd']
    
    def __init__(self,rank, suit, faceup=True):
        self.rank=rank
        self.suit=suit
        self.value=(Card.RANKS.index(self.rank)+1)
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
        self.raised={}
        self.table=table
        self.actionRemains=False
        self.clearRaise()
    
    def raisePot(self,raiser,amount,allIn):
        self.raised['isRaised']=True
        self.raised['raisedBy']=raiser
        self.raised['amount']=amount
        self.raised['allInFlag']=allIn
    
    def clearRaise(self):
        self.raised={'isRaised':False, 'raisedBy':None, 'raiseAmt':None, 'allInFlag':False}
    
    def __str__(self):
        resp = "Pot Value is "+str(self.potValue)
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
    
    @classmethod
    def classmthd(cls):
        return 'class method called'
    
    def __init__(self, usrId, playname, bank, stack):
        self.usrId=usrId
        self.bank=bank
        self._stack=stack
        self.playname=playname
        self.atTable=False
        self.seated=False
        self.seatNum=None
        self.hand=[]
        self.folded=False
        self.raised=False
        
    @property
    def stack(self):
        return self._stack
    
    @stack.setter
    def changeStackAmt(self, increment):
        self._stack += increment 
        
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
        self.raised=False
    
    def getAction(self, table, pot):
        options=['Fold']
        isPotRaised = pot.raised.isRaised
        if isPotRaised:
            if pot.raised.raisedBy == self:
                pot.actionRemains = False
                return
            else:
                options.append('Call', 'reraise')
        
        action = input("your options are:"+str(options))
        pass
        #options=['check', 'raise', 'fold', 'call']
        
    def Raise(self, amount, pot):
        self.changeStackAmt(-amount)
        pot.potVaue += amount
        pot.raised = {'isRaised':True, 'raisedBy':self, 'raiseAmt':amount, 'allInFlag':False}
        
    def Call(self, amount, pot):
        pass
        
    def RaiseAllIn(self, amount, pot):
        pass
    
    def CallAllIn(self, amount, pot):
        pass
    
    def Fold(self, amount, pot):
        self.folded=True
        pass
        
    def sitDown(self):
        if self.atTable:
            self.seated=True
            seatNum = self.atTable.seatPlayer(self)
            self.seatNum = seatNum
        else:
            print("Need to be added to a table first")
        
    def standUp(self):
        self.atTable.unSeatPlayer(self)
        self.seated=False
        self.seatNum=None
        
    def joinTable(self):
        pass
    
    def leaveTable(self):
        if self.seated:
            self.standUp()
        self.atTable.removePlayerFromTable(self)
        self.atTable=False
        
    def __str__(self):
        resp = self.playname+" is the player and they have "+str(self._stack)+" chips"
        return resp

    
class Table:
    
    BLINDS=[10,20]
    
    def __init__(self, maxseats):
        self.tableId=1
        self.online=False
        self.MINPLAYERS = 3 #min number of seated players
        self.deck=Deck()
        self.players=[]
        self.pots=[]  #main pot and side pots for a given hand
        self.seatedPlayers={} #key is seatnumber, value is player object
        self.maxseats=maxseats
        self.openSeatNums=list(range(maxseats))  #Unordered list of open seat numbers. Starts at 0
        self.buttonSeatNum=None     # Seat number for button
        self.smallSeatNum=None  # Seat number for small blind
        self.bigSeatNum=None    # Seat number for big blind
        self.numHands=0
        self.actionToSeatNum=None
        self.bettingRound=0 #1 = preflop, 2=flop, 3=turn, 4=river
      
    @property
    def occupiedSeatNums(self):
        seatnums = list(self.seatedPlayers.keys())
        seatnums.sort()
        return seatnums    
     
    def startGame(self):
        self.online=True
        if(len(self.occupiedSeatNums))<self.MINPLAYERS:
            print("Need at least 3 seated players to start")
            return
        self.buttonSeatNum = self.occupiedSeatNums[0]
        self.smallSeatNum = self.getNextSeatNum(self.buttonSeatNum)
        self.bigSeatNum= self.getNextSeatNum(self.smallSeatNum)
        return
        
    def pauseGame(self):
        pass
        
    def endGame(self):
        pass
    
    def addPlayerToTable(self, playerToAdd):
        if playerToAdd in self.players:
            print("Error Player already at table")
        elif len(self.players) == self.maxseats:
            print("Table is full")
        else:
            self.players.append(playerToAdd)
            playerToAdd.atTable = self
            
    def seatPlayer(self, playerToSeat):
        seatNum = self.openSeatNums.pop()
        self.seatedPlayers[seatNum] = playerToSeat
        return seatNum
    
    def unSeatPlayer(self, playerToUnSeat):
        openSeatNum=playerToUnSeat.seatNum
        self.seatedPlayers.pop(openSeatNum)
        self.openSeatNums.append(openSeatNum)
        pass
    
    def removePlayerFromTable(self, playerToRemove):
        if playerToRemove.seated:
            playerToRemove.standUp()
        newPlayerList = [p for p in self.players if not p.usrId == playerToRemove.usrId]
        self.players = newPlayerList
        
    def clearPlayerHands(self):
        for seatnum in self.seatedPlayers.keys():
            self.seatedPlayers[seatnum].clearHand()
    
    def resetRound(self):
        print("New Betting Round")
        self.bettingRound=0
        if(len(self.occupiedSeatNums))<self.MINPLAYERS:
            print("Need at least 3 seated players to start")
            return
        self.numHands+=1
        self.clearPlayerHands()
        self.moveBtton()
        print("Button is at seat Number: "+str(self.buttonSeatNum))
        self.deck.repopulate()
        self.deck.shuffle()
        pot=Pot(self)
        self.pots.append(pot)
        self.getAntes(pot)
        return pot
   
    def getAntes(self, pot):
        smallPlayer = self.seatedPlayers[self.smallSeatNum]
        bigPlayer = self.seatedPlayers[self.bigSeatNum]
        smallPlayer.Raise(Table.BLINDS[0], pot)
        bigPlayer.Raise(Table.BLINDS[1], pot)   
         
    def deal(self):
        cur_player = self.seatedPlayers[self.smallSeatNum]
        for _ in range(2):
            for _ in range(len(self.seatedPlayers)):
                card = self.deck.deal(1)[0]
                cur_player.addCardToHand(card)
                cur_player = self.getNextSeatedPlayer(cur_player)
        self.printPlayerHands()
        
    def beginBetting(self, pot):
        self.bettingRound+=1
        if self.bettingRound == 1:
            self.actionToSeatNum = self.getNextSeatNum(self.bigSeatNum) #bet starts to left of Big blind
        else:
            self.actionToSeatNum = self.getNextSeatNum(self.buttonSeatNum) #bet starts to left of button
        while pot.actionRemains:
            bettingPlayer = self.seatedPlayers[self.actionToSeatNum]
                bettingPlayer.getAction(self, pot)
                # Do other stuff
            self.actionToSeatNum = self.getNextSeatNum(self.actionToSeatNum)
        print("Betting round complete")
        return
                
    def printPlayerHands(self):
        for _, player in self.seatedPlayers.items():
            print("Player "+player.playname+" hand is "+str(player.humanReadableHand))
            
    def moveBtton(self):
        self.buttonSeatNum = self.getNextSeatNum(self.buttonSeatNum)
        self.smallSeatNum = self.getNextSeatNum(self.buttonSeatNum)
        self.bigSeatNum = self.getNextSeatNum(self.bigSeatNum)
        pass

    ## Get the player to the left of the current player
    def getNextSeatedPlayer(self, cur_player):
        cur_seat_num = cur_player.seatNum
        nextSeatNum = self.getNextSeatNum(cur_seat_num)
        return self.seatedPlayers[nextSeatNum]  
    
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
        nextSeatNum = self.getNextSeatNum(cur_seat_num)
        return self.seatedPlayers[nextSeatNum]  
    
    ## Get the seat number to the right of the current seat nujmber    
    def getPrevSeatNum(self, cur_seat_num):
        cur_seat_idx = self.occupiedSeatNums.index(cur_seat_num)
        if cur_seat_idx == len(self.occupiedSeatNums)-1:
            cur_seat_idx = 0
        else:
            cur_seat_idx+=1
        return self.occupiedSeatNums[cur_seat_idx]
      
    def __str__(self):
        resp = "Table online is "+str(self.online)+" Players are "+str([p.playname for p in self.players])
        resp+="\n\n Open Seat nums"+str(self.openSeatNums)
        resp+="\nseated players:\n"
        for k,v in self.seatedPlayers.items():
            resp+=str(k)+str(v.playname)+'\n'
        return resp
    

