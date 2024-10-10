import base64
import hashlib
import hmac
import os
import urllib
import time

import requests
from datetime import datetime


def appshare_flag():
    version_code = f"{appshare_version_code}34"
    timestamp = get_time()
    # timestamp_short = int((int(timestamp) / 1000))
    # 服务器时区转换
    timestamp_short = int((int(timestamp) / 1000) + (8 * 60 * 60))
    time_struct = time.localtime(timestamp_short)
    formatted_time = time.strftime("%Y%m%d%H%M", time_struct)
    print(formatted_time)
    md5 = hashlib.md5()
    md5.update((appshare_token + version_code + formatted_time).encode('utf-8'))
    sign = md5.hexdigest().upper()
    flag_api = 'user/login/v1/launchApp2'
    api_sign = f"{flag_api}:{sign}:{timestamp}"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'okhttp/4.12.0',
        'Host': 'app.sharess.cn',
        'api_sign': api_sign
    }
    flag_url = (f"https://app.sharess.cn/{flag_api}?token={appshare_token}&oaid={appshare_token}&sign={sign}"
                f"&versionCode={appshare_version_code}&deviceSdk=34")
    return_response = requests.get(flag_url, headers=headers, allow_redirects=False)
    print(return_response.text)

def appshare_sign():
    appshare_flag()
    timestamp = get_time()
    # timestamp_short = int((int(timestamp) / 1000))
    # 服务器时区转换
    timestamp_short = int((int(timestamp) / 1000) + (8 * 60 * 60))
    time_struct = time.localtime(timestamp_short)
    formatted_time = time.strftime("%Y%m%d%H%M", time_struct)
    print(formatted_time)
    md5 = hashlib.md5()
    md5.update((appshare_token + formatted_time).encode('utf-8'))
    sign = md5.hexdigest().upper()
    api = 'user/v1/daySign'
    api_sign = f"{api}:{sign}:{timestamp}"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'okhttp/4.12.0',
        'Host': 'app.sharess.cn',
        'api_sign': api_sign
    }
    sign_url = f"https://app.sharess.cn/{api}?token={appshare_token}&oaid={appshare_token}&sign={sign}"
    return_response = requests.post(sign_url, headers=headers, allow_redirects=False)
    print(return_response.text)
    ding_push(return_response.text)


headers = {
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; MI 6 MIUI/20.6.18)'
}


def get_time():
    # url = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
    url = 'https://worldtimeapi.org/api/timezone/Asia/ShangHai'
    response = requests.get(url, headers=headers).json()
    # t = response['data']['t']
    utc_time_str = response['utc_datetime']
    utc_time = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
    t = int(utc_time.timestamp() * 1000)
    return t


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
    data = ("{\"at\":{\"isAtAll\":true},\"msgtype\":\"text\",\"text\":{\"content\":" + content + "}}").encode(
        'utf-8')
    response = requests.post(url, data=data, headers=headers).json()
    if response["errcode"] != 0:
        print("钉钉推送失败")


def main():
    appshare_sign()


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    ding_access_token = os.environ['DING_ACCESS_TOKEN']
    ding_secret = os.environ['DING_SECRET']
    appshare_token = os.environ['APPSHARE_TOKEN']
    appshare_version_code = os.environ['APPSHARE_VERSION_CODE']
    main()
