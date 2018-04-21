# -*- encoding:utf-8 -*-

from pymongo import MongoClient

def main():
    client = MongoClient('192.168.0.102',27017)
    system_db = client.wpcc
    pipeline = system_db.wpcc_form.aggregate([{"$group":{
        "_id":"$transportation",
        "count":{"$sum":1}
    }}])

    print(list(pipeline))


if __name__=="__main__":
    main()