import requests
import json
url = 'http://192.168.20.248:5500/task'
data = {'db_name':'17DZ','login_info':{"account":"13524339221","password":"gcf13524339221"},'zt':['上海好药师恒都大药房', '上海复美金亮大药房'],'callback_ip':'192.168.20.141:20882'}
response=requests.post(url,headers={"Content-Type":"application/json"},data=json.dumps(data))
print(response.text)



import requests
import json
url = 'http://192.168.20.248:5500/task'
data = {'db_name':'17DZ','login_info':{"account":"13524339221","password":"gcf13524339221"},'zt':["上海好药师恒都大药房","上海复美金亮大药房"],'callback_ip':'192.168.20.141:20882'}
response=requests.post(url,headers={"Content-Type":"application/json"},data=json.dumps(data))
print(response.text)