import json
from flask import Flask, request
import pandas as pd
import numpy as np
import onnxruntime as rt

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    writeCsv(data.get('res'), data.get('thi'))

    return predict()


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


if __name__ == '__main__':
    predict()
