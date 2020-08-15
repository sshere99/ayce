
from flask import Flask, render_template
from flask_socketio import SocketIO
import pktypes
from pktypes import *
from pkhands import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('session3.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)
    
@socketio.on('start pause')
def handle_start_game_event(json, methods=['GET', 'POST']):
    print('received start request: ' + str(json))
    print(json.keys())
    f={'user_name':'yeas', 'message':'yup'}
    socketio.emit('get card resp', f, callback=messageReceived)
    
def seat_players():
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
    return t

    
if __name__ == '__main__':
    socketio.run(app, debug=True)