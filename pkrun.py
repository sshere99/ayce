
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
tables = ['table1','table2','table3']

print("STARTING SERVER!!!!!!!")

@app.route('/')
def sessions():
    return render_template('session3.html')

@app.route('/<tableURI>')
def table(tableURI):
    print(tableURI)
    if tableURI in tables:
        return render_template('session3.html', tableURI=tableURI)
    else:
        return render_template('err.html')
    
@socketio.on('connect')
def handle_connect():
    connected = True
    print('Client connected'+' ID IS: '+str(request.sid))
    #send_message_to_client(request.sid, 'Connected to server please join table')
    clients.append(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)

@socketio.on('join')
def on_join(data):
    room_ID = data['urname']
    user_ID = data['urname']
    print(data)
    tableID=data['tabId']
    join_room(room_ID)
    seat_user(room_ID, user_ID, tableID)
    #send_message_to_room(room_ID, str(room_ID)+'joined the table'+str(tableID))
    #send(username + ' has entered the room.', channel=channel)

def seat_user(room_id, user_ID, tableID):
    #player = get_player_by_id(user_ID)
    data=room_id
    socketio.emit('seat_user', data, room=room_id)
              
def send_message_to_room(room_id, data):
    socketio.emit('output', data, room=room_id)
    
def send_message_to_client(client_id, data):
    socketio.emit('output', data, room=client_id)  
    
@socketio.on('start pause')
def handle_start_game_event(json, methods=['GET', 'POST']):
    tab_state = str(json['message'])
    print('received start request: ' + tab_state +' ID IS: '+str(request.sid))
    print('\n\n\n\n\n\n\n\n\n\n STATE '+tab_state)
    if tab_state=='online':
        socketio.emit('online', 'ONLINE', broadcast=True)
        run_game(request.sid)
    elif tab_state=='pause':
        pause_game()
    else:
        end_game()
    ##socketio.emit('my response', json, callback=messageReceived)
    
@socketio.on('sit stand')
def handle_stand(json, methods=['GET', 'POST']):
    print('received STAND REQUEST')
    print(json.keys())
    ##socketio.emit('my response', json, callback=messageReceived)
    
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
    
def pause_game():
    print("\n\n\n\nPAUSING")
    socketio.emit('output', 'PAUSE')
    
def end_game():
    print("\n\n\n\nENDING")
    socketio.emit('output', 'END')
    
def run_game(client_id):
    #create Table
    t = Table(10)
    joe = Player('Joe_', 'Joe', bank=44, stack=500)
    fred = Player('Fred_', 'Fred', bank=44, stack=100)
    willis = Player('Willis_', 'willis', bank=44, stack=1000)
    sally = Player('Sally_', 'Sally', bank=44, stack=1800)
    lucy = Player('Lucy_', 'Lucy', bank=44, stack=1600)
    patty = Player('Patty_', 'Patty', bank=44, stack=1000)

    t.addPlayerToLobby(joe)
    t.addPlayerToLobby(fred)
    t.addPlayerToLobby(willis)
    t.addPlayerToLobby(sally)
    t.addPlayerToLobby(lucy)
    t.addPlayerToLobby(patty)

    for player in t.playersInLobby:
        player.sitDown()

    t.socketio = socketio
    t.startGame()
    pot, small, big = t.startNewHand()
    
    
if __name__ == '__main__':
    socketio.run(app, debug=True)