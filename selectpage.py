#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pymongo
import uuid
from pymongo import MongoClient

def get_ruleid(name):
    client = MongoClient('192.168.0.102',27017)
    dev_db = client.devplatform
    dev_collection = dev_db.rule.find({"alias":name})
    for dev_item in dev_collection:
        print(dev_item)
        if isinstance(dev_item, dict):
            rule_id = dev_item.get("_id")
            return rule_id
        else:
            print("no rule")

def get_page_equal_ruleid(rule_id):
    client = MongoClient('192.168.0.102', 27017)
    gz_db = client.gz_opinion
    gz_collection = gz_db.page_setup.find({},{"relations":1})
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
                if relation_ruleid.encode('utf-8') == str(rule_id):
                    import pdb; pdb.set_trace()
                    print('found')



if __name__ == "__main__":
    rule_id= get_ruleid("涉华外媒group查询")
    get_page_equal_ruleid(rule_id)