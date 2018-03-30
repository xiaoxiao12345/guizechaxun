#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pymongo
import uuid
from pymongo import MongoClient

def get_ruleid(name):
    client = MongoClient('192.168.0.102',27017)
    dev_db = client.devplatform
    gz_db = client.gz_opinion
    dev_collection = dev_db.rule.find({"alias":name})
    for dev_item in dev_collection:
        print(dev_item)
        if isinstance(dev_item, dict):
            rule_id = dev_item.get("_id")
            print("rule_id", str(rule_id))
        else:
            print("no rule")

    gz_collection = gz_db.page_setup.find({},{"relations":1})
    print(gz_collection.count())

    for item in gz_collection:
        if not item.has_key("relations"):
            continue
        if not item["relations"]:
            continue

        for key, value in item["relations"]["MDict"].items():
            if not value or value['type'] != 1:
                continue

            for tag_name, tag_value in value['value']['module']['binding'].items():
                relation_ruleid = tag_value['datasource']['id']
                print("relation_ruleid", relation_ruleid.encode('utf-8'))
                if relation_ruleid.encode('utf-8') == str(rule_id):
                    print('found')

            '''    
            try:
                if isinstance(uuid.UUID(key), uuid.UUID):
                    if item["relations"]["MDict"][key]["value"]["module"]["binding"]:
                        for binding_key ,value in item['relations']['MDict'][key]['value']['module']['binding'].items():
                            relation_ruleid = item["relations"]["MDict"][key]["value"]["module"]["binding"][binding_key]["datasource"]["id"]
                            print(relation_ruleid+"/n")
                            if relation_ruleid == rule_id:
                                print("get relation_ruleid == rule_id")
                                print("relation_ruleid:"+relation_ruleid)
                                print("\n")
            except:
                pass

            '''

if __name__ == "__main__":
    get_ruleid("涉华外媒group查询")