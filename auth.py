import vk_api
import os
import json

login = ''
passwd = ''

VK = vk_api.VkApi(login, passwd)
VK.auth()
VK = VK.get_api()
access_token = 0

try:
    User = VK.users.get()
except:
    print("Error")
else:
    print(f"\nHello {User[0]['first_name']}")

    with open('vk_config.v2.json', 'r') as data_file:
        data = json.load(data_file)

    for xxx in data[login]['token'].keys():
        for yyy in data[login]['token'][xxx].keys():
            access_token = data[login]['token'][xxx][yyy]['access_token']

    print('=' * 85)
    print(f"Твой ID {User[0]['id']}")
    print('=' * 85)
    print(f"Access_Token: {access_token}")
    print('=' * 85)

    os.remove('vk_config.v2.json')
input('Exit [Enter]')


