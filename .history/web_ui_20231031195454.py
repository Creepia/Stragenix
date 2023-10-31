from flask import Flask, render_template
from flask_socketio import SocketIO
import talib as tal
import numpy as np
np.random.seed(42)
import AutoTestback as atb
import Conclude as cc

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

DEFAULT_SIGN_DICT="""signDict={
    "Random":atb.RANDOM
}"""
signDict={
    "Random":atb.RANDOM
}

def getIndicators(df):
    return atb.getIndicators(df)

def getSignDict():
    global signDict
    return signDict
@app.route('/')
def index():
    return render_template("TestBack.html", folder="Test", output_folder="Conclusion", initial_cash="1000000", get_indicator_func=DEFAULT_INDI_FUNC,get_signal_dict=DEFAULT_SIGN_DICT)

@app.route('/Conclude')
def Conclude():
    return render_template("Conclude.html", folder="Conclude")

@app.route('/Visualization')
def Visualization():
    return render_template("Visualization.html", folder="Test", output_folder="Conclusion", initial_cash="1000000", get_indicator_func=DEFAULT_INDI_FUNC)

@socketio.on("updateIndicatorsFunctions")
def updateIndicatorsFunctions(data):
    print(data)
    exec(data)
    return {"success":True}

@socketio.on("updateSignalsDictionary")
def updateSignalsFunctions(data):
    print(data)
    exec(data)
    return {"success":True}

@socketio.on("doAutoTestBack")
def doAutoTestBack(data):
    # print("doing auto test back...")
    TestBack=atb.TestBackModel()
    SG=atb.SignalGeneartor()
    SG.addDecisions(signDict)
    folder=data["folder"]
    for name,decifunc in SG.NextDecision():
        TestBack.run_folder(
            folder=folder,
            save_log=f"{folder}/{name}",
            signal_func_name=name,
            get_indicator_func=getIndicators,
            get_signal_func=decifunc,
            initial_cash=int(data["initial_cash"]),
            output_folder=data["output_folder"]
            )
    return {"success":True}

@socketio.on("doConclude")
def doConclude(data):
    CD=cc.Concluder(data["folder"])
    CD.readFolder()
    return {"success":True}

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000,debug=1)
