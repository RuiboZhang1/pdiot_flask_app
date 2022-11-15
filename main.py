import sqlite3
import json
from flask import Flask, request, Response, abort, make_response, jsonify
import helper_functions
import pandas as pd
import numpy as np
import onnxruntime as rt

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/register', methods=['POST'])
def register():
    student_id = request.json.get('student_id')
    password = request.json.get('password')
    
    if (helper_functions.checkExistUser(student_id)):
        # abort(Response('User already registerded', 400))
        print("User already registered")
        abort(400)
    else:
        helper_functions.insertUser(student_id, password)
        print('Registration successful')
        message = {'success':'true'}
        return make_response(jsonify(message), 200)

        


@app.route('/login', methods=['POST'])
def login():
    student_id = request.json.get('student_id')
    password = request.json.get('password')

    if (helper_functions.verifyUser(student_id, password)):
        print('Login successful')
        message = {'success':'true'}
        return make_response(jsonify(message), 200)
    else:
        print('Login failed')
        message = {'success':'false'}
        abort(400)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    helper_functions.writeCsv(data.get('res'), data.get('thi'))

    return helper_functions.predict()


# HOW TO USE TIMESTAMP TO FIND THE HISTORY
# 1. Activity Per Hour, 1 miniute slice
# 2. Activity Per Day, 10 miniutes slice
@app.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'POST':
        student_id = request.json.get('student_id')
        activity = request.json.get('activity')
        start_time = request.json.get('start_time')
        end_time =  request.json.get('end_time')

        if (helper_functions.checkExistHistory(student_id, activity, start_time)):
            print("History is existed")
            abort(400)
        else:
            helper_functions.insertHistory(student_id, activity, start_time)
            print('history added')
            message = {'success':'true'}
            return make_response(jsonify(message), 200)
    else:
        student_id = request.json.get('student_id')
        curr_time = request.json.get('curr_time') # timestamp in centisecond
        get_type = request.json.get('get_type') # hour or day

        if (get_type == 'hour'):
            start_time = curr_time - 360000

            # selection activity from database where match the student_id and between the start time and current time
            


        



if __name__ == '__main__':
    app.run(debug=True)