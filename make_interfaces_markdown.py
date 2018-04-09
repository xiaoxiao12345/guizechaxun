#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pymongo
from threading import Thread
from collections import defaultdict
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import re
from functools import partial



def get_urleg_from_log(url, log_path):
    line_exp = r".*?Url:(.*?)cache.*"
    pat = re.compile(line_exp)
    url_eg = None
    with open(log_path, "rt") as f:
        for line in f.readlines():
            m = pat.match(line)
            if m:
                url_eg = m.group(1).strip().rstrip(",")
                # 青岛接口本地ip/电信ip替换为联通ip
                replace_ips = ["192.168.100.18", "222.173.108.185"]
                for replace_ip in replace_ips:
                    url_eg = url_eg.replace(replace_ip, "218.59.56.153")
                if url in url_eg:
                    return url_eg
            else:
                return url
class MarkdownDoc(object):
    """
    get a markdown doc which includes every page's contorls and rules' urls in autodesign2.
    """
    def __init__(self, title=u"页面模块接口调用文档", host=None, port=None, log_path_dir=None):
        self.title = title
        if host is None:
            self.host = "localhost"
        if port is None:
            self.port = 27017
        if log_path_dir is None:
            self.log_path_dir = "cp_logs"
        #self.log_paths = self.get_log_paths()
        self.log_paths = []

    def get_log_paths(self):
        log_path_dir = self.log_path_dir
        real_path = os.path.realpath(log_path_dir)
        if not os.path.exists(real_path):
            raise Exception("not exists log_path_dir %s" % log_path_dir)
        log_paths = []
        for log_name in os.listdir(real_path):
            log_path = os.path.join(real_path, log_name)
            log_paths.append(log_path)
        return log_paths

    def _get_autodesign2Data(self):
        autodesign_data = Autodesign2Data(self.host, self.port).get_datas()
        objs = []
        for auto_d in autodesign_data:
            objs = auto_d["objs"]
        self.autodesign_data = defaultdict(list)
        count = 0
        for obj in objs.values():
            count += 1
            obj_data = obj.get("data", {}).get("option", {}).get("data", [])
            for obj_d in obj_data:
                if obj_d.get("type") in ["get", "post"]:
                    self.autodesign_data[obj["rule_id"]].append(obj_d.get("data", {}))
        #print "autodesign2_count:{}".format(count)

    def _get_ruleData(self):
        self.rule_data = RuleData(self.host, self.port).get_datas()

    def _get_controlData(self):
        self.control_data = ControlData(self.host, self.port).get_datas()

    def _get_pageData(self):
        self.page_data = PageData(self.host, self.port).get_datas()
    
    def _get_page_setupData(self):
        self.page_setup_data = Page_setupData(self.host, self.port).get_datas()

    def get_docData(self):
        threads = [Thread(target=getattr(self, attr)) for attr in dir(self) if attr.startswith("_get_")]
        for t in threads:
            t.daemon = True
            t.start()
        for t in threads:
            t.join()
        ## get datas completed
        page_datas = self.page_data
        control_data = self.control_data
        rule_data = self.rule_data
        autodesign_data = self.autodesign_data
        page_setup_data = self.page_setup_data
        doc_data = DocData(page_datas, control_data, rule_data, page_setup_data, autodesign_data)
        return doc_data.get_doc_data()
        
    def gen_markdown_doc(self):
        try:
            doc_datas = self.get_docData()
        except: 
            raise 
        else:
            print "start to generate markdown document..."
            file_path = os.path.join(os.path.realpath("."), "%s.md" % self.title)
            try:
                self._gen_markdown_file(doc_datas, file_path)
            except Exception as e:
                raise Exception("generate markdown file failed:%s" % e)
            else:
                print "generate markdown file successfully. file path is %s" % file_path

            
    def _gen_markdown_file(self, doc_datas, file_path):
        """markdown string eg:
        ####1.page_name
        >
        1. control_name
        >>
        * url
        * eg: 
        """
        markdown_string = []
        title_string = "##%s" % self.title
        ps_string = "***PS:%s***" % u"接口示例参数仅供参考，请以接口实际调用参数为准！！！"
        markdown_string.extend([title_string, ps_string])
        page_count = 0
        for data in doc_datas:
            page_string = []
            page_count += 1
            page_name_string = "###%s. %s:%s" % (page_count, u"页面", data["page"])
            page_string.append(page_name_string)
            #page_string.append(">")
            control_count = 0
            for control_name, urls in data["controls_urls"]:
                control_count += 1
                control_name_string = ">####%s.%s.%s:%s" % (page_count, control_count, u"控件", control_name)
                page_string.append(control_name_string)
                #page_string.append("\n")
                page_string.append(">>")
                for url in urls:
                    #log_paths = self.log_paths
                    #p_executor = ProcessPoolExecutor()
                    #result_iterator = p_executor.map(partial(get_urleg_from_log, url), log_paths)
                    #result_iterator = [r for r in result_iterator]

                    #urleg = None # default value
                    """
                    # when use executor.submit
                    result_iterator = []
                    for log_path in log_paths:
                        f = p_executor.submit(get_urleg_from_log, url, log_path)
                        result_iterator.append(f)
                    #for res in as_completed(result_iterator):
                        #if res.result() is not None:
                            #url_eg = res.result()
                    """
                    #for res in result_iterator:
                    #    if res is not None:
                    #        urleg = res
                    #urleg_string = ""
                    #if urleg:
                    #    urleg_string = "* %s:%s" % (u"接口示例", urleg)
                    #else:
                    #    pass
                    #    #not_found_string = u"在现有的cp.log文件中没有找到, 需要更多的cp.log文件。或者当前接口已经废弃，不再使用！！！"
                    #    #urleg_string = "* %s:***%s***" % (u"接口示例", not_found_string)
                    if url:
                        url_string = "* ####%s:%s" % (u"接口", url)
                        page_string.append(url_string)
                        #page_string.append(urleg_string)
            markdown_string.extend(page_string)
        markdown_string = "\n".join(markdown_string)
        with open(file_path, "wt") as f:
            f.write(markdown_string.encode("utf-8"))


class DocData(object):
    """
    get every page's contorls and rules, then get rules' urls in autodesign2
    
    """
    def __init__(self, page_data, control_data, rule_data, page_setup_data, autodesign2_data=None):
        """
        """
        self.page_data = page_data
        self.control_data = control_data
        self.rule_data = rule_data
        self.page_setup_data = [d for d in page_setup_data]
        self.autodesign2_data = autodesign2_data

    def get_page_up(self, page_id):
        page_setup_data = self.page_setup_data
        for page_setup_d in page_setup_data:
            if str(page_setup_d["_id"]) == str(page_id):
                return page_setup_d
        
    def get_doc_data(self):
        """
        doc_data: list [doc_d, ...]
        doc_d: dict {"page": page_info.name, "contorls_urls": [(control_info.name, rule_info.urls), ...]}
        page_info: {"_id": xx, "name": xx, "alias", xx, ..}
        control_info: {"_id": xx, "name": xx, "alias": xx, ..}
        rule_info: {"_id": xx, "name": xx, "alias": xx, .., urls:[]}
        每个页面的控件名和控件对应的url（控件绑定的规则是自定设计中自定义生成的规则）
        PS：非自动设计生成的规则是没有对应的url的
        """
        
        doc_data = []
        page_data = [d for d in self.page_data]
        control_data = [d for d in self.control_data]
        # for rules not in autodesign2
        #rule_data = [d for d in self.rule_data]
        for p_d in page_data:
            #import pdb; pdb.set_trace()
            doc_d = {}
            doc_d["page"] = p_d["alias"]
            doc_d["controls_urls"] = [] 
            page_id = p_d["_id"]
            p_d =  self.get_page_up(page_id)
            if not p_d:
                continue
            # 初始化关系节点
            controls = p_d.get("controls", [])
            # 处理非初始化关系节点后的control_id和rule_id
            relations_mdict_values = p_d.get("relations", {}).get("MDict", {}).values()
            # handle relations
            try:
                find_rule_id1 = self.add_controls_urls_from_relations(relations_mdict_values, control_data, doc_d["controls_urls"])
            except Exception as e:
                raise Exception("add_controls_urls_from_relations failed: %s" % e)
            
            # handle controls
            try:
                find_rule_id2 = self.add_controls_urls_from_controls(controls, control_data, doc_d["controls_urls"])
            except Exception as e:
                raise Exception("add_controls_urls_from_controls failed: %s" % e)

            if find_rule_id1 or find_rule_id2:
                print doc_d["page"]

            if doc_d["controls_urls"]:
                doc_data.append(doc_d)
        #import pdb; pdb.set_trace()
        return doc_data

    def add_controls_urls_from_controls(self, controls, control_data, controls_urls):
        find_rule_id = False
        _rule_ids = ["58cf717b9ff6eb26d9fdff78"]
        for control in controls:
            rule_id = control.get("rule_key", "")
            if str(rule_id) in _rule_ids:
                find_rule_id = True
            control_id = control.get("control_key", "")
            if not rule_id or not control_id:
                continue
            # about control
            contr_name = self.get_contrname_from_id(control_id, control_data)
            if contr_name is None:
                continue
            # about rule's urls
            urls = self.get_urls_from_autodesign2(rule_id)
            if urls:
                #import pdb; pdb.set_trace()
                controls_urls.append((contr_name, urls))
        return find_rule_id

    def add_controls_urls_from_relations(self, relations_mdict_values, control_data, controls_urls):
        find_rule_id = False
        _rule_ids = ["58cf717b9ff6eb26d9fdff78"]
        for m_value in relations_mdict_values:
            m_value_value = m_value.get("value", {})
            # 跳过tag节点
            if not m_value_value or not isinstance(m_value_value, dict):
                continue
            module = m_value_value.get("module", {})
            if not module or not isinstance(module, dict):
                continue
            module_binding = module.get("binding", {})
            if not module_binding or not isinstance(module_binding, dict):
                continue
            datasource = module_binding.values()[0].get("datasource", {})
            if not datasource or not isinstance(datasource, dict):
                continue
            rule_id = datasource.get("id")
            if str(rule_id) in _rule_ids:
                find_rule_id = True
            control_id = module.get("id")
            if not control_id and not rule_id:
                continue
            contr_name = self.get_contrname_from_id(control_id, control_data)
            if contr_name is None:
                continue
            urls = self.get_urls_from_autodesign2(rule_id)
            if urls:
                #import pdb; pdb.set_trace()
                controls_urls.append((contr_name, urls))
        return find_rule_id
            
    def get_contrname_from_id(self, control_id, control_data):
        """
        由控件id获取控件名
        """
        contr_name = None
        for contr in control_data:
            if str(contr["_id"]) == control_id:
                contr_name = contr["alias"]
                break
        return contr_name
        
    def get_urls_from_autodesign2(self, rule_id, autodesign2_data=None):
        """
        @autodesign2_data:defaultdict {rule_id: [data], ...}
        @data: dict {"script": xx, "url": xx, "timeout":xx, ...}
        根据自动设计中自定义对象，生成规则的id,获取对应的urls
        """
        if autodesign2_data is None:
            autodesign2_data = self.autodesign2_data
        datas = autodesign2_data[rule_id]
        if not datas:
            return []
        urls = []
        for data in datas:
            urls.append(data.get("url"))
        return urls
            

# classes of get datas from mongodb
class BaseData(object):
    def __init__(self, host, port, main_db_name="devplatform", sub_db_name="gz_opinion", condition=None, projection=None):
        self.condition = condition
        self.projection = projection
        self.host = host
        self.port = port
        self.main_db_name = main_db_name
        self.sub_db_name = sub_db_name
        self.mongo_client = pymongo.MongoClient(self.host, self.port)
        self.db = self.mongo_client[self.sub_db_name]
        self.mdb = self.mongo_client[self.main_db_name]
        
    def get_datas(self):
        coll = self.coll
        condition = self.condition
        projection = self.projection
        datas = self._get_datas(coll, condition, projection)
        return datas

    def _get_datas(self, coll, condition=None, projection=None):
        """
        """
        _condition = {}
        _projection = {}
        if condition is not None:
            _condition.update(condition)
        if projection is not None:
            _projection.update(projection)
        if coll in ["autodesign2", "page_setup"]:
            _db = self.db
        else:
            _db = self.mdb
        try:
            if _projection:
                datas = _db[coll].find(_condition, _projection)
            else:
                datas = _db[coll].find(_condition)
        except:
            raise
        return datas

    
class Autodesign2Data(BaseData):
    coll = "autodesign2"

class Page_setupData(BaseData):
    coll = "page_setup"
class RuleData(BaseData):
    coll = "rule"


class PageData(BaseData):
    coll = "page"


class ControlData(BaseData):
    coll = "control"
    
    
    
def main():
    import time
    start = time.time()
    markdown_doc = MarkdownDoc(host="192.168.0.102")
    markdown_doc.gen_markdown_doc()
    end = time.time()
    print "generate markdown file cost:{} seconds".format(end - start)

if __name__ == "__main__":
    main()
