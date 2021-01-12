#!/usr/bin/env python3
#coding: utf-8

import subprocess
from subprocess import PIPE
import pandas
import matplotlib.pyplot
import datetime
import os
from flask import Flask, render_template, request

# Create a Flask instance
app = Flask(__name__)

##### Define routes #####
@app.route('/')
def home():
    return render_template('index.html',url="home")

##### Run the Flask instance, browse to http://<< Host IP or URL >>:5000 #####
if __name__ == "__main__":

    ## S3から最新のCSVファイルをダウンロード
    PROC = subprocess.run("aws s3 cp s3://piperstorage/data.csv ./", shell=True, text=True)

    
    ## CSVファイルをオープンして、プロットしたイメージファイルへ変換
    DATEINFO = {"date": "str", "weight": "float"}
    PARSE_DATES = ["date"]
    PLOT_POINT = pandas.read_csv("data.csv", index_col=0, dtype=DATEINFO, parse_dates=True)
    PLOT_POINT.plot()
    matplotlib.pyplot.savefig("./static/Graph.png")
    

    ## Flaskで展開
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', '5000')), threaded=True)
