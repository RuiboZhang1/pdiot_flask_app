import sqlite3
from flask import Flask, request, Response, abort, make_response, jsonify
import helper_functions
import pandas as pd
import numpy as np
import onnxruntime as rt
import time
from collections import Counter

app = Flask(__name__)

# preload model for saving time
res = rt.InferenceSession("ONNX/res.onnx")
thi = rt.InferenceSession("ONNX/thi.onnx")
input_name_res = res.get_inputs()[0].name
label_name_res = res.get_outputs()[0].name
input_name_thi = thi.get_inputs()[0].name
label_name_thi = thi.get_outputs()[0].name


# connect to the sqlite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# registration api
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

        
# login api
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


# activity prediction api
@app.route('/predict', methods=['POST'])
def predict():
    print("receive request")
    data = request.json
    student_id = data.get('id')
    print(student_id)
    timestamp = "166" + str(data.get('res')[0][0])[:-2]

    helper_functions.writeCsv(data.get('res'), data.get('thi'))
    activity = predict()

    helper_functions.insertHistory(student_id, activity, timestamp)

    return activity


# HOW TO USE TIMESTAMP TO FIND THE HISTORY
# 1. Activity Per Hour, 1 miniute slice
# 2. Activity for five minutes, 5 seconds slice
@app.route('/history', methods=['POST'])
def history():
    student_id = request.json.get('student_id')
    curr_time = str(int(time.time() * 1000))
    print("current time:", curr_time)
    get_type = request.json.get('get_type') # hour or miniute

    return_list = []
    time_list = []
    
    if (get_type == 'hour'):
        for i in range(61):
            time_list.insert(0, str(int(curr_time) - 60000 * i))
    elif (get_type == 'miniute'):  # 5 miniutes
        for i in range(61):
            time_list.insert(0, str(int(curr_time) - 5000 * i))

    for i in range(60):
        start_time = time_list[i]
        end_time = time_list[i+1]
        activity_list = helper_functions.getHistory(student_id, start_time, end_time)
            
        if (activity_list == []):
            return_list.append('')
        else:
            activity_dic = helper_functions.generateActivityDic()
            for j in activity_list:
                activity_dic[j] += 1
                
            most_common_activity = max(activity_dic, key=activity_dic.get)
            return_list.append(most_common_activity)

    # total recorded activity
    total = len(return_list) - return_list.count("")
    unique_activity = list(set(filter(None, return_list)))
    activity_percentage_dic = helper_functions.generateActivityPercentageDic()

    for i in unique_activity:
        if i == "general_movement":
            activity_percentage_dic["Movement"] += return_list.count(i) / total
        elif i == "ascending_stairs" or i == "descending_stairs":
            activity_percentage_dic["Up/Down stairs"] += return_list.count(i) / total
        elif i == "sitting" or i == "sitting_bent_forward" or i == "sitting_bent_backward" or i == "desk_work":
            activity_percentage_dic["Sitting"] += return_list.count(i) / total
        elif i == "standing":
            activity_percentage_dic["Standing"] += return_list.count(i) / total
        elif i == "Running":
            activity_percentage_dic["Running"] += return_list.count(i) / total
        elif i == "Walking":
            activity_percentage_dic["Walking"] += return_list.count(i) / total
        elif i == "lying_down_left" or i == "lying_down_on_back" or i == "lying_down_on_stomach" or i == "lying_down_right":
            activity_percentage_dic["Lying"] += return_list.count(i) / total        

    return_json = {"data": return_list, "percentage": activity_percentage_dic}

    print(return_json)
    return make_response(jsonify(return_json), 200)
            


# main function to predict the activity
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
    return result

        
if __name__ == '__main__':
    # TODO: change the host address to your internal IP address of the VM.
    app.run(host="10.154.0.2", debug=True)
