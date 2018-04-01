#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pymongo
import uuid
from pymongo import MongoClient
from docx import Document
from docx.shared  import Pt

def get_rule_name(url):
    client = MongoClient('192.168.0.102', 27017)
    gz_db = client.gz_opinion
    collection = gz_db.autodesign2.find({},{"objs":1,"_id":0})
    rule_name = []
    for item in collection:
        for key, value in item['objs'].items():
            if not value.has_key('option'):
                continue

            option = value['option']
            if not option.has_key('data'):
                continue

            data = option['data']
            if data and isinstance(data,list):
                for data_item in data:
                    if not data_item.has_key('data'):
                        continue

                    if isinstance(data_item['data'], dict):
                        if not data_item['data'].has_key('url'):
                            continue

                        if data_item['data']['url'] == url:
                            key = key.encode('gbk')
                            print(item['objs'][key]['alias'])
                            rule_name.append(item['objs'][key]['alias'])

    return rule_name

def get_ruleid(name):
    client = MongoClient('192.168.0.102',27017)
    dev_db = client.devplatform
    dev_collection = dev_db.rule.find({"alias":name})
    for dev_item in dev_collection:
        if isinstance(dev_item, dict):
            rule_id = dev_item.get("_id")
            return rule_id
        else:
            print("no rule")

def get_page_equal_ruleid(rule_id):
    page = []
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
                    dev_db = client.devplatform
                    page_collection = dev_db.page.find({"_id":item['_id']})
                    for page_item in page_collection:
                        for page_key,page_value in page_item.items():
                            if page_key == 'alias':
                                page.append(page_value)

                    return page


def gen_doc(name, page):
    document = Document()
    document.add_heading(text=u'用了'+name+u'规则的页面',level=1)

    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    run.font.size = Pt(24)
    run.font.name = u'宋体'
    for item in page:
        document.add_paragraph(text=item, style='ListBullet')
    document.add_page_break()
    document.save(name+'.docx')

def main():
    rule_name = get_rule_name("http://61.164.49.130:13001/statisticsTask/api/result/list")
    for rule in rule_name:
        rule_id = get_ruleid(rule)
        if rule_id:
            page = get_page_equal_ruleid(rule_id)
            if page:
                gen_doc(rule, page)
if __name__ == "__main__":
    main()
