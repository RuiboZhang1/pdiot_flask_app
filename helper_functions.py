import sqlite3 as sql
import json
import pandas as pd
import numpy as np
import onnxruntime as rt
from flask import Flask, request, Response, abort, make_response, jsonify


def checkExistUser(student_id):
    con = sql.connect("database.db")
    cur = con.cursor()
    statement = "SELECT * FROM users WHERE student_id = '%s'" % student_id
    cur.execute(statement)

    if cur.fetchone() is not None:
        return True
    else:
        return False


def insertUser(student_id, password):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO users (student_id, password) VALUES (?, ?)" , (student_id, password))
    con.commit()
    con.close()


def verifyUser(student_id, password):
    con = sql.connect("database.db")
    cur = con.cursor()
    statement = f"SELECT 1 FROM users WHERE student_id = '{student_id}' AND password = '{password}'"
    cur.execute(statement)

    if cur.fetchone() is not None:
        return True
    else:
        return False


def checkExistHistory(student_id, activity, start_time, end_time):
    con = sql.connect("database.db")
    cur = con.cursor()
    statement = f"SELECT 1 FROM history WHERE student_id = '{student_id} AND activity = '{activity}' AND start_time = '{start_time}' AND end_time = '{end_time}'"
    cur.execute(statement)

    if cur.fetchone() is not None:
        return True
    else:
        return False

def insertHistory(student_id, activity, start_time):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO history (student_id, activity, start_time) VALUES (?, ?, ?)" , (student_id, activity, start_time))
    con.commit()
    con.close()

def getHistory(student_id, start_time, curr_time):
    con = sql.connect("database.db")
    cur = con.cursor()
    statement = f"SELECT * FROM history WHERE student_id = '{student_id} AND start_time >= '{start_time} sq'"


def writeCsv(res, thi):
    res = json.loads(res)
    thi = json.loads(thi)
    file = open("cache/thi.csv", "w")
    file.write(
        "timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z\n"
    )
    for i in thi:
        file.write(str(i)[1:-1] + "\n")

    file = open("cache/res.csv", "w")
    file.write("timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n")
    for i in res:
        file.write(str(i)[1:-1] + "\n")
    
    file.close()


def predict():
    result = None
    resDf = pd.read_csv("cache/res.csv")
    thiDf = pd.read_csv("cache/thi.csv")
    res_columns_of_interest = [
        'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z'
    ]
    thi_columns_of_interest = [
        'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z', 'mag_x',
        'mag_y', 'mag_z'
    ]

    res_class_labels = {
        1: 'Lying down left',
        2: 'Lying down on back',
        3: 'Lying down on stomach',
        4: 'Lying down right',
        5: 'Sitting bent backward',
        6: 'Sitting bent forward',
        7: 'Sitting'
    }

    thi_class_labels = {
        0: 'Desk work',
        1: 'Climbing stairs',
        2: 'Descending stairs',
        3: 'Running',
        4: 'Walking at normal speed',
        5: 'Movement',
        6: 'Standing'
    }

    resFeatures = []
    thiFeatures = []
    # print(resDf["accel_x"].to_list())
    for feature in res_columns_of_interest:
        data = np.array(resDf[feature].to_list())
        resFeatures.append(np.sum(data))
        resFeatures.append(np.median(data))
        resFeatures.append(np.mean(data))
        resFeatures.append(50)
        resFeatures.append(np.std(data))
        resFeatures.append(np.var(data))
        resFeatures.append(np.sqrt(np.mean(data**2)))
        resFeatures.append(max(data))
        resFeatures.append(max(map(abs, data)))
        resFeatures.append(min(data))

    for feature in thi_columns_of_interest:
        data = np.array(thiDf[feature].to_list())
        thiFeatures.append(np.sum(data))
        thiFeatures.append(np.median(data))
        thiFeatures.append(np.mean(data))
        thiFeatures.append(50)
        thiFeatures.append(np.std(data))
        thiFeatures.append(np.var(data))
        thiFeatures.append(np.sqrt(np.mean(data**2)))
        thiFeatures.append(max(data))
        thiFeatures.append(max(map(abs, data)))
        thiFeatures.append(min(data))

    res = rt.InferenceSession("ONNX/res.onnx")
    input_name = res.get_inputs()[0].name
    label_name = res.get_outputs()[0].name
    resFeatures = np.array([resFeatures])
    resFeatures = resFeatures.astype(np.float32)
    pred_onx = res.run([label_name], {input_name: resFeatures})[0]

    if pred_onx[0] == 100:
        thi = rt.InferenceSession("ONNX/thi.onnx")
        input_name = thi.get_inputs()[0].name
        label_name = thi.get_outputs()[0].name
        thiFeatures = np.array([thiFeatures])
        thiFeatures = thiFeatures.astype(np.float32)
        pred_onx = thi.run([label_name], {input_name: thiFeatures})[0]
        result = thi_class_labels[pred_onx[0]]
    else:
        result = res_class_labels[pred_onx[0]]
    # print(result)
    return result