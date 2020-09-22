
from flask import Flask, render_template, jsonify
from flask import request
from flask_socketio import SocketIO, join_room, leave_room
import pktypes
from pktypes import *
from pkhands import *
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
connected = False
clients = []
t1 = Table(10)
t2 = Table(10)
t3 = Table(10)
tables = {'table1':t1,'table2':t2,'table3':t3}

Joe_ = Player('Joe_', 'Joe', bank=44, stack=500)
Fred_ = Player('Fred_', 'Fred', bank=44, stack=100)
Willis_ = Player('Willis_', 'willis', bank=44, stack=1000)
Sally_ = Player('Sally_', 'Sally', bank=44, stack=1800)
Lucy_ = Player('Lucy_', 'Lucy', bank=44, stack=1600)
Patty_ = Player('Patty_', 'Patty', bank=44, stack=1000)
players = {'Joe_':Joe_, 'Sally':Sally_, 'Fred_':Fred_, 'Willis_':Willis_, 'Patty_':Patty_}

print("STARTING SERVER!!!!!!!")

@app.route('/')
def sessions():
    return render_template('session3.html')

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

def seat_user(user_ID, tableID):
    if user_ID in players.keys():
        player = players[user_ID]
        t = tables[tableID]
        t.addPlayerToLobby(Joe_)
        socketio.emit('seat_user', user_ID, room=user_ID)
    else:
        socketio.emit('output_alert', 'USER ID NOT RECOGNIZED', room=user_ID)
              
def send_message_to_room(tableID, data):
    socketio.emit('output', data, room=room_id)
    
def send_message_to_client(usrID, data):
    socketio.emit('output', data, room=usrID)  
    
@socketio.on('start pause')
def handle_start_game_event(json, methods=['GET', 'POST']):
    tab_state = str(json['message'])
    tblID = str(json['tbl'])
    print('received table state request: ' + tab_state +' ID IS: '+str(tblID))
    t = tables[tblID]
    if tab_state=='online':
        t.online = True
        socketio.emit('online', 'ONLINE', room=tblID)
        run_game(request.sid, t)
    elif tab_state=='pause':
        t.online = True
        t.paused = True
        socketio.emit('online', 'PAUSE', room=tblID)
    elif tab_state=='deal':
        t.online = True
        t.paused = False
        socketio.emit('online', 'DEAL', room=tblID)          
    else:
        t.online = False
        t.paused = True
        socketio.emit('output', 'OFFLINE', room=tblID)
    
@socketio.on('sit stand')
def handle_stand(json, methods=['GET', 'POST']):
    print('received STAND REQUEST')
    print(json.keys())
    ##socketio.emit('my response', json, callback=messageReceived)
    
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
    
def run_game(client_id, t):
    t.addPlayerToLobby(Joe_)
    t.addPlayerToLobby(Fred_)
    t.addPlayerToLobby(Willis_)

    for player in t.playersInLobby:
        player.sitDown()

    t.socketio = socketio
    t.startGame()
    pot, small, big = t.startNewHand()
    
    
if __name__ == '__main__':
    socketio.run(app, debug=True)