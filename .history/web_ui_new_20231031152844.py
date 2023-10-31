from flask import Flask, render_template, request
from flask_socketio import SocketIO
import talib as tal
import numpy as np
import AutoTestback as atb

app = Flask(__name__)
app.config["SECRET_KEY"] = "scrtk"
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("newQuestion")
def newQuestion(room_id):
    pass

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000,debug=1)
