import pandas as pd
import numpy as np
import os

class Concluder():
    """
    One class for a folder, eg visualization.
    One dataset can be, eg. nasdaq.
    One file is a file of a sigle strategy.
    """
    def __init__(self,folder:str):
        self.folder=folder
        self.dataset_name=""
        self.file_name=""
        self.df=None
    def readData(self,data:pd.DataFrame):
        newline=pd.DataFrame(columns=["total_trading_times","avg_trading_times","avg_win_rate","avg_return_rate"],index=[self.file_name[13:-4] if self.file_name[:13]=="total_output_" else ""])
        newline["total_trading_times"]=data["diff_list_length"].sum()
        newline["avg_trading_times"]=data["diff_list_length"].mean()
        newline["avg_win_rate"]=(data["win_rate"]*data["diff_list_length"]/data["diff_list_length"]).mean()
        newline["avg_return_rate"]=(data["total_returns"]*data["diff_list_length"]/data["diff_list_length"]).mean()
        self.df=pd.concat([self.df,newline])
    def readFile(self,file):
        data=pd.read_csv(file)
        self.readData(data)
    def readDataSet(self,dataset):
        self.dataset_name=dataset
        for file in os.listdir(self.folder+"/"+self.dataset_name):
            if file[-4:]==".csv":
                self.file_name=file
                print("reading ",self.dataset_name+"/"+file)
                self.readFile(self.folder+"/"+self.dataset_name+"/"+file)
    def readFolder(self):
        for dataset in os.listdir(self.folder):
            self.df=None
            if dataset=="output":
                continue
            print("In folder ",dataset)
            self.readDataSet(dataset)
            self.save()
    def save(self):
        if (not os.path.exists(self.folder+"/output")):
            os.makedirs(self.folder+"/output")
        print("saving ",self.df)
        self.df.to_csv(self.folder+"/output/avg_of_"+self.dataset_name+".csv")