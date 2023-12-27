import base64
import hashlib
import hmac
import os
import urllib

import requests


def get_weilaigpt_token():
    login_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Host': 'api.thisonegpt.com',
    }
    login_url = "https://api.thisonegpt.com/sqx_fast/app/Login/registerCode?phone=" + weilaigpt_user + "&password=" + weilaigpt_pass
    login_response = requests.post(login_url, headers=login_headers, allow_redirects=False)
    return login_response.json()['token']

def weilaigpt_sign():
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Token': get_weilaigpt_token()
    }
    sign_url = "https://pc.weilaigpt.cn/sqx_fast/app/integral/signIn"
    return_response = requests.get(sign_url, headers=headers, allow_redirects=False)
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
    weilaigpt_sign()


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    ding_access_token = os.environ['DING_ACCESS_TOKEN']
    ding_secret = os.environ['DING_SECRET']
    weilaigpt_user = os.environ['WEILAIGPT_USER']
    weilaigpt_pass = os.environ['WEILAIGPT_PASS']
    main()