#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import httplib,urllib
from time import ctime
import threading

postJson={
            "gfield":"TopicID",
            "accurate":'true',
            "topicID_not":0,
            "id_not":0,
            "DGarbage":0,
            "categories":3,
            "word":"广州",
            "not":"广告",
            "group":"true",
            "sort":"",
            "rows":50,
            "endtime":"20180330",
            "starttime":"20180330",
            "page":1
}
params = urllib.urlencode(postJson)

headers = {"Content-Type":"application/x-www-form-urlencoded",
           "Connection":"Keep-Alive"
           }

def  Clean():
    requrl ="/search/common/wyzhcluster/group"
    conn = httplib.HTTPConnection("27.17.18.131",38131)
    conn.request(method="POST",url=requrl,body=params, headers=headers)
   # r = requests.post('http://27.17.18.131:38131/search/common/wyzhcluster/group', data={'name': 'leo'})
    response=conn.getresponse()
    print(response.status)

#创建10个线程
threads = []
for i in range(10):
    t = threading.Thread(target=Clean, kwargs={})
    threads.append(t)




if __name__ == "__main__":
    print("start"),ctime()
    for i in threads:
        i.start()
    for i in threads:
        i.join()


    print"end",ctime()
