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
import math
from tornado import gen
from urllib import unquote
from Handler import BaseHandler,TmpHandle
from Handler import VerifyIP
from bs4 import BeautifulSoup
from auth import jwtauth
from bson.objectid import ObjectId
import requests
import urllib
import datetime

provinceslist = {'北京':'11',
 '天津':'12',
 '河北':'13',
 '山西':'14',
 '内蒙古':'15',
 '辽宁':'21',
 '吉林':'22',
 '黑龙江':'23',
 '上海':'31',
 '江苏':'32',
 '浙江':'33',
 '安徽':'34',
 '福建':'35',
 '江西':'36',
 '山东':'37',
 '河南':'41',
 '湖北':'42',
 '湖南':'43',
 '广东':'44',
 '广西':'45',
 '海南':'46',
 '重庆':'50',
 '四川':'51',
 '贵州':'52',
 '云南':'53',
 '西藏':'54',
 '陕西':'61',
 '甘肃':'62',
 '青海':'63',
 '宁夏':'64',
 '新疆':'65',
 '台湾':'71',
 '香港':'81',
 '澳门':'82',
 '其它':'xx'}

# @jwtauth
@VerifyIP
class GetUrlAll(BaseHandler):
    """获取所有满足要求的url数据"""

    @gen.coroutine
    def prepare(self):
        self.keyword = self.get_argument('keywords')
        self.page = self.get_argument('currentpage', 1)
        self.pagesize = 20
        n = yield self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': -1, 'result.url': {'$regex': self.keyword}}).count()
        res = self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': -1, 'result.url': {'$regex': self.keyword}}).limit(self.pagesize).skip(self.pagesize*(int(self.page)-1))
        self.results = []
        for item in (yield res.to_list(20)):

            self.results.append(item['result'])
        self._data = {'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page}
    def GET(self):
        pass


# @jwtauth
class GetrRuleAll(BaseHandler):
    """获取Rule"""

    @gen.coroutine
    def prepare(self):
        # print dir(self)
        self.classname = self.get_argument('classname', None)
        self.host = self.get_argument('host', None)
        self.page = self.get_argument('currentpage', 1)
        self.pagesize = 10
        query = {}
        if self.classname is not None:
            query['classname'] = self.classname
        if self.host is not None:
            query['host'] = self.host
        n = yield self.dbs.rule.find(query).count()
        res = self.dbs.rule.find(query).limit(self.pagesize).skip(self.pagesize*(int(self.page)-1))
        self.results = []
        for item in (yield res.to_list(20)):
            item['_id'] = str(item["_id"])
            self.results.append(item)

        self._data = {'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page, 'code': 1}
        #self.writejson({'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page})
    def GET(self):
        pass

# addrule
@jwtauth
class AddRule(BaseHandler):
    """添加Url过滤规则"""

    @gen.coroutine
    def post(self):
        rule = self.get_json_argument('rule')
        host = self.get_json_argument('host')
        # classname = self.get_json_argument('classname')
        if rule and host:
            obj = {}
            obj['rule'] = rule
            obj['host'] = host
            # obj['classname'] = classname
            con = self.dbs.rule
            yield con.save(obj)
            self.writejson({'data': repr(obj['_id']), 'code': 1, 'description': '添加成功！'})


class DelRule(BaseHandler):

    @gen.coroutine
    def post(self):
        id = self.get_json_argument('ruleid')
        if id:
            obj = {}
            obj['_id'] = ObjectId(id)
            con = self.dbs.rule
            yield con.remove(obj)
            self.writejson({'data': repr(obj['_id']), 'code': 1, 'description': '删除成功！'})

class getshodan(BaseHandler):
    @gen.coroutine
    def prepare(self):
        import shodan

        iplist = []
        total = 0
        SHODAN_API_KEY = "gy2a9mIJu5QnwyeoQ33n0VUNF39eiwpa"
        query = self.get_argument('hostname')
        api = shodan.Shodan(SHODAN_API_KEY)
        results = api.search(query)
        total = int(results['total'])
        for result in results['matches']: iplist.append({"ip":result['ip_str'],"country":result['location']['country_name']})
        self._data = {"data":iplist,"total":total}

    def GET(self):
        pass

@jwtauth
class getMonth(BaseHandler):

    @gen.coroutine
    def get(self):
        sql  = "SELECT DATE_FORMAT(exam_createtime,'%Y-%m') d, SUM(exam_paper_number) exam_paper_number,SUM(exam_student_number) exam_student_number,SUM(check_score_number_pay) check_score_number_pay,SUM(check_score_number) check_score_number FROM exam_info WHERE 1 GROUP BY d ORDER BY d DESC"
        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        res = []
        import datetime
        for item in result:
            data = {}
            #考试学校数
            thismonth = str(datetime.datetime.strptime(item['d'],'%Y-%m'))
            nextmonth = str((datetime.datetime.strptime(item['d'],'%Y-%m') + datetime.timedelta(31)).replace(day=1))
            sqlschool = "SELECT COUNT(DISTINCT(exam_school_guid)) nums FROM exam_info WHERE exam_createtime >='"+thismonth+"' and exam_createtime< '"+nextmonth+"'"
            self.mdb_cur.execute(sqlschool)
            results = self.mdb_cur.fetchall()
            #注册学生数
            sql_userstudent = "SELECT count(1) nums FROM ru_userstudent s WHERE  s.RU_Userstudent_code in (SELECT RU_User_code FROM ru_user WHERE 1 AND  RU_User_createdTime >='"+thismonth+"' and RU_User_createdTime< '"+nextmonth+"')"
            self.mdb_cur.execute(sql_userstudent)
            result_userstudent = self.mdb_cur.fetchall()
            #考试数
            sql_examcount = "SELECT count(DISTINCT(exam_id)) nums from exam_info WHERE exam_createtime >='"+thismonth+"' and exam_createtime< '"+nextmonth+"'"
            self.mdb_cur.execute(sql_examcount)
            result_examcount = self.mdb_cur.fetchall()
            #订单数,收入
            sql_pay = "SELECT SUM(RU_Order_money) nums,count(1) counts FROM ru_order where RU_Order_state=1 AND RU_Order_payTime >='"+thismonth+"' and RU_Order_payTime< '"+nextmonth+"'"
            self.mdb_cur.execute(sql_pay)
            result_pay = self.mdb_cur.fetchall()
            #微信用户数
            sql_weixinbind = "SELECT count(DISTINCT(RU_UserBind_userCode)) nums FROM ru_userbind WHERE RU_UserBind_createdTime >='"+thismonth+"' and RU_UserBind_createdTime< '"+nextmonth+"'"
            self.mdb_cur.execute(sql_weixinbind)
            result_weixinbind = self.mdb_cur.fetchall()

            data['月份'] = item['d']
            data['试卷数'] = int(item['exam_paper_number'])
            data['查分考生覆盖率'] = str(round(int(item['check_score_number'])/int(item['exam_student_number']),4)*100)+"%"
            data['查分人数'] = int(item['check_score_number'])
            data['付费查分数'] = int(item['check_score_number_pay'])
            data['考生数'] = int(item['exam_student_number'])
            data['考试学校数'] = int(results[0]['nums'])
            data['注册学生数'] = int(result_userstudent[0]['nums'])
            data['微信用户数'] = int(0 if result_weixinbind[0]['nums']==None else result_weixinbind[0]['nums'])
            data['考试数'] = int(result_examcount[0]['nums'])
            data['收入'] = int(0 if result_pay[0]['nums']==None else result_pay[0]['nums'])
            data['订单数'] = int(0 if result_pay[0]['counts']==None else result_pay[0]['counts'])

            res.append(data)
        columnDefs = [{"name":"月份"}]
        for items in data.keys():
            name = {}
            if items!='月份':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "columnDefs": columnDefs,'code': 1})
@jwtauth
class getMonthProvinces(BaseHandler):
    def get(self, *args, **kwargs):
        sql="select * from month_provinces WHERE business_type=1"
        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        res = []
        for item in result:
            data = {}
            data['月份'] = item['month']
            data['试卷数'] = int(item['exam_paper_number'])
            data['查分考生覆盖率'] = str(0 if int(item['exam_student_number']) ==0 else round(int(item['check_score_number'])/int(item['exam_student_number']),4)*100)+"%"
            data['查分人数'] = int(item['check_score_number'])
            data['考试学校数'] = int(item['exam_school_number'])
            data['注册学生数'] = item['reg_userstudent_number']
            data['付费查分数'] = int(item['check_score_number_pay'])
            data['考生数'] = int(item['exam_student_number'])
            data['省份'] = item['provinces']
            data['收入'] = item['income']
            data['订单数'] = item['order_number']
            data['微信用户数'] = item['wx_user_number']
            res.append(data)
        columnDefs = [{"name":"月份"}]
        for items in data.keys():
            name = {}
            if items!='月份':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "columnDefs": columnDefs,'code': 1})

class getMonthProvincesschool(BaseHandler):
    def get(self, *args, **kwargs):
        sql="select * from month_provinces WHERE business_type=2"
        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        res = []
        for item in result:
            data = {}
            data['月份'] = item['month']
            data['试卷数'] = int(item['exam_paper_number'])
            data['查分考生覆盖率'] = str(0 if int(item['exam_student_number']) ==0 else round(int(item['check_score_number'])/int(item['exam_student_number']),4)*100)+"%"
            data['查分人数'] = int(item['check_score_number'])
            data['考试学校数'] = int(item['exam_school_number'])
            data['注册学生数'] = item['reg_userstudent_number']
            data['付费查分数'] = int(item['check_score_number_pay'])
            data['考生数'] = int(item['exam_student_number'])
            data['学校'] = item['school_name']
            data['省份'] = item['provinces']
            data['收入'] = item['income']
            data['订单数'] = item['order_number']
            data['微信用户数'] = item['wx_user_number']
            res.append(data)
        columnDefs = [{"name":"月份"}]
        for items in data.keys():
            name = {}
            if items!='月份':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "columnDefs": columnDefs,'code': 1})

class getMonthProvincessales(BaseHandler):
    def get(self, *args, **kwargs):
        sql="select * from month_provinces WHERE business_type=3"
        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        res = []
        for item in result:
            data = {}
            data['月份'] = item['month']
            data['试卷数'] = int(item['exam_paper_number'])
            data['查分考生覆盖率'] = str(0 if int(item['exam_student_number']) ==0 else round(int(item['check_score_number'])/int(item['exam_student_number']),4)*100)+"%"
            data['查分人数'] = int(item['check_score_number'])
            data['考试学校数'] = int(item['exam_school_number'])
            data['注册学生数'] = item['reg_userstudent_number']
            data['付费查分数'] = int(item['check_score_number_pay'])
            data['考生数'] = int(item['exam_student_number'])
            data['业务员'] = item['school_name']
            data['省份'] = item['provinces']
            data['收入'] = item['income']
            data['订单数'] = item['order_number']
            data['微信用户数'] = item['wx_user_number']
            res.append(data)
        columnDefs = [{"name":"月份"}]
        for items in data.keys():
            name = {}
            if items!='月份':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "columnDefs": columnDefs,'code': 1})

class getday(BaseHandler):
    def get(self, *args, **kwargs):
        sql_totalItems="SELECT count(1) totalItems FROM (SELECT DATE_FORMAT(exam_createtime,'%Y-%m-%d') d FROM exam_info WHERE 1 GROUP BY d ORDER BY d DESC) a"
        sql="SELECT DATE_FORMAT(exam_createtime,'%Y-%m-%d') d,SUM(pay_num) pay_nums,SUM(exam_paper_number) exam_paper_number,SUM(exam_student_number) exam_student_number,SUM(check_score_number_pay) check_score_number_pay,SUM(check_score_number) check_score_number FROM exam_info WHERE 1 GROUP BY d ORDER BY d DESC"
        self.mdb_cur.execute(sql_totalItems)
        totalItems = self.mdb_cur.fetchall()

        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        print len(result)
        res = []
        for item in result:
            data = {}
            data['日期'] = item['d']
            data['试卷数'] = int(item['exam_paper_number'])
            data['查分考生覆盖率'] = str(0 if int(item['exam_student_number']) ==0 else round(int(item['check_score_number'])/int(item['exam_student_number']),4)*100)+"%"
            data['查分人数'] = int(item['check_score_number'])
            # data['考试学校数'] = int(item['exam_school_number'])
            # data['注册学生数'] = item['reg_userstudent_number']
            data['付费查分数'] = int(item['check_score_number_pay'])
            data['考生数'] = int(item['exam_student_number'])
            data['使用赠送学分'] = int(item['check_score_number_pay'])-int(item['pay_nums'])
            # data['省份'] = item['provinces']
            # data['收入'] = item['income']
            # data['订单数'] = item['order_number']
            # data['微信用户数'] = item['wx_user_number']
            res.append(data)
        columnDefs = [{"name":"日期"}]
        for items in data.keys():
            name = {}
            if items!='日期':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "totalItems":totalItems[0]['totalItems'],"columnDefs": columnDefs,'code': 1})

class getexamdata(BaseHandler):
    def get(self, *args, **kwargs):
        sql="SELECT DATE_FORMAT(o.exam_createtime,'%Y-%m-%d') d,t.RU_SchoolTenant_ruCode,p.RU_Examplan_gradeCodeString,o.* FROM exam_info o \
LEFT JOIN ru_schooltenant t on t.RU_SchoolTenant_schoolGuid = o.exam_school_guid \
LEFT JOIN ru_examplan p on p.RU_Examplan_guid = o.exam_id \
 WHERE 1 \
AND p.RU_Examplan_publishedTime>'2014-12'\
ORDER BY d DESC"
        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        res = []
        for item in result:
            data = {}
            data['日期'] = item['d']
            data['试卷数'] = int(item['exam_paper_number'])
            data['查分考生覆盖率'] = str(0 if int(item['exam_student_number']) ==0 else round(int(item['check_score_number'])/int(item['exam_student_number']),4)*100)+"%"
            data['查分人数'] = int(item['check_score_number'])
            # data['考试学校数'] = int(item['exam_school_number'])
            data['联考组织代码'] = item['exam_unit_rucode']
            data['付费查分数'] = int(item['check_score_number_pay'])
            data['考生数'] = int(item['exam_student_number'])
            data['使用赠送学分'] = int(item['check_score_number_pay'])-int(item['pay_num'])
            data['组织代码'] = item['RU_SchoolTenant_ruCode']
            # data['收入'] = item['income']
            data['年级'] = item['RU_Examplan_gradeCodeString']
            # data['微信用户数'] = item['wx_user_number']
            res.append(data)
        columnDefs = [{"name":"日期"}]
        for items in data.keys():
            name = {}
            if items!='日期':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "columnDefs": columnDefs,'code': 1})

@VerifyIP
class getexamdaydata(BaseHandler):
    def get(self, *args, **kwargs):
        sql="SELECT a.*,s.RU_School_schoolname FROM \
(SELECT DATE_FORMAT(exam_createtime,'%Y-%m-%d') d \
,(CASE WHEN exam_unit_rucode LIKE '11%' THEN '北京' \
WHEN exam_unit_rucode LIKE '12%' THEN '天津' \
WHEN exam_unit_rucode LIKE '13%' THEN '河北' \
WHEN exam_unit_rucode LIKE '14%' THEN '山西' \
WHEN exam_unit_rucode LIKE '15%' THEN '内蒙古' \
WHEN exam_unit_rucode LIKE '21%' THEN '辽宁' \
WHEN exam_unit_rucode LIKE '22%' THEN '吉林' \
WHEN exam_unit_rucode LIKE '23%' THEN '黑龙江' \
WHEN exam_unit_rucode LIKE '31%' THEN '上海' \
WHEN exam_unit_rucode LIKE '32%' THEN '江苏' \
WHEN exam_unit_rucode LIKE '33%' THEN '浙江' \
WHEN exam_unit_rucode LIKE '34%' THEN '安徽' \
WHEN exam_unit_rucode LIKE '35%' THEN '福建' \
WHEN exam_unit_rucode LIKE '36%' THEN '江西' \
WHEN exam_unit_rucode LIKE '37%' THEN '山东' \
WHEN exam_unit_rucode LIKE '41%' THEN '河南' \
WHEN exam_unit_rucode LIKE '42%' THEN '湖北' \
WHEN exam_unit_rucode LIKE '43%' THEN '湖南' \
WHEN exam_unit_rucode LIKE '44%' THEN '广东' \
WHEN exam_unit_rucode LIKE '45%' THEN '广西' \
WHEN exam_unit_rucode LIKE '46%' THEN '海南' \
WHEN exam_unit_rucode LIKE '50%' THEN '重庆' \
WHEN exam_unit_rucode LIKE '51%' THEN '四川' \
WHEN exam_unit_rucode LIKE '52%' THEN '贵州' \
WHEN exam_unit_rucode LIKE '53%' THEN '云南' \
WHEN exam_unit_rucode LIKE '54%' THEN '西藏' \
WHEN exam_unit_rucode LIKE '61%' THEN '陕西' \
WHEN exam_unit_rucode LIKE '62%' THEN '甘肃' \
WHEN exam_unit_rucode LIKE '63%' THEN '青海' \
WHEN exam_unit_rucode LIKE '64%' THEN '宁夏' \
WHEN exam_unit_rucode LIKE '65%' THEN '新疆' \
WHEN exam_unit_rucode LIKE '71%' THEN '台湾' \
WHEN exam_unit_rucode LIKE '81%' THEN '香港' \
WHEN exam_unit_rucode LIKE '82%' THEN '澳门' \
ELSE '其它' END) AS provinces,count(1) nums,exam_school_guid FROM exam_info \
WHERE 1 \
GROUP BY d,provinces,exam_school_guid \
) a \
LEFT JOIN ru_school s on s.RU_School_guid = a.exam_school_guid ORDER BY a.d DESC"
        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        res = []
        for item in result:
            data = {}
            data['日期'] = item['d']
            data['省份'] = item['provinces']
            data['学校名称'] = item['RU_School_schoolname']
            data['考试次数'] = int(item['nums'])
            res.append(data)
        columnDefs = [{"name":"日期"}]
        for items in data.keys():
            name = {}
            if items!='日期':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "columnDefs": columnDefs,'code': 1})

@jwtauth
class getexammonthdata(BaseHandler):
    def get(self, *args, **kwargs):
        sql="SELECT a.*,s.RU_School_schoolname FROM \
(SELECT DATE_FORMAT(exam_createtime,'%Y-%m') d \
,(CASE WHEN exam_unit_rucode LIKE '11%' THEN '北京' \
WHEN exam_unit_rucode LIKE '12%' THEN '天津' \
WHEN exam_unit_rucode LIKE '13%' THEN '河北' \
WHEN exam_unit_rucode LIKE '14%' THEN '山西' \
WHEN exam_unit_rucode LIKE '15%' THEN '内蒙古' \
WHEN exam_unit_rucode LIKE '21%' THEN '辽宁' \
WHEN exam_unit_rucode LIKE '22%' THEN '吉林' \
WHEN exam_unit_rucode LIKE '23%' THEN '黑龙江' \
WHEN exam_unit_rucode LIKE '31%' THEN '上海' \
WHEN exam_unit_rucode LIKE '32%' THEN '江苏' \
WHEN exam_unit_rucode LIKE '33%' THEN '浙江' \
WHEN exam_unit_rucode LIKE '34%' THEN '安徽' \
WHEN exam_unit_rucode LIKE '35%' THEN '福建' \
WHEN exam_unit_rucode LIKE '36%' THEN '江西' \
WHEN exam_unit_rucode LIKE '37%' THEN '山东' \
WHEN exam_unit_rucode LIKE '41%' THEN '河南' \
WHEN exam_unit_rucode LIKE '42%' THEN '湖北' \
WHEN exam_unit_rucode LIKE '43%' THEN '湖南' \
WHEN exam_unit_rucode LIKE '44%' THEN '广东' \
WHEN exam_unit_rucode LIKE '45%' THEN '广西' \
WHEN exam_unit_rucode LIKE '46%' THEN '海南' \
WHEN exam_unit_rucode LIKE '50%' THEN '重庆' \
WHEN exam_unit_rucode LIKE '51%' THEN '四川' \
WHEN exam_unit_rucode LIKE '52%' THEN '贵州' \
WHEN exam_unit_rucode LIKE '53%' THEN '云南' \
WHEN exam_unit_rucode LIKE '54%' THEN '西藏' \
WHEN exam_unit_rucode LIKE '61%' THEN '陕西' \
WHEN exam_unit_rucode LIKE '62%' THEN '甘肃' \
WHEN exam_unit_rucode LIKE '63%' THEN '青海' \
WHEN exam_unit_rucode LIKE '64%' THEN '宁夏' \
WHEN exam_unit_rucode LIKE '65%' THEN '新疆' \
WHEN exam_unit_rucode LIKE '71%' THEN '台湾' \
WHEN exam_unit_rucode LIKE '81%' THEN '香港' \
WHEN exam_unit_rucode LIKE '82%' THEN '澳门' \
ELSE '其它' END) AS provinces,count(1) nums,exam_school_guid FROM exam_info \
WHERE 1 \
GROUP BY d,provinces,exam_school_guid \
) a \
LEFT JOIN ru_school s on s.RU_School_guid = a.exam_school_guid ORDER BY a.d DESC"
        self.mdb_cur.execute(sql)
        result = self.mdb_cur.fetchall()
        res = []
        for item in result:
            data = {}
            data['日期'] = item['d']
            data['省份'] = item['provinces']
            data['学校名称'] = item['RU_School_schoolname']
            data['考试次数'] = int(item['nums'])
            res.append(data)
        columnDefs = [{"name":"日期"}]
        for items in data.keys():
            name = {}
            if items!='日期':
                name['name'] = items
                columnDefs.append(name)
        self.writejson({"data": res, "columnDefs": columnDefs,'code': 1})

class test(BaseHandler):
    @gen.coroutine
    def get(self):
        self.string('yjuser12')
        print
        result = yield self.totest.user.find({}).to_list(20)
        for item in result:
            print item
        # self.yjuser1 =
        # self.yjuser2 = string('hdskjhf2')