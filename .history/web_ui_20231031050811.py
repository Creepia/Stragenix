# 导入flask模块
from flask import Flask, render_template, request, flash
# 导入talib模块
import talib as tal
# 导入numpy模块
import numpy as np
import AutoTestback as atb

# 创建一个flask应用对象
app = Flask(__name__)
# 设置一个密钥，用于消息闪现
app.secret_key = "flask"


# 定义一个函数，用于执行RUN_FOLDER函数
def RUN_FOLDER(folder,get_indicator_func=atb.getIndicators,initial_cash=1000000,output_folder="Conclusion"):
    TestBack=atb.TestBackModel()
    SG=atb.SignalGeneartor()
    for name,decifunc in SG.NextDecision():
        TestBack.run_folder(
            folder=folder,
            save_log=f"{folder}/{name}",
            signal_func_name=name,
            get_indicator_func=atb.getIndicators,
            get_signal_func=decifunc,
            initial_cash=1000000,
            output_folder="Conclusion"
            )

# 定义一个路由，用于显示主页面
@app.route("/")
def index():
    # 渲染index.html模板，传入一些默认参数
    return render_template("index.html", folder="data", output_folder="Conclusion", initial_cash="1000000", get_indicator_func=atb.getIndicators.__code__)

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
