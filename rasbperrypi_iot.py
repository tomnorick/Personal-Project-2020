#!/usr/bin/env python3
#coding: utf-8

import time
import datetime
import picamera
import cv2
import sys
import numpy
from PIL import Image
import csv
import pyocr
import pyocr.builders
import subprocess
from subprocess import PIPE

PATH = './img/'

## カメラモジュールによる画像読み込み ##
def Mod_Camera_Capture():
    DATE = datetime.datetime.now()
    YMDHMS = DATE.strftime("%Y%m%d%H%M%S")

    with picamera.PiCamera() as camera:
        camera.resolution = (800,500)
        CAPTURE_DATA = YMDHMS + '.jpg'
        camera.capture(PATH + CAPTURE_DATA)
    
    # 取り込んだ画像ファイル名と、取り込んだ時点の日付情報を戻り値として返す
    return CAPTURE_DATA, DATE


## OCR実行前の処理 2値化 ##
def Mod_Image_Preprocess(CAPTURE_FILE):
    SOURCEIMAGE = cv2.imread(PATH + CAPTURE_FILE)

    #イメージ読み込み
    GRAYIMAGE = cv2.cvtColor(SOURCEIMAGE, cv2.COLOR_BGR2GRAY)

    #2値化
    ret, img_thresh = cv2.threshold(GRAYIMAGE,48,255,cv2.THRESH_BINARY)

    KERNEL = numpy.ones((3,3), numpy.uint8)
    OPENING_IMAGE = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, KERNEL)
    OPENING_IMAGE = cv2.bitwise_not(OPENING_IMAGE)

    #2値化したファイルをOPファイルとして保存
    DIGIT_IMAGE = PATH + 'OP_' + CAPTURE_FILE
    cv2.imwrite(DIGIT_IMAGE, OPENING_IMAGE)

    # 2値化したファイル名を戻り値として返す
    return DIGIT_IMAGE


## 画像データをデータへ変換（OCR）してCSVへレコード追加##
def Mod_OCR(DIGIT_IMAGE, DATE):

    #letsgodigitalライブラリを使ってOCRを実行
    tools = pyocr.get_available_tools()
    tool = tools[0]

    IMG = Image.open(DIGIT_IMAGE)

    BUILDER = pyocr.builders.TextBuilder(tesseract_layout=6)
    OCR = tool.image_to_string(IMG, lang="letsgodigital", builder = BUILDER)

    # OCRで得られた数値をCSVへ日付データと共に出力するレコードへ変換
    NEW_LINE = [DATE, OCR]
    
    # CSVへレコード追加
    with open('data.csv', 'a') as CSV_FILE:
        writer = csv.writer(CSV_FILE, lineterminator='\n')
        writer.writerow(NEW_LINE)

    return


## CSVファイルをS3へアップ ##
def Mod_Upload_Cloud():
    PROC = subprocess.run("aws s3 cp ./data.csv s3://piperstorage", shell=True, text=True)

    return


def main():

    CAPTUREFILE, CAPTUREDATE = Mod_Camera_Capture()
    DIGITALFILE = Mod_Image_Preprocess(CAPTUREFILE)
    Mod_OCR(DIGITALFILE, CAPTUREDATE)
    Mod_Upload_Cloud()

if __name__ == '__main__':
    main()