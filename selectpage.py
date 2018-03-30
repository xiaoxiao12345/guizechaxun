#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pymongo
import uuid
from pymongo import MongoClient

def get_ruleid(name):
    client = MongoClient('192.168.0.102',27017)
    dev_db = client.devplatform
    gz_db = client.gz_opinion
    dev_collection = dev_db.rule.find_one({"alias":name})
    gz_collection = gz_db.page_setup.find({},{"relations.MDict":1})
    print(dev_collection)
    if isinstance(dev_collection, dict):
        rule_id = dev_collection.get("name")
        print(rule_id)
    else:
        print("no rule")
    for item in gz_collection:
        if item.has_key("relations"):
            if item["relations"]:
                for key, value in item["relations"]["MDict"].items():
                    try:
                        if isinstance(uuid.UUID(key), uuid.UUID):
                            print(key)
                            if item["relations"]["MDict"][key]["value"]["module"]["binding"]:
                                for binding_key ,value in item['relations']['MDict'][key]['value']['module']['binding'].items():
                                    relation_ruleid = item["relations"]["MDict"][key]["value"]["module"]["binding"][binding_key]["datasource"]["id"]
                                    print(relation_ruleid+"/n")
                                    if relation_ruleid == rule_id:
                                        print("get relation_ruleid == rule_id")
                                        print("relation_ruleid:"+relation_ruleid)
                    except:
                        pass



if __name__ == "__main__":
    get_ruleid("舆情预警文章_保存更新")