import base64
import hashlib
import hmac
import json
import urllib

import requests
from datetime import datetime


def darkkar_notic():
    response = requests.get('https://www.darkkar.com/api/getInitData', headers=headers).json()
    print(response['AnnouncementTitle'] + "\n" + response['Announcement'])
    ding_push(response['AnnouncementTitle'] + "\n" + response['Announcement'])


def get_darkkar_token(user):
    login_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Android/4.3.0',
    }
    login_url = "https://www.darkkar.com/api/login?account=" + user[0] + "&password=" + user[1]
    login_response = requests.post(login_url, headers=login_headers, allow_redirects=False)
    return 'Bearer ' + str.replace(login_response.text, '"', '')


def darkkar_sign():
    for key in range(len(darkkar_users)):
        user = darkkar_users[key]
        darkkar_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Android/4.3.0',
            'authorization': get_darkkar_token(user)
        }
        user_data_url = "https://www.darkkar.com/api/getUserData?versionCode=" + str(version_code)
        user_data_response = requests.get(user_data_url, headers=darkkar_headers, allow_redirects=False).json()
        print('{},积分{},本次{}'.format(user[0], user_data_response['Points'], user_data_response['ObtainPoints']))
        ding_push('{},积分{},本次{}'.format(user[0], user_data_response['Points'], user_data_response['ObtainPoints']))


headers = {
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; MI 6 MIUI/20.6.18)'
}


def get_time():
    # url = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
    # url = 'https://worldtimeapi.org/api/timezone/Asia/ShangHai'
    # response = requests.get(url, headers=headers).json()
    # # t = response['data']['t']
    # utc_time_str = response['utc_datetime']
    # utc_time = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
    # t = int(utc_time.timestamp() * 1000)
    # return t
    return int(datetime.now().timestamp() * 1000)


def ding_push(content):
    timestamp = get_time()
    secret_enc = ding_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, ding_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = f"https://oapi.dingtalk.com/robot/send?access_token={ding_access_token}&timestamp={timestamp}&sign={sign}"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
    }
    data = ("{\"at\":{\"isAtAll\":true},\"msgtype\":\"text\",\"text\":{\"content\":\"" + content + "\"}}").encode(
        'utf-8')
    response = requests.post(url, data=data, headers=headers).json()
    if response["errcode"] != 0:
        print("钉钉推送失败")


def main():
    darkkar_sign()
    darkkar_notic()

def main_handler(event, context):
    return main()

if __name__ == '__main__':
    ding_access_token = ''
    ding_secret = ''
    version_code = 67
    darkkar_users = json.loads('[]')
    main()
