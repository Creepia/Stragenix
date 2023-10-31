from flask import Flask, render_template, request
from flask_socketio import SocketIO
import talib as tal
import numpy as np
import AutoTestback as atb

app = Flask(__name__)
app.config["SECRET_KEY"] = "scrtk"
socketio = SocketIO(app)

DEFAULT_INDI_FUNC="""def getIndicators(df):
    df["RSI"] = tal.RSI(df["Close"])
    df["SMA"] = tal.SMA(df["Close"])
    df["SAR"] = tal.SAR(df["High"], df["Low"], 0.02, 0.2)
    df["WPR"] = get_WPR(df["High"], df["Low"], df["Close"], 14)
    df["CCI"] = tal.CCI(df["High"], df["Low"], df["Close"], 20)
    df["ADX"] = tal.ADX(df["High"], df["Low"], df["Close"])
    _, _, df["MACD"] = tal.MACD(df["Close"], fastperiod=10, slowperiod=20, signalperiod=9)
    df=get_KD(df,window=14,k=3,d=2)
    df["-DI"]=tal.MINUS_DI(df["High"], df["Low"], df["Close"], timeperiod=14)
    df["+DI"]=tal.MINUS_DI(df["High"], df["Low"], df["Close"], timeperiod=14)
    df["ADXR"]=tal.ADXR(df["High"], df["Low"], df["Close"], timeperiod=14)
    df["MFI"]=tal.MFI(df["High"], df["Low"], df["Close"],df["Volume"] ,timeperiod=14)
    df["EMA"]=tal.EMA(np.array(df["Close"]), timeperiod = 6)
    df=get_RVI(df,n=10)
    df["OBV"] = tal.OBV(df["Close"], df['Volume'])
    return df
"""

@app.route('/')
def index():
    return render_template("index.html", folder="data", output_folder="Conclusion", initial_cash="1000000", get_indicator_func=DEFAULT_INDI_FUNC)

@socketio.on("updateIndicators")
def updateIndicators(data):
    print(data)
    exec(data)
    return {"success":True}

@socketio.on("updateSignals")
def updateSignalFunctions(data):
    print(data)
    return {"success":True}

@socketio.on("/doAutoTestBack")
def doAutoTestBack(data):
    print(data)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000,debug=1)
