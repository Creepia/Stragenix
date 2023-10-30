# 导入flask模块
from flask import Flask, render_template, request, flash
# 导入talib模块
import talib as tal
# 导入numpy模块
import numpy as np
from . import AutoTestback

# 创建一个flask应用对象
app = Flask(__name__)
# 设置一个密钥，用于消息闪现
app.secret_key = "flask"

# 定义一个函数，用于计算指标
def getIndicators(df):
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

# 定义一个函数，用于执行RUN_FOLDER函数
def RUN_FOLDER(folder,get_indicator_func=getIndicators,get_signal_func=deci_func,initial_cash=1000000,output_folder="Conclusion"):
    # 这里省略了具体的实现细节，你可以根据你的需求编写代码
    pass

# 定义一个路由，用于显示主页面
@app.route("/")
def index():
    # 渲染index.html模板，传入一些默认参数
    return render_template("index.html", folder="data", output_folder="Conclusion", initial_cash="1000000", get_indicator_func=getIndicators.__code__, get_signal_func=deci_func.__code__)

# 定义一个路由，用于处理表单提交
@app.route("/submit", methods=["POST"])
def submit():
    # 获取表单中的参数
    folder = request.form.get("folder")
    output_folder = request.form.get("output_folder")
    initial_cash = request.form.get("initial_cash")
    get_indicator_func = request.form.get("get_indicator_func")
    get_signal_func = request.form.get("get_signal_func")

    # 检查参数是否合法，如果不合法，返回错误信息并闪现消息
    if not folder or not output_folder or not initial_cash or not get_indicator_func or not get_signal_func:
        flash("请填写所有参数")
        return render_template("index.html", folder=folder, output_folder=output_folder, initial_cash=initial_cash, get_indicator_func=get_indicator_func, get_signal_func=get_signal_func)

    try:
        # 将字符串转换为函数对象
        get_indicator_func = eval(get_indicator_func)
        get_signal_func = eval(get_signal_func)

        # 调用RUN_FOLDER函数，并获取结果
        result = RUN_FOLDER(folder,get_indicator_func,get_signal_func,int(initial_cash),output_folder)

        # 返回结果页面，并传入结果参数
        return render_template("result.html", result=result)

    except Exception as e:
        # 如果发生异常，返回错误信息并闪现消息
        flash(str(e))
        return render_template("index.html", folder=folder, output_folder=output_folder, initial_cash=initial_cash, get_indicator_func=get_indicator_func, get_signal_func=get_signal_func)

# 运行flask应用
if __name__ == "__main__":
    app.run(debug=True)
