import base64
import hashlib
import hmac
import urllib
import time

import requests


def appshare_sign():
    timestamp = get_time()
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
    url = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
    response = requests.get(url, headers=headers).json()
    t = response['data']['t']
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
    ding_access_token = ''
    ding_secret = ''
    appshare_token = 'EF500D24F12DA53C1724855D7E3B57F4'
    main()
