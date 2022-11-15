import sqlite3
import json
from flask import Flask, request, Response, abort, make_response, jsonify
import helper_functions
import pandas as pd
import numpy as np
import onnxruntime as rt

app = Flask(__name__)

# preload model
res = rt.InferenceSession("ONNX/res.onnx")
thi = rt.InferenceSession("ONNX/thi.onnx")
input_name_res = res.get_inputs()[0].name
label_name_res = res.get_outputs()[0].name
input_name_thi = thi.get_inputs()[0].name
label_name_thi = thi.get_outputs()[0].name


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
    print("receive request")

    helper_functions.writeCsv(data.get('res'), data.get('thi'))

    return predict()


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
        1: 'lying_down_left',
        2: 'lying_down_on_back',
        3: 'lying_down_on_stomach',
        4: 'lying_down_right',
        5: 'sitting_bent_backward',
        6: 'sitting_bent_forward',
        7: 'sitting'
    }

    thi_class_labels = {
        0: 'desk_work',
        1: 'ascending_stairs',
        2: 'descending_stairs',
        3: 'running',
        4: 'walking',
        5: 'general_movement',
        6: 'standing'
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

    
    resFeatures = np.array([resFeatures])
    resFeatures = resFeatures.astype(np.float32)
    pred_onx = res.run([label_name_res], {input_name_res: resFeatures})[0]

    if pred_onx[0] == 100:
        
        thiFeatures = np.array([thiFeatures])
        thiFeatures = thiFeatures.astype(np.float32)
        pred_onx = thi.run([label_name_thi], {input_name_thi: thiFeatures})[0]
        result = thi_class_labels[pred_onx[0]]
    else:
        result = res_class_labels[pred_onx[0]]
    # print(result)
    return result

        



if __name__ == '__main__':
    # app.run(host="10.154.0.2", debug=True)
    app.run(debug=True)