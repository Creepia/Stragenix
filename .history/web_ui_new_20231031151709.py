from flask import Flask, render_template, request, current_app
from flask_socketio import SocketIO, join_room
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "scrtk"
socketio = SocketIO(app)

@app.route('/lobby')
def lobby():
    return render_template('lobby.html')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("newQuestion")
def newQuestion(room_id):
    start_time = time.time()

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000,debug=1)
