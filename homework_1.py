# 1. Посмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.
import requests
import json

req = requests.get("https://api.github.com/users/AnnaPavl/repos")

with open('user.json', 'w') as outfile:
    json.dump(req.json(), outfile)

with open('user.json') as json_file:
    data = json.load(json_file)

for i in range(len(data)):
    print(data[i].get('name'))

print(req.headers)

# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests

link = "https://oauth.vk.com/authorize"
idt = 7819534
uri = 'https://oauth.vk.com/blank.html'
display = 'page'
response_type = 'token'
scope = 'friends'
params = {'client_id': idt, 'redirect_uri': uri, 'response_type': response_type, 'display': display, 'scope': scope}
resp = requests.get(link, params=params).text
file = open("vk.txt", "w")
file.write(resp)
file.close()
f = open('vk.txt', 'r')
print(f.read())
