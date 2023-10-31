import os
import talib as tal
import random
import numpy as np
import pandas as pd
random.seed(42)
np.random.seed(42)


"""def get_Signal(RSI,SMA,SAR,WPR,CCI,AXD,MACD,model_path):
    model=tf.keras.models.load_model(model_path)
    test_x=pd.concat(RSI,SMA,SAR,WPR,CCI,AXD,MACD)
    for i in test_x:
        test_x[i]=test_x[i]/(test_x[i].max())
    test_x=np.reshape(test_x,test_x.shape+(1,))
    Trend=model.predict(test_x)
    Signal=pd.DataFrame(np.zeros(RSI.shape[0]))
    hasShare=0
    for i in range(RSI.shape[0]):
        # if tomorrow will up, then buy.
        if(Trend[i]==1 and hasShare==0):
            Signal[i]=1
            hasShare=1
        elif(Trend[i]==0 and hasShare==1):
            Signal[i]=2
            hasShare=0
    return Signal"""


def append_df(df, A, ignore_index=True):
    try:
        if (df.empty):
            return A
        elif (A.empty):
            return None
        else:
            return pd.concat([df, A], ignore_index=ignore_index)
    except:
        return pd.DataFrame()


# When you want to check the data after adding the indicators, you may check this variable.
debug_df=pd.DataFrame()
class TestBackModel():
    def __init__(self):
        self.backtest = pd.DataFrame()
        self.diff_list = []
        self.win_rate = 0
        self._name = "test_data"
        self.total_returns = 0
        self._signal_func_name=""

    def setBuySignals(self, df: pd.DataFrame,get_indicator_func,get_signal_func,drop_na=True):
        """
        This method will apply the indicators for df. Then set self.buy_signals as the df with only Date,Close,Signal columns.
        """
        df = self.apply_indicators_and_signal_for_data(df,get_indicator_func,get_signal_func)
        if (drop_na):
            df = df.dropna()
            df = df.reset_index(drop=True)
        global debug_df
        debug_df=df
        self.buy_signals = pd.DataFrame(df.loc[:, ["Date", "Close", "Signal"]])

    def setName(self, name: str):
        self._name = name
    def setSignalFunctionName(self, name: str):
        self._signal_func_name = name

    def setBuySignals_csv(self, filepath: str,get_indicator_func,get_signal_func, drop_na=True):
        df = pd.read_csv(filepath)
        self.setBuySignals(df=df,get_indicator_func=get_indicator_func,get_signal_func=get_signal_func,drop_na=drop_na)

    def run(self ,initial_cash=1000000,save_log=""):
        try:
            shares = 0
            position = "Hold"     # 当前仓位，默认为持仓
            equity = initial_cash  # 初始资产等于初始资金
            # 遍历每一行买入信号数据
            for _, row in self.buy_signals.iterrows():
                date = row['Date']
                close = row['Close']
                signal = row['Signal']

                if signal == 1 and shares == 0:
                    # 买入操作
                    position = "Buy"
                    shares += equity / close  # 计算可买入的股票数量
                    equity = 0  # 资金置为0，全仓买入
                elif signal == 2 and shares > 0:
                    # 卖出操作
                    position = "Sell"
                    equity += shares * close
                    shares = 0  # 持有股票数量置为0
                else:
                    position = ""
                # 将回测结果添加到数据框中
                self.backtest_row = pd.DataFrame(
                    {'Date': date, 'Close': close, 'Signal': signal, 'Position': position, 'Equity': equity}, index=[0])
                self.backtest = append_df(self.backtest, self.backtest_row)

            col_list = list(self.backtest['Equity']
                            [self.backtest['Equity'] != 0])
            col_list = [float(x) for x in col_list]
            clean_list = [col_list[0]] + [col_list[i]
                                        for i in range(1, len(col_list)) if col_list[i] != col_list[i-1]]
            self.diff_list = [clean_list[i+1] - clean_list[i]
                            for i in range(len(clean_list)-1)]
            # print([x > 0 for x in self.diff_list],self.diff_list)
            self.win_rate = sum([x > 0 for x in self.diff_list]) / len(self.diff_list)
            equity_series = self.backtest['Equity']
            last_equity = equity_series.iloc[-1]
            if last_equity == 0:
                # 循环向前查找直到找到一个非零值
                for i in range(len(equity_series) - 2, -1, -1):
                    if equity_series.iloc[i] != 0:
                        last_equity = equity_series.iloc[i]
                        break
            self.total_returns = (last_equity - initial_cash) / initial_cash
            output_data = pd.DataFrame({'backtest_length': len(self.backtest), 'diff_list_length': len(self.diff_list), 'total_returns': self.total_returns, 'win_rate': self.win_rate}, index=[self._name])
            print("Ran the backtest.")
            if(save_log):
                self.save_log(save_log)
            return (output_data)
        except Exception as e:
            print(f"{self._name} running with a error: {e}")
            return (pd.DataFrame({'backtest_length': None, 'diff_list_length': None, 'total_returns': None, 'win_rate': None}, index=[self._name]))

    def run_folder(self, folder: str, get_indicator_func,get_signal_func,signal_func_name="",initial_cash=1000000, drop_na=True,save_log="",print_output=True,output_folder="Conclusion"):
        self.setSignalFunctionName(signal_func_name)
        output=pd.DataFrame({'backtest_length': None, 'diff_list_length': None, 'total_returns': None, 'win_rate': None}, index=[""])
        if not os.path.exists(output_folder+"/"+folder):
            os.mkdir(output_folder+"/"+folder)
        output.to_csv(output_folder+"/"+folder+"/total_output_"+self._signal_func_name+".csv",mode="w")
        for file_path in os.listdir(folder):
            if ("output" in file_path) or file_path[-11:]=="_result.csv" or file_path[-4:]!=".csv":
                continue
            filepath = folder + "/" + file_path
            self.setName(file_path[:-4])
            print(f"Runnning {self._name} with {self._signal_func_name}")
            try:
                self.setBuySignals_csv(filepath, get_indicator_func,get_signal_func,drop_na)
                output=self.run(initial_cash=initial_cash,save_log=save_log)
                output.to_csv(output_folder+"/"+folder+"total_output_"+self._signal_func_name+".csv",mode="a",header=False)
                if print_output:
                    print(output)
            except Exception as e:
                print(e)
                print("Error at running the dataframe,Skip.")
            self.backtest=None
            print("====================")

    def save_log(self, folder_name):
        try:
            if (not os.path.exists(folder_name)):
                os.makedirs(folder_name)
            self.backtest.to_csv(folder_name+"/"+self._name+"_result_"+self._signal_func_name+".csv", index=False, mode="w")
            print("Output is Saved.")
        except Exception as e:
            print(f"{self._name} saving with a error: {e}")

    def apply_indicators_for_data(self,df,get_indicator_func):
        if(df.empty):
            print("Cannot find data thus failed at applying indicators")
            return df
        elif ("Close" in df):
            df=get_indicator_func(df)
        else:
            print("Cannot find data thus failed at applying indicators")
        return df
    
    def apply_signal_for_data(self,df,get_signal_func):
        if("Close" in df):
            df["Signal"]=0
            df=get_signal_func(df)
            return df

    def apply_indicators_and_signal_for_data(self,df,get_indicator_func,get_signal_func):
        """
        Parameters
        -----
        get_indicator_func\n
        get_signal_func
        The two functions both returns a complete DataFrame
        """
        df=self.apply_indicators_for_data(df=df,get_indicator_func=get_indicator_func)
        df=self.apply_signal_for_data(df=df,get_signal_func=get_signal_func)
        return df

class SignalGeneartor():
    def __init__(self, decisions={}):
        """
        decisions {str:function}.
        eg. {"RSI":get_RSI}
        """
        self.decisions = decisions

    def addDecisions(self, decisions={}):
        self.decisions = {**self.decisions, **decisions}

    def getDecisions(self):
        return self.decisions
    
    def NextDecision(self):
        for name,func in self.getDecisions().items():
            yield (name,func)


def get_WPR(High, Low, Close, n):
    H_n = High.rolling(n).max()
    L_n = Low.rolling(n).min()
    return (H_n-Close)/(H_n-L_n) * 100

def get_KD(data, window=14, k=3, d=3):
    # Calculate %K
    data['L14'] = data['Low'].rolling(window=window).min()
    data['H14'] = data['High'].rolling(window=window).max()
    data['%K'] = 100*((data['Close'] - data['L14']) / (data['H14'] - data['L14']))
    # Calculate %D
    data['%D'] = data['%K'].rolling(window=d).mean()
    return data

def get_RVI(df, n=10):
    # Calculate RVI numerator
    df['RVI_Numerator'] = (df['Close'] - df['Open']) / (df['High'] - df['Low'])
    # Calculate N period SMA for RVI
    df['RVI_SMA'] = df['RVI_Numerator'].rolling(window=n).mean()
    return df

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

def RANDOM(df):
    df['Signal'] = pd.DataFrame(np.random.randint(0,3,size=(df.shape[0],1)))
    return df

def MACD(df):
    MACD=df["MACD"]
    Signal = pd.DataFrame(np.zeros(MACD.shape[0]))

    Signal[MACD < 0] = 1  # buy
    Signal[MACD > 0] = 2  # sell

    df["Signal"]=Signal
    return df

def RSI(df,perc=30):
    RSI=df["RSI"]
    Signal=pd.DataFrame(np.zeros(RSI.shape[0]))
    Signal[RSI<perc]=1 # buy
    Signal[RSI>100-perc]=2 # sell
    df["Signal"]=Signal
    return df

def EMA(df):
    EMA=df["EMA"]
    Close=df["Close"]
    Signal=pd.DataFrame(np.zeros(EMA.shape[0]))
    Signal[Close<EMA]=1
    Signal[Close>EMA]=2
    df["Signal"]=Signal
    return df

def SMA(df):
    SMA=df["SMA"]
    Close=df["Close"]
    Signal=pd.DataFrame(np.zeros(SMA.shape[0]))
    Signal[Close<SMA]=1
    Signal[Close>SMA]=2
    df["Signal"]=Signal
    return df

def MFI(df,perc=20):
    MFI=df["MFI"]
    Signal=pd.DataFrame(np.zeros(MFI.shape[0]))
    Signal[MFI<perc]=1 # buy
    Signal[MFI>100-perc]=2 # sell
    df["Signal"]=Signal
    return df

def AND_Indicator(*indi_funcs):
    def AND(df):
        sigs=[indi_func(df.copy())["Signal"] for indi_func in indi_funcs]
        Signal=pd.DataFrame(np.zeros(df.shape[0]))
        # the i_th row
        for i in range(df.shape[0]):
            # pivot is the first signal of the first indicator
            pivot=0 if sigs[0].iloc[i]==0 else sigs[0].iloc[i]
            # the j_th indicator
            for j in range(1,len(sigs)):
                if sigs[j].iloc[i]!=pivot:
                    pivot=0
                    break
            Signal.iloc[i]=pivot
        df["Signal"]=Signal
        return df
    return AND
