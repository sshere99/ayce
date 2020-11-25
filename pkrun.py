
from flask import Flask, render_template, jsonify
from flask import request
from flask_socketio import SocketIO, join_room, leave_room
import pktypes
from flask_cors import CORS
from pktypes import *
from pkhands import *
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
CORS(app, resources={r'/*': {'origins': '*'}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

socketio = SocketIO(app, cors_allowed_origins="*")
#socketio = SocketIO(app)
connected = False
clients = []
t1 = Table(10)
t2 = Table(10)
t3 = Table(10)
t1.socketio = socketio
t2.socketio = socketio
t3.socketio = socketio
tables = {'table1':t1,'table2':t2,'table3':t3}

Joe_ = Player('Joe_', 'Joe_', bank=44, stack=500)
Fred_ = Player('Fred_', 'Fred_', bank=44, stack=100)
Willis_ = Player('Willis_', 'Willis_', bank=44, stack=1000)
Sally_ = Player('Sally_', 'Sally_', bank=44, stack=1800)
Lucy_ = Player('Lucy_', 'Lucy_', bank=44, stack=1600)
Patty_ = Player('Patty_', 'Patty_', bank=44, stack=1000)
players = {'Joe_':Joe_, 'Sally_':Sally_, 'Fred_':Fred_, 'Willis_':Willis_, 'Patty_':Patty_}

rooms = [{'actions': {'bet': False, 'check': False},
  'amount': 0,
  'dealer': False,
  'noOfPlayers': 0,
  'online': True,
  'options': {'amount': 20000, 'bigBlind': 10, 'smallBlind': 5},
  'players': [],
  'tableID': 'Poker table 1',
  'tablePot': 0}]


print("STARTING SERVER!!!!!!!")

@app.route('/')
def sessions():
    return render_template('session3.html')

@app.route('/admin')
def admin():
    return "Hi"

@app.route('/<tableURI>')
def table(tableURI):
    if tableURI in tables:
        return render_template('session3.html', tableURI=tableURI)
    else:
        return render_template('err.html')
    
@socketio.on('connect')
def handle_connect():
    connected = True
    print('Client connected'+' ID IS: '+str(request.sid))
    tbl = str(request.args.get('tbl'))
    print(tbl)
    join_room(tbl.strip('/'))
    clients.append(request.sid)
    socketio.emit('rooms', rooms)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)

@socketio.on('join')
def on_join(data):
    user_ID = data['urname']
    print('\n\n\n\n CID'+str(request.sid))
    tableID=data['tabId']
    join_room(user_ID)
    seat_user(user_ID, tableID)
    
@socketio.on('joinTable')
def on_join_vue(data):
    print("CONNECTED")
    socketio.emit('joined', rooms[0])

def seat_user(user_ID, tableID):
    if user_ID in players.keys():
        player = players[user_ID]
        t = tables[tableID]
        t.addPlayerToLobby(player)
        player.sitDown()
        socketio.emit('seat_user', user_ID, room=user_ID)
        plyrs=[p.playname for p in t.seatedPlayers]
        socketio.emit('output', 'Seated Players:\n'+str(plyrs), room=tableID)
        socketio.emit('add_user_to_table', {'usrnam':user_ID, 'seatnum':player.seatNum}, room=tableID)
    else:
        socketio.emit('output_alert', 'USER ID NOT RECOGNIZED', room=user_ID)
              
@socketio.on('start pause')
def handle_start_game_event(json, methods=['GET', 'POST']):
    tab_state = str(json['message'])
    tblID = str(json['tbl'])
    print('received table state request: ' + tab_state +' ID IS: '+str(tblID))
    t = tables[tblID]
    if tab_state=='online':
        t.online = True
        t.paused = True
        socketio.emit('online', 'ONLINE', room=tblID)
    elif tab_state=='pause':
        t.online = True
        t.paused = True
        socketio.emit('online', 'PAUSE', room=tblID)
    elif tab_state=='deal':
        t.online = True
        t.paused = False
        socketio.emit('online', 'DEAL', room=tblID) 
        run_game(request.sid, t)
    else:
        t.online = False
        t.paused = True
        socketio.emit('offline', 'OFFLINE', room=tblID)
    
@socketio.on('sit stand')
def handle_stand(json, methods=['GET', 'POST']):
    print('received STAND REQUEST')
    print(json.keys())
    ##socketio.emit('my response', json, callback=messageReceived)
    
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
    
def run_game(client_id, t):
    while t.online and not t.paused:
        t.startGame()
        if not t.paused:
            pot, small, big = t.startNewHand()
            t.pushTableState()
            t.paused = True
    
    
if __name__ == '__main__':
    socketio.run(app, debug=True)