
from flask import Flask, render_template
from flask import request
from flask_socketio import SocketIO
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

print("STARTING SERVER!!!!!!!")

@app.route('/')
def sessions():
    return render_template('session3.html')
    
@socketio.on('connect')
def handle_connect():
    connected = True
    print('Client connected'+' ID IS: '+str(request.sid))
    send_message(request.sid, 'pankaj')
    clients.append(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)

def send_message(client_id, data):
    socketio.emit('output', data, room=client_id)
    print('sending message "{}" to client "{}".'.format(data, client_id))   

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json)+' from client '+str(request.sid))
    socketio.emit('my response', json, callback=messageReceived)
    
@socketio.on('start pause')
def handle_start_game_event(json, methods=['GET', 'POST']):
    print('received start request: ' + str(json)+' ID IS: '+str(request.sid))
    print(json.keys())
    #f={'user_name':'yeas', 'message':'yup'}
    #socketio.emit('get card resp', f, callback=messageReceived)
    #print("DO SOME MORE STUFF")
    #t=create_table()
    #socketio.emit('output', t.__str__(), callback=messageReceived)
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
    
    
    
if __name__ == '__main__':
    socketio.run(app, debug=True)