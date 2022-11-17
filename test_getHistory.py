import requests
import time

curr_time = str(int(time.time() * 100))

url = 'http://127.0.0.1:5000/history'

registerObject = {'student_id': 's1911027', 'curr_time': curr_time, 'get_type':'hour'}

response = requests.get(url, json=registerObject)

print(response)
print(response.status_code)
a = response.json()
for i in a:
    if (i == ''):
        print('no movement')
    else:
        print(i)
