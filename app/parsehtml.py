# -*- coding:utf-8 -*-
# author: hoster
# -------------------------------------------------------------------------------
import re
import jieba.posseg as pseg
from setting import *
import time
import tornado.web
import tornado.httpclient
from tornado import gen
from Handler import Handler
from auth import jwtauth
"""
抽取单篇文档中的关键词
输入参数：
        data    文档数据  字符串
         zbr    单位配置  列表
         zbj    金额配置  列表
         fzr    人名配置  列表
         zsh    证书配置  列表
         date   日期配置  列表
输出参数：
        result  抽取结果    字典
"""


class ParseHtml():

    # 初始化函数
    def __init__(self, data):
        self.data = data
        self.zbr = ZBR
        self.zbj = ZBJ
        self.fzr = FER
        self.zsh = ZSH
        self.date = DATE

    # 数据定位
    def location(self, param, ty):
        para = str(param).replace('r', '')
        if self.data.find(para) == -1:
            return ''
        else:
            datas = self.data[self.data.find(para):]
            if ty == 1:
                das = datas.split(' ')
                das = ''.join(das)
                return das
            else:
                return datas

    # 去除HTML标签
    def removeAngleBrackets(self, para):
        # 去除所有<>包含的数据
        li = [r'<[\s\S]*?>+', '[\s\S]*?>', '<[\s\S]*?', '：', ':', r'\n', r'\t']
        # res = ''
        for ll in li:
            reM = re.compile(ll, re.I)
            para = reM.sub(' ', para)
        return para.strip(' ')

    # 抽取中标单位
    def parse_department(self):
        # 正则终止条件列表, 范围由小到大
        end_dep = ["子公司", "分公司", "公司", "院", "厂", "商", "<"]
        department = ''
        # 利用关键字和终止条件抽取单位名称
        for te in self.zbr:
            for temp in end_dep:
                # 拼接正则条件
                pa = te+"[\s\S]*?"+temp
                m = re.findall(pa, self.data, re.I)
                # 匹配结果处理
                if len(m) != 0 and m is not " ":
                    mm = str(m[0])
                    reM = re.compile(r'\s*', re.I)
                    t = reM.sub('', te)
                    dep = mm[len(t):]
                    dep = self.removeAngleBrackets(dep)
                    dm = dep.split(" ")
                    # dm = list(reversed(dm))
                    if len(dm) > 0:
                        for tem in dm:
                            if str(tem).find("院") != -1 or str(tem).find("公司") != -1:
                                department = tem
                                break
                            else:
                                continue
                if department is not '':
                    break
                else:
                    continue
            if department is not '':
                break
            else:
                continue
        # 关键字和终止条件抽取单位名称失败，直接正则匹配
        if department == '':
            m = re.findall(r'>[^ -~]*?公司<', self.data, re.I)
            if len(m) != 0:
                for tt in m:
                    if tt.find('代理') == -1 and tt is not '':
                        department = self.removeAngleBrackets(tt)
                        break
                    else:
                        continue
            return department.strip(' ')
        else:
            # if len(department) > 20:
            #     return ''
            # else:
            return department.strip(' ')

    # 抽取中标金额
    def parse_money(self, param1, param2):
        # 正则终止条件
        end_money = ["元", "圆", "<"]
        money = ''
        n_money = ''
        tk = ["壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
        # 统配提取带有单位的金额数据
        pattern = re.compile('((([1-9]{1})(\d{0,2}))((,\d{3})+)(\.\d{1,13})(\s*?)(元|万元))|((([1-9]{1})(\d{0,2}))((,\d{3})+)(\s*?)(元|万元))|(([1-9]{1})(\d{1,10})(\.\d{0,6})(\s*?)(元|万元))|(([1-9]{1})(\.\d{0,6})(\s*?)(万元))|(([1-9]{1})(\d{1,10})(\s*?)(元|万元))')
        search = pattern.search(param1)
        if search:
            mon = search.group()
            money = str(mon)
        # 统配提取结果判断
        if money is not '':
            return money
        else:
            pattern = re.compile('(([1-9]{1})(\d{0,2})((,\d{3})+)(\.\d{1,10}))|(([1-9]{1})(\d{1,10})(\.\d{1,10}))|(\d{5,8})')
            search = pattern.search(param1)
            if search:
                mon = search.group()
                money = str(mon)
            if money is not '':
                m = re.findall(r'万元', self.data, re.I)
                if len(m) != 0:
                    return money+"万元"
                else:
                    mn = money.split('.')
                    if len(mn[0]) > 3:
                        return money+"元"
                    else:
                        return ''
                    # return money+"元"
            else:
                # 统配提取失败处理 关键字和终止条件抽取金额数据
                for temp in param2:
                    for te in end_money:
                        pa = te+"[\s\S]*?"+temp
                        m = re.findall(pa, self.data, re.I)
                        if len(m) != 0 and m is not " ":
                            mm = str(m[0])
                            reM = re.compile(r'\s*?', re.I)
                            t = reM.sub('', te)
                            money = mm[len(t):]
                            money = self.removeAngleBrackets(money)
                            break
                        else:
                            continue
                    if money is not '':
                        break
                    else:
                        continue
                li = [r'（元', r'（万元', r'\(元', r'\(万元', r'（人民币元', r'人民币', r'<[\s\S]*?>']
                if money is not '':
                    money_li = money.split(' ')
                    for mo in money_li:
                        for k in tk:
                            if mo.find(k) != -1:
                                for ll in li:
                                    reM = re.compile(ll, re.I)
                                    n_money = reM.sub(' ', mo)
                                break
                            else:
                                continue
                    if n_money is not ' ':
                        return n_money
                    else:
                        pattern = re.compile('((([1-9]{1})(\d{0,2}))((,\d{3})+)(\.\d{1,13})(<[\s\S]*?>+)(元|万元))|((([1-9]{1})(\d{0,2}))((,\d{3})+)(<[\s\S]*?>+)(元|万元))|(([1-9]{1})(\d{1,10})(\.\d{0,6})(<[\s\S]*?>+)(元|万元))|(([1-9]{1})(\d{1,10})(<[\s\S]*?>+)(元|万元))')
                        search = pattern.search(money)
                        if search:
                            mon = search.group()
                            n_money = str(mon)
                        reM = re.compile(r'<[\s\S]*?>', re.I)
                        n_money = reM.sub('', n_money)
                        return n_money
                else:
                    return ''

    # 金额结果
    def money(self):
        mon = ''
        for tt in self.zbj:
            data = self.location(tt, 0)
            # print "data:", data
            reM = re.compile(r'<[\s\S]*?>+', re.I)
            data = reM.sub(' ', data)
            if data is not '':
                mon = self.parse_money(data, tt)
                if mon is not '':
                    break
                else:
                    continue
        if mon is not '':
            return mon
        else:
            # mon = self.parse_money(self.data, self.zbj)
            # if mon is not '':
            #     return mon
            # else:
            #     return ''
            return ''

    # 抽取建造师姓名
    def parse_name(self, para1, para2):
        name = ''
        end_dep = ["资质", "，", "证书", "注册", r"证号", "<"]
        # 关键字和终止条件抽取建造师姓名
        for temp in para2:
            for te in end_dep:
                pa = te+"[\s\S]*?"+temp
                m = re.findall(pa, para1, re.I)
                if len(m) != 0 and m is not " ":
                    mm = str(m[0])
                    name = mm[len(te):]
                    name = self.removeAngleBrackets(name)
                    break
                else:
                    continue
        # 抽取结果处理，删除噪声数据
        if name is not '':
            if name.find('，') != -1:
                na = name.split('，')
                for tt in na:
                    if tt is not '':
                        name = tt
                        break
                    else:
                        continue
                return name
            else:
                # name = name.replace(u'\xc2\xa0', u' ')
                na = name.split(' ')
                for tt in na:
                    if tt is not ' ':
                        name = tt
                        break
                    else:
                        continue
                li = ['。', '：', '<', '（[\s\S]*?）', '）', '姓名', '和电话', '联系电话[\S\s]+', '(资质|证书|注册|证号)[\S\s]+',
                      '(注册|证书)[\s\S]*?(京|津|冀|晋|蒙|辽|吉|黑|沪|苏|浙|皖|闽|赣|鲁|豫|鄂|湘|粤|桂|琼|渝|川|贵|云|藏|陕|甘|青|宁|新)\d{12}']
                for ll in li:
                    reM = re.compile(ll, re.I)
                    name = reM.sub('', name)
                name = name.strip(' ')
                if 1 < len(name) < 4:
                    return name
                else:
                    return ''
        else:
            return ''

    # 语义提取建造师姓名
    def semantic_name(self):
        name_1 = ''
        name_2 = ''
        noise = Noise
        department = self.parse_department()

        for tt in self.fzr:
            data = self.location(tt, 0)
            if data is not '':
                reM = re.compile(r'<[\s\S]*?>', re.I)
                data = reM.sub('', data)
                dat = data.split(' ')
                das = ''.join(dat)
                words = pseg.cut(das)
                for w in words:
                    if w.flag == 'nr' and w.word not in noise and len(w.word) > 1 and department.find(w.word.encode('utf-8')) == -1:
                        name_1 = w.word
                        break
                    else:
                        continue
            if name_1 != '':
                break
            else:
                continue
        n_data = self.location(r"联系人", 1)
        n_words = pseg.cut(n_data)
        for w in n_words:
                if w.flag == 'nr':
                    name_2 = w.word
                    break
                else:
                    continue
        if name_1 is not '' and name_1 != name_2 and len(name_1) > 1:
            return name_1
        else:
            return ''

    def name(self):
        name = ''
        for tt in self.fzr:
            data = self.location(tt, 0)
            if data is not '':
                name = self.parse_name(data, tt)
                if name is not '':
                    break
                else:
                    continue
        s_name = self.semantic_name()
        if s_name != '':
            return s_name
        elif s_name == '' and name != '':
            return name
        else:
            return ''

    # 抽取建造师证书号
    def parse_num(self, param1, param2):
        num = ''
        # 通配抽取证书号
        #

        reM = re.compile(r'<[\s\S]*?>+', re.I)
        param3 = reM.sub(' ', param1)
        param3 = param3.replace('"', '')
        pattern = re.compile('((京|津|冀|晋|蒙|辽|吉|黑|沪|苏|浙|皖|闽|赣|鲁|豫|鄂|湘|粤|桂|琼|渝|川|贵|云|藏|陕|甘|青|宁|新)[0-9]{12})|((京|津|冀|晋|蒙|辽|吉|黑|沪|苏|浙|皖|闽|赣|鲁|豫|鄂|湘|粤|桂|琼|渝|川|贵|云|藏|陕|甘|青|宁|新)(([\s])|([\s]<[\S\s]>[\s]))+([0-9]{12}))')
        search = pattern.search(param3)
        if search:
            tem = search.group()
            num = str(tem)
        # 通配抽取结果判断
        if num is not '':
            num = self.removeAngleBrackets(num)
            return num
        else:
            # 通配抽取失败 采用关键字和终止条件抽取证书号
            for te in param2:
                pa = te+"[\s\S]*?<"
                m = re.findall(pa, param1, re.I)
                if len(m) != 0 and m is not " ":
                    mm = str(m[0])
                    num = mm[len(te):]
                    num = self.removeAngleBrackets(num)
                    break
                else:
                    continue
            if num is not '' and len(num) > 9:
                return num
            else:
                num_1 = ''
                num_2 = ''
                # 抽取十位数字类型注册号
                pattern = re.compile('[0-9]{10}')
                search = pattern.search(param1)
                if search:
                    tem = search.group()
                    num_1 = str(tem)
                pattern = re.compile('[0-9]{11}')
                search = pattern.search(param1)
                if search:
                    tem = search.group()
                    num_2 = str(tem)
                if num_1 == num_2[:10]:
                    return ''
                else:
                    return num_1

    # 证书号结果
    def number(self):
        num = ''
        for tt in self.zsh:
            data = self.location(tt, 0)
            # print "data:", data
            num = self.parse_num(data, tt)
            if num is not '':
                break
            else:
                continue
        if num is not '':
            pattern = re.compile('[0-9]{10}')
            search = pattern.search(str(num))
            if search is None:
                return ''
            else:
                return num
        else:
            return ''

    # 抽取发布日期
    def parse_date(self, data):
        dates = ''
        # 通配抽取发布日期 格式类型有xxxx年xx月xx日、xxxx年x月x日、xxxx.xx.xx、xxxx.x.x、xxxx/xx/xx、xxxx/x/x、xxxx-xx-xx、xxxx-x-x
        pattern = re.compile('(2[0-9]{3}年([0-9]{1,2})月([0-9]{1,2})日)|(2[0-9]{3}-([0-9]{1,2})-([0-9]{1,2}))|(2[0-9]{3}/([0-9]{1,2})/([0-9]{1,2}))|(2[0-9]{3}\.([0-9]{1,2})\.([0-9]{1,2}))')
        search = pattern.search(data)
        if search:
            Dates = search.group()
            Dates = str(Dates)
            # 解决带有空格的日期数据抽取问题
            if Dates is '':
                    return ''
            else:
                return Dates
        else:
            pattern = re.compile('(2[0-9]{3}([\s]+)年([\s]+)([0-9]{1,2})([\s]+)月([\s]+)([0-9]{1,2})([\s]+)日)')
            search = pattern.search(data)
            if search:
                Dates = search.group()
                Dates = str(Dates)
                return Dates
            else:
                return ''

    # 时间返回结果
    def re_date(self):
        de = ''
        for tt in self.date:
            data = self.location(tt, 1)
            de = self.parse_date(data)
            print de
            if de is not '':
                break
            else:
                continue
        if de is not '':
            return de
        else:
            de = self.parse_date(self.data)
            return de

    # 合并抽取结果，以字典形式保存
    def get_result(self):
        result = {"中标人": self.parse_department(), "金额": self.money(), "建造师": self.name(),
                  "证书": self.number(), "日期": self.re_date()}
        return result

@jwtauth
class GetKeywords(Handler):
    @gen.coroutine
    def get(self):
        cons = self.get_argument('db')
        res = []
        # mongodb 模糊查询
        n = self.dbs.resultcollection.find({'project': cons}).limit(100)
        for item in (yield n.to_list(100)):
            if item['url'] in ['http://zfcg.linyi.gov.cn/sdgp2014/site/read.jsp?colcode=0304&id=868', 'http://www.pyjsgc.com/show.asp?id=10438', 'http://ggzy.yzcity.gov.cn/yzweb/infodetail/?infoid=cb9273b1-9d04-4c49-9fa3-8bac9605b527&categoryNum=004001004001']:
                continue
            if item['result']['content'] is not None:
                reM = re.compile(r'<[\s\S]*?>+', re.I)
                pa = reM.sub(' ', item['result']['content'].encode('utf-8'))
                pa = pa.replace('\n', '')
                result = ParseHtml(pa)
                dic = result.get_result()
                dic['项目名称'] = item['result']['title'].encode('utf-8')
                dic['url'] = item['url']
                for items in dic:
                    print dic[items]
                res.append(dic)
        self.writejson({'data': res})
