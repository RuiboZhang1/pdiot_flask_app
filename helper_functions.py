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


