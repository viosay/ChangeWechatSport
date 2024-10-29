import base64
import hashlib
import hmac
import os
import urllib

import requests
from datetime import datetime


def pcr532_sign():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Android/4.3.0',
    }
    data = {
        'username': pcr532_username,
        'passc': pcr532_passc,
        'USERID': pcr532_USERID
    }
    sign_url = "https://www.rfidfans.com/upload/qiandao.php"
    return_response = requests.post(sign_url, headers=headers, data=data, allow_redirects=False)
    print(return_response.text)
    ding_push(return_response.text)


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
    pcr532_sign()


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    ding_access_token = os.environ['DING_ACCESS_TOKEN']
    ding_secret = os.environ['DING_SECRET']
    pcr532_username = os.environ['PCR532_USERNAME']
    pcr532_passc = os.environ['PCR532_PASSC']
    pcr532_USERID = os.environ['PCR532_USER_ID']
    main()
