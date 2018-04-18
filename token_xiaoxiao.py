import hashlib
import time
import requests
import json

def get_token():
    data={
        'key':'5ab9bf09e1382329eec64960',
        'open_key':'e533ca102340f1962b3461035103d706',
        'timestamp':str(int(time.time())),
        'user_name':'zhongxin',
        'user_password':'e10adc3949ba59abbe56e057f20f883e',
    }

    sign=hashlib.md5(data['key']+data['open_key']+data['timestamp']+data['user_name']+data['user_password']).hexdigest()
    r = requests.post('http://192.168.56.103:8800/api/user/token/2',{
        'key':data['key'],
        'username':data['user_name'],
        'timestamp':data['timestamp'],
        'sign':sign
    })

    return json.loads(r.content)


def main():
    token  = get_token()

    data={'token':token['data']}

    r = requests.post('http://192.168.56.103:8800/api/user/batch',data=data)


if __name__ == '__main__':
    main()