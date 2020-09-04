
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
tables = []

print("STARTING SERVER!!!!!!!")

@app.route('/')
def sessions():
    return render_template('session3.html')
    
@socketio.on('connect')
def handle_connect():
    connected = True
    print('Client connected'+' ID IS: '+str(request.sid))
    send_message_to_client(request.sid, 'Connected to server please join table')
    clients.append(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)

@socketio.on('join')
def on_join(data):
    username = data['username']
    tableId = data['tableId']
    join_room(tableId)
    send_message_to_room(tableId, str(username)+'joined the table'+str(tableId))
    #send(username + ' has entered the room.', channel=channel)
    
def send_message_to_client(client_id, data):
    socketio.emit('output', data, room=client_id)  

def send_message_to_room(room_id, data):
    socketio.emit('output', data, room=room_id)

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json)+' from client '+str(request.sid))
    socketio.emit('my response', json, callback=messageReceived)
    
@socketio.on('start pause')
def handle_start_game_event(json, methods=['GET', 'POST']):
    print('received start request: ' + str(json)+' ID IS: '+str(request.sid))
    print(json.keys())
    run_game(request.sid)
    
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
    
def run_game(client_id):
    #create Table
    t = Table(10)
    joe = Player('sdff', 'Joe', bank=44, stack=500)
    fred = Player('sdf2', 'Fred', bank=44, stack=100)
    willis = Player('sdf3', 'willis', bank=44, stack=1000)
    sally = Player('sdf9', 'Sally', bank=44, stack=1800)
    lucy = Player('sdf8', 'Lucy', bank=44, stack=1600)
    patty = Player('sdf7', 'Patty', bank=44, stack=1000)

    t.addPlayerToLobby(joe)
    t.addPlayerToLobby(fred)
    t.addPlayerToLobby(willis)
    t.addPlayerToLobby(sally)
    t.addPlayerToLobby(lucy)
    t.addPlayerToLobby(patty)

    for player in t.playersInLobby:
        player.sitDown()
    
    rsp = {'val1': 'test stuff branch v2', 
           'box1': myd['8s']+myd['8s']+pTxt('chec'), 
           'box2': myd['facedown']+pTxt('check10'),
           'box4': myd['facedown']+pTxt('check2'),
          }
    socketio.emit('table_state', rsp, callback=messageReceived)
    t.startGame()
    pot, small, big = t.startNewHand(socketio)
    
    
if __name__ == '__main__':
    socketio.run(app, debug=True)