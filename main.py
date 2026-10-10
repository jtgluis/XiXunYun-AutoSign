import httpx
import time
import os
import requests

from utils.randomize import generate
from utils.location import encrypted_latitude, encrypted_longitude
from utils.data import (
    account,
    password,
    school_id,
    province,
    city,
    address,
    address_name
)

# ==========================
# Server酱 推送函数
# ==========================
def send_serverchan(title, content):
    sendkey = "SCT435821T5mnPXxe1FsJfxxuljllJRDHD"  # os.getenv("SERVERCHAN_SENDKEY")

    if not sendkey:
        print("未配置 SERVERCHAN_SENDKEY")
        return

    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    data = {
        "title": title,
        "desp": content
    }

    try:
        requests.post(url, data=data, timeout=10)
        print("Server酱推送成功")
    except Exception as e:
        print(f"Server酱推送失败: {e}")


# ==========================
# 登录获取token
# ==========================
def login_and_get_token():
    token, uuid = generate()
    print(f"初始随机token为：{token}")

    url = f"https://api.xixunyun.com/login/api?token={token}&from=app&version=5.4.3&school_id={school_id}"

    payload = {
        'app_version': '5.4.3',
        'uuid': uuid,
        'request_source': 3,
        'platform': 2,
        'password': password,
        'system': '14',
        'school_id': school_id,
        'account': account,
        'app_id': 'cn.vanber.xixunyun.saas'
    }

    headers = {
        'User-Agent': 'okhttp/3.8.1',
        'content-type': 'application/x-www-form-urlencoded'
    }

    try:
        with httpx.Client(timeout=20) as client:
            response = client.post(url, headers=headers, data=payload)
            data = response.json()

            if data.get('code') == 20000:
                cookies = response.cookies
                token = data['data']['token']

                print("登录成功")
                send_serverchan("登录成功", "成功获取token")

                return token, cookies
            else:
                msg = data.get('message')
                print(f"登录失败：{msg}")
                send_serverchan("登录失败", msg)
                return None, None

    except Exception as e:
        print(f"登录异常：{e}")
        send_serverchan("登录异常", str(e))
        return None, None


# ==========================
# 执行签到
# ==========================
def signin_with_token(token, cookies):

    time.sleep(5)

    url = f"https://api.xixunyun.com/signin_rsa?token={token}&from=app&version=4.9.7&school_id={school_id}"

    payload = {
        'address': address,
        'province': province,
        'city': city,
        'latitude': encrypted_latitude,
        'longitude': encrypted_longitude,
        'address_name': address_name
    }

    headers = {
        'User-Agent': 'okhttp/3.8.1',
        'content-type': 'application/x-www-form-urlencoded'
    }

    try:
        with httpx.Client(timeout=20) as client:
            response = client.post(url, headers=headers, data=payload)
            data = response.json()
            message = data.get('message')

            if data.get('code') == 20000:
                print(f"签到成功：{message}")
                send_serverchan("签到成功", message)
                return True
            else:
                print(f"签到失败：{message}")
                send_serverchan("签到失败", message)
                return False

    except Exception as e:
        print(f"签到异常：{e}")
        send_serverchan("签到异常", str(e))
        return False


# ==========================
# 主程序
# ==========================
if __name__ == "__main__":

    token, cookies = login_and_get_token()

    if token and cookies:

        # 失败自动重试一次
        success = signin_with_token(token, cookies)

        if not success:
            print("准备重试一次签到...")
            time.sleep(10)
            signin_with_token(token, cookies)

    else:
        print("未获取到token，终止程序")
