# -*- coding:utf-8 -*-
'''
======================
@author Vincent
======================
'''
from __future__ import division
import tornado.web
import tornado.httpclient
import urllib2
import re
import textwrap
import json
import random
from tornado import gen
from urllib import unquote
from Handler import Handler
from bs4 import BeautifulSoup
from auth import jwtauth
from bson.objectid import ObjectId
import requests
import urllib
# @jwtauth
# class ReverseHandler(tornado.web.RequestHandler):
#     def head(self, frob, frob_id):
#         # frob = retrieve_from_db(frob_id)
#         print int(frob_id)
#         if int(frob_id) > 20:
#             self.set_status(200)
#         else:
#             self.set_status(2001)
#
#     def write_error(self, status_code, **kwargs):
#         self.write("Gosh darnit, user! You caused a %d error." % status_code)
#
#     def get(self, input, ints):
#
#         temp = {"data": input[::-1]}
#
#         self.write(temp)
#
#
# class BookModule(tornado.web.UIModule):
#     def render(self, book):
#         return self.render_string(
#             "modules/book.html",
#             book=book,
#         )
#
#     def css_files(self):
#         return "/static/css/recommended.css"
#
#     def javascript_files(self):
#         return "/static/js/recommended.js"


@jwtauth
class StartSpider(Handler):
    """开始抓取数据接口"""

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        fid = self.get_argument('fid')
        if type(fid) is int:
            fid = str(fid)
        elif type(fid) is str:
            fid = fid
        page = str(self.get_argument('page', 1))
        callback = self.get_argument('callback', None)
        client = tornado.httpclient.AsyncHTTPClient()
        url = 'http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO&page=%s&count=200' % (fid, page)
        response = yield tornado.gen.Task(client.fetch, url)
        result = json.loads(response.body)
        if callback:
            responses = yield tornado.gen.Task(client.fetch, callback)
            self.writejson(json.loads(responses.body))
        else:
            self.writejson(result)


@jwtauth
class LongText(Handler):
    """Get Long Text"""

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        uid = self.get_argument('uid')
        if type(uid) is int:
            uid = str(uid)
        elif type(uid) is str:
            uid = uid
        bid = self.get_argument('bid')
        try:
            client = tornado.httpclient.AsyncHTTPClient()
            url = 'http://m.weibo.cn/%s/%s' % (uid, bid)
            response = yield tornado.gen.Task(client.fetch, url)
            html = BeautifulSoup(response.body, "lxml")
            text = html.find('div', class_='weibo-text')
            if text is not None:
                strtext = map(lambda x: str(x.encode('utf-8')), text.contents)
                longtext = ''.join(strtext)
                data = {'data': longtext, 'code': '000'}
            else:
                data = {'data': '', 'code': '2'}
            self.writejson(data)
        except:
            self.writejson({'data': 'system error', 'code': '1'})


@jwtauth
class IndexHandler(Handler):

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        query = self.get_argument('username')
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, "http://m.weibo.cn/n/" + query)
        result = response.headers['set-cookie'].split(';')
        try:
            cookies = ''
            params = {}
            for item in result:
                if 'M_WEIBOCN_PARAMS' in item:
                    cookies = item.split('=')[1]
            for item in unquote(cookies).split('&'):
                temp = item.split('=')
                params[temp[0]] = temp[1]
            fid = params['fid']
            client = tornado.httpclient.AsyncHTTPClient()
            url = 'http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO' % fid
            inforesponse = yield tornado.gen.Task(client.fetch, url)
            # print inforesponse.body
            userinfo = json.loads(inforesponse.body)['cards'][0]['card_group'][0]['mblog']['user']
            self.writejson({'data': userinfo, 'fid': fid, 'code': '000'})
        except IndexError, e:
            self.writejson({'data': result, 'code': '1'})


# @jwtauth
class Testdata(Handler):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):

        # # cons = self.get_argument('db')
        # my_dict = {i: i * i for i in xrange(100)}
        # # my_set = {i * 15 for i in xrange(100)}
        # import ast
        # expr = "[1, 2, 3]"
        # my_list = ast.literal_eval(expr)
        # print my_list
        # iterable = ['ahskjahd', 12, 23, 11, 'aaaa']
        # mongodb 模糊查询
        n = self.dbs.student.find().limit(2000)
        i = 0
        for item in (yield n.to_list(2000)):
            result = yield self.dbs.students.find_one({'M': item['M'], 'RU_School_schoolname': item['RU_School_schoolname'], 'province': item['province']})
            if result is not None:
                moneysum = result['Money']+item['Money']
                old_document = yield self.dbs.students.find_one({"_id": result['_id']})
                results = yield self.dbs.students.update({"_id": result['_id']}, {"$set": {"Money": moneysum}})
                print 'updated %s document' % results['n']
            else:
                inserts = yield self.dbs.students.insert({"Money": item['Money'], "M": item['M'], 'RU_School_schoolname': item['RU_School_schoolname'], 'province': item['province']})
                print inserts
            i += 1
        self.writejson({'data': i})


# 江西学校缴费情况表合并
class Mregedata(Handler):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):

        # # cons = self.get_argument('db')
        # my_dict = {i: i * i for i in xrange(100)}
        # # my_set = {i * 15 for i in xrange(100)}
        # import ast
        # expr = "[1, 2, 3]"
        # my_list = ast.literal_eval(expr)
        # print my_list
        # iterable = ['ahskjahd', 12, 23, 11, 'aaaa']
        # mongodb 模糊查询
        n = self.dbs.student.find().limit(2000)
        i = 0
        for item in (yield n.to_list(2000)):
            result = yield self.dbs.students.find_one({'M': item['M'], 'RU_School_schoolname': item['RU_School_schoolname'], 'province': item['province']})
            if result is not None:
                moneysum = result['Money']+item['Money']
                old_document = yield self.dbs.students.find_one({"_id": result['_id']})
                results = yield self.dbs.students.update({"_id": result['_id']}, {"$set": {"Money": moneysum}})
                print 'updated %s document' % results['n']
            else:
                inserts = yield self.dbs.students.insert({"Money": item['Money'], "M": item['M'], 'RU_School_schoolname': item['RU_School_schoolname'], 'province': item['province']})
                print inserts
            i += 1
        self.writejson({'data': i})


@jwtauth
class Testdata7netcc(Handler):
    """获取训练样本数据"""

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        # SubjectParam = self.get_json_argument('subject')
        client = tornado.httpclient.AsyncHTTPClient()
        code_url = 'http://10.161.165.239:7011/imgsvr/ru'
        code_result = yield tornado.gen.Task(client.fetch, code_url)
        print code_result.body
        code_result_json = json.loads(code_result.body)
        if code_result_json['status'] == 200:
            schoool_code_list = code_result_json['data']
        schoool_code_list_small = random.sample(schoool_code_list, 60)
        res = map(lambda x: "http://10.161.165.239:7011/imgsvr/exam?ru="+x['Code'], schoool_code_list_small)
        result = []
        i = 0
        while True:
            i += 1
            for item in res:
                school_result = yield tornado.gen.Task(client.fetch, item)
                temp_result = json.loads(school_result.body)
                if temp_result['data'] and temp_result['status'] == 200:
                    result.append(temp_result)
            self.SchoolOne = []
            if result.__len__() > 0:
                if len(random.sample(result, 1)[0]['data']) > 1:
                    self.SchoolOne = random.sample(random.sample(result, 1)[0]['data'], 1)[0]
                else:
                    self.SchoolOne = random.sample(result, 1)[0]['data'][0]
            if len(self.SchoolOne['km']) == 0:
                continue
            else:
                subject = random.sample(self.SchoolOne['km'], 1)[0]
            url = "http://10.161.165.239:7011/imgsvr/answerpaper?ru=%s&examguid=%s&km=%s" % (self.SchoolOne['ru'], self.SchoolOne['Guid'], subject)
            response = yield tornado.gen.Task(client.fetch, url)
            try:
                results = json.loads(response.body)
            except:
                continue
            url2 = "http://10.161.165.239:7011/imgsvr/asiresponse?ru=%s&examguid=%s&km=%s&viewIndex=1&viewLength=1" % (self.SchoolOne['ru'], self.SchoolOne['Guid'], subject)
            response2 = yield tornado.gen.Task(client.fetch, url2)
            reuslts2 = json.loads(response2.body)
            if len(reuslts2['data']) == 0:
                continue
            else:
                break
        self.writejson({'result': reuslts2['data'], 'PapersInfo': results, 'number': i})


class yuwen7netcc(Handler):
    """获取优质作文数据"""

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        SubjectParam = self.get_json_argument('subject')
        client = tornado.httpclient.AsyncHTTPClient()
        code_url = 'http://10.161.165.239:7011/imgsvr/ru'
        code_result = yield tornado.gen.Task(client.fetch, code_url)
        if code_result.body is None:
            self.writejson({'data': '请检查您的服务是否是开启状态！'})
            return
        else:
            try:
                code_result_json = json.loads(code_result.body)
            except Exception as e:
                self.writejson({'data': e})
                return
        if code_result_json['status'] == 200 and code_result_json['data']:
            schoool_code_list = code_result_json['data']
        self.schoolname_list = [
            '合肥市第六中学',
            '安徽省全椒中学',
            '安徽省和县第一中学',
            '太和县中学',
            '六安市第二中学',
            '巢湖市第二中学',
            '安徽省明光中学',
            '颍上县第一中学',
            '安徽省泾县中学',
            '和县第三中学(和县高级职业中学)',
            '皖西中学',
            '濮阳建业国际学校',
            '淮北一中',
            '安庆市第七中学',
            '吉安县第二中学',
            '新建县第二中学',
            '安徽省阜阳第一中学',
            '桦南县第一中学',
            '江西省修水县英才高级中学',
            '安徽省休宁中学',
            '安徽省和县第二中学',
            '临夏回民中学',
            '鹤岗市第一中学',
            '马鞍山第二中学',
            '安徽省怀宁中学',
            '安庆九一六学校',
            '上饶中学',
            '湖南省双峰县第一中学(双峰一中)',
            '安徽省阜阳市第三中学',
            '安徽省来安中学',
            '南安国光中学',
            '安庆九中',
            '乐桥中学',
            '安徽省南陵县博文中学',
            '南昌市第十九中学（高三）',
            '定远县第二中学',
            '江西省新干中学',
            '巢湖市第一中学',
            '哈尔滨德强学校',
            '淮北市第十二中学',
            '安徽省含山第二中学',
            '上栗县上栗中学',
            '大地学校',
            '安徽省定远中学',
            '永修县第二中学',
            '望江县中学',
            '将军中学',
            '贵阳一中新世界国际学校',
            '安仁县第一中学',
            '当涂县第一中学',
            '安徽省太和县第一中学',
            '湖南省衡阳县第五中学',
            '于都三中',
            '濉溪县第二中学',
            '福建省建阳第一中学',
            '郴州市第二中学',
            '海南省五指山市琼州学院附属中学',
            '奉节县吐祥中学',
            '贵州省大方县第二中学',
            '安庆市第一中学',
            '永修县第一中学',
            '蒙城县第一中学',
            '安徽省宿州市第二中学',
            '仙游金石中学',
            '淮南四中',
            '重庆市万州区新田中学',
            '安徽省怀宁县秀山中学',
            '江西省兴国县第三中学',
            '芜湖市第一中学',
            '皋城中学',
            '滁州中学',
            '安微省怀宁县高河中学',
            '尚志市尚志中学',
            '昆钢一中',
            '泥河镇初级中学',
            '嘉善二中',
            '怀宁县第二中学',
            '怀远县123高考辅导班',
            '宿松中学',
            '仙游金石中学（初中部',
            '怀宁县新安中学',
            '无为一中',
            '江西省丰城中学西校区',
            '安徽省砀山中学',
            '六盘水市第三中学',
            '山西省潞城市第一中学',
            '哈尔滨市第一六二中学',
            '福建省云霄第一中学',
            '清丰县第一高级中学',
            '黔西县树立中学',
            '庐江县第二中学',
            '翰英中学',
            '太原市六十中',
            '汉川一中',
            '安徽省含山中学',
            '马鞍山市第二十二中学',
            '南昌市外国语学校',
            '兴国县第一中学',
            '皖江高中',
            '盘县第二中学',
        ]
        for item in schoool_code_list:
            if item['Name'].encode('utf-8') in self.schoolname_list:
                continue
            else:
                schoool_code_list.remove(item)
        result = []
        for item in schoool_code_list:
            code_url2 = "http://10.161.165.239:7011/imgsvr/exam?ru="+item['Code']
            school_result = yield tornado.gen.Task(client.fetch, code_url2)
            try:
                temp_result = json.loads(school_result.body)
                if temp_result['data'] and temp_result['status'] == 200:
                    result.append(temp_result)
            except:
                continue
        self.SchoolOne = []
        CompositionIdList = []
        for items in result:
            if len(items['data']) > 0:
                self.SchoolOne += items['data']
            # else:
            #     print "SchoolOne", items['data']
            #     self.SchoolOne.append(items['data'])
            # url = "http://10.161.165.239:7011/imgsvr/answerpaper?ru=%s&examguid=%s&km=%s" % (self.SchoolOne['ru'], self.SchoolOne['Guid'], SubjectParam)
            # response = yield tornado.gen.Task(client.fetch, url)
            # try:
            #     results = json.loads(response.body)
            # except:
            #     continue
        for Item in self.SchoolOne:
            url2 = "http://10.161.165.239:7011/imgsvr/asiresponse?ru=%s&examguid=%s&km=%s&viewIndex=1&viewLength=40" % (Item['ru'], Item['Guid'], SubjectParam)
            ResponseData = yield tornado.gen.Task(client.fetch, url2)
            try:
                Result = json.loads(ResponseData.body)
                if len(Result['data']) > 0:
                    for value in Result['data']:
                        if value['ItemString'][-1]['Score'] > 55:
                            CompositionIdList.append({'ImageGuid': value['ImageGuid'], 'code': Item['ru']})
                        else:
                            continue
                else:
                    continue
            except Exception as e:
                continue
        ImagePath = '/var/local/www7netcc/CompositionIdList/'
        for itemss in CompositionIdList:
            code = itemss['code']
            ImageGuid = itemss['ImageGuid']
            imgurl = 'http://10.161.165.239:7011/imgsvr/img?ru=%s&guid=%s' % (code, ImageGuid)
            response = yield tornado.gen.Task(client.fetch, imgurl)
            result = response.body
            ImageFile = open(ImagePath+ImageGuid+'.jpeg', "wb")
            ImageFile.write(result)
            ImageFile.flush()
            ImageFile.close()
        self.writejson({'status': 200, 'length': len(CompositionIdList)})


class GetPapersImage(Handler):
    """根据ImageGuid获取图片"""

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        code = self.get_argument('code')
        ImageGuid = self.get_argument('ImageGuid')
        client = tornado.httpclient.AsyncHTTPClient()
        imgurl = 'http://10.161.165.239:7011/imgsvr/img?ru=%s&guid=%s' % (code, ImageGuid)
        response = yield tornado.gen.Task(client.fetch, imgurl)
        result = response.body
        self.set_header("Content-Type", "image/jpeg")
        self.write(result)


class VerificationUrl(Handler):
    """检测url是否有效"""

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        UrlRule = self.get_argument('rule')
        import urllib
        n = self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': 0}).limit(1000)
        for item in (yield n.to_list(1000)):
            # print self.getPR(item['result']['url'])
            if item['result']['url'][-1] == '/':
                Rule = item['result']['url']+UrlRule
            else:
                Rule = item['result']['url']+'/'+UrlRule
            self.httpExists(Rule)
    self.writejson({'data': 0})

    @tornado.web.asynchronous
    @gen.coroutine
    def httpExists(self, url):
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, url)

        self.code = response.code

        if self.code == 200:
            print url
        else:
            print str(self.code)+'     '+url

    GPR_HASH_SEED = "Mining PageRank is AGAINST GOOGLE'S TERMS OF SERVICE. Y\
    es, I'm talking to you, scammer."

    def google_hash(self, value):
        magic = 0x1020345
        for i in xrange(len(value)):
            magic ^= ord(self.GPR_HASH_SEED[i % len(self.GPR_HASH_SEED)]) ^ ord(value[i])
            magic = (magic >> 23 | magic << 9) & 0xFFFFFFFF
        return "8%08x" % (magic)

    def getPR(self, www):

        try:
            print self.google_hash(www)
            print www
            url = 'http://toolbarqueries.google.com.hk/tbr?client=navclient-auto&ch=%s&features=Rank&q=info:%s&gws_rd=cr' % (self.google_hash(www), www)
            print url
            response = requests.get(url)
            # print response
            rex = re.search(r'(.*?:.*?:)(\d+)', response.text)
            return rex.group(2)
        except:
            return None
