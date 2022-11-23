import requests

url = 'http://34.89.117.73:5000/register'

registerObject = {'student_id': 's1911028', 'password': '12312312312'}
response = requests.post(url, json=registerObject)

print(response)
print(response.status_code)
