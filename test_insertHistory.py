import requests
import time
import json
import numpy as np

url = 'http://127.0.0.1:5000/history'

activities = ['standing', 'sitting', 'general_movement', 'desk_work', 'running']

for i in range(30):
    randomNum = np.random.randint(0, 10)
    time.sleep(randomNum)

    activity = activities[np.random.randint(0,5)]
    ts = str(int(time.time() * 100))

    registerObject = {'student_id': 's1911027', 'activity': activity, 'start_time': ts}

    response = requests.post(url, json=registerObject)

print(response)
print(response.status_code)
