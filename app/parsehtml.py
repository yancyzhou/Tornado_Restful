# -*- encoding: utf-8 -*-
# author: hoster
# -------------------------------------------------------------------------------
import re

import jieba.posseg as pseg
from setting import *

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
    def __init__(self, data, zbr, zbj, fzr, zsh, date):
        self.data = data
        self.zbr = zbr
        self.zbj = zbj
        self.fzr = fzr
        self.zsh = zsh
        self.date = date

    # 数据定位
    def location(self, param):
        para = str(param).replace('r', 'u')
        # para = str(para).replace(' ', '')
        if self.data.find(para) == -1:
            return ''
        else:
            datas = self.data[self.data.find(para):]
            datas = datas.split(' ')
            datas = ''.join(datas)
            return datas

    # 去除HTML标签
    def removeAngleBrackets(self, para):
        # 去除所有<>包含的数据
        li = [r'<[\s\S]*?>+', '[\s\S]*?>', '<[\s\S]*?', '：', '\n']
        # res = ''
        for ll in li:
            reM = re.compile(ll, re.I)
            para = reM.sub('', para)
        return para.strip(' ')

    # 抽取中标单位
    def parse_department(self):
        # 正则终止条件列表, 范围由小到大
        end_dep = ["子公司", "分公司", "公司", "院", "中心", "厂", "商", "<"]
        department = ''
        # 利用关键字和终止条件抽取单位名称
        for temp in end_dep:
            for te in self.zbr:
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
                    if len(dm) > 0:
                        for tem in dm:
                            if str(tem).find("公司") != -1 or str(tem).find("院") != -1 or str(tem).find("中心") != -1:
                                department = tem
                                break
                            else:
                                continue
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
    def parse_money(self, param):
        # 正则终止条件
        end_money = ["元", "圆", "<"]
        money = ''
        n_money = ''
        tk = ["壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
        # 统配提取带有单位的金额数据
        pattern = re.compile('((([1-9]{1})(\d{0,2}))((,\d{3})+)(\.\d{1,13})(元|万元))|((([1-9]{1})(\d{0,2}))((,\d{3})+)(元|万元))|(([1-9]{1})(\d{1,10})(\.\d{0,6})(元|万元))|(([1-9]{1})(\d{1,10})(元|万元))')
        search = pattern.search(param)
        if search:
            mon = search.group()
            money = str(mon)
        # 统配提取结果判断
        if money is not '':
            return money
        else:
            pattern = re.compile('(([1-9]{1})(\d{0,2})((,\d{3})+)(\.\d{1,10}))|(([1-9]{1})(\d{3,10})(\.\d{1,10}))')
            search = pattern.search(param)
            if search:
                mon = search.group()
                money = str(mon)
            if money is not '':
                m = re.findall(r'万元', self.data, re.I)
                if len(m) != 0:
                    return money+"万元"
                else:
                    return money+"元"
            else:
                # 统配提取失败处理 关键字和终止条件抽取金额数据
                for temp in end_money:
                    for te in self.zbj:
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
                    for k in tk:
                        if money.find(k) != -1:
                            for ll in li:
                                reM = re.compile(ll, re.I)
                                n_money = reM.sub(' ', money)
                            break
                        else:
                            continue
                    if n_money is not '':
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
            data = self.location(tt)
            if data is not '':
                mon = self.parse_money(data)
                if mon is not '':
                    break
                else:
                    continue
        if mon is not '':
            return mon
        else:
            mon = self.parse_money(self.data)
            if mon is not '':
                return mon
            else:
                return ''

    # 抽取建造师姓名
    def parse_name(self, para):
        name = ''
        end_dep = ["资质", "，", "证书", "注册", r"证号", "<"]
        # 关键字和终止条件抽取建造师姓名
        for temp in end_dep:
            for te in self.fzr:
                pa = te+"[\s\S]*?"+temp
                m = re.findall(pa, para, re.I)
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
                name = name.replace('\xc2\xa0', ' ')
                na = name.split(' ')
                for tt in na:
                    if tt is not ' ':
                        name = tt
                        break
                    else:
                        continue
                li = ['。', '：', '<', '（[\s\S]*?）', '姓名', '和电话', '联系电话[\S\s]+', '(资质|证书|注册|证号)[\S\s]*',
                      '(注册|证书)[\s\S]*?(京|津|冀|晋|蒙|辽|吉|黑|沪|苏|浙|皖|闽|赣|鲁|豫|鄂|湘|粤|桂|琼|渝|川|贵|云|藏|陕|甘|青|宁|新)\d{12}']
                for ll in li:
                    reM = re.compile(ll, re.I)
                    name = reM.sub('', name)
                name = name.strip(' ')
                if 1 < len(name) < 10:
                    return name
                else:
                    return ''
        else:
            return ''

    def semantic_name(self):
        name_1 = ''
        name_2 = ''
        noise = [u'候选人', u'通知书']
        for tt in self.fzr:
            data = self.location(tt)
            if data is not '':
                reM = re.compile(r'<[\s\S]*?>', re.I)
                data = reM.sub('', data)
                dat = data.split(' ')
                das = ''.join(dat)
                words = pseg.cut(das)
                for w in words:
                    if w.flag == 'nr' and w.word not in noise:
                        name_1 = w.word
                        break
                    else:
                        continue
            if name_1 is not '':
                break
            else:
                continue
        n_data = self.location(r"联系人")
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
            data = self.location(tt)
            if data != '':
                name = self.parse_name(data)
                if name is not '':
                    break
                else:
                    continue
        s_name = self.semantic_name()
        if s_name is not '':
            return s_name
        elif s_name is '' and name is not '':
            return name
        else:
            return ''

    # 抽取建造师证书号
    def parse_num(self, param):
        num = ''
        # 通配抽取证书号
        pattern = re.compile('((京|津|冀|晋|蒙|辽|吉|黑|沪|苏|浙|皖|闽|赣|鲁|豫|鄂|湘|粤|桂|琼|渝|川|贵|云|藏|陕|甘|青|宁|新)[0-9]{12})|((京|津|冀|晋|蒙|辽|吉|黑|沪|苏|浙|皖|闽|赣|鲁|豫|鄂|湘|粤|桂|琼|渝|川|贵|云|藏|陕|甘|青|宁|新)(([\s])|([\s]?<[\S\s]>[\s]?))+([0-9]{12}))')
        search = pattern.search(param)
        if search:
            tem = search.group()
            num = str(tem)
        # 通配抽取结果判断
        if num is not '':
            num = self.removeAngleBrackets(num)
            return num
        else:
            # 通配抽取失败 采用关键字和终止条件抽取证书号
            for te in self.zsh:
                pa = te+"[\s\S]*?<"
                m = re.findall(pa, param, re.I)
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
                search = pattern.search(self.data)
                if search:
                    tem = search.group()
                    num_1 = str(tem)
                pattern = re.compile('[0-9]{11}')
                search = pattern.search(self.data)
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
            data = self.location(tt)
            num = self.parse_num(data)
            if num is not '':
                break
            else:
                continue
        if num is not '':
            return num
        else:
            return ''

    # 抽取发布日期
    def parse_date(self):
        dates = ''
        # 通配抽取发布日期 格式类型有xxxx年xx月xx日、xxxx年x月x日、xxxx.xx.xx、xxxx.x.x、xxxx/xx/xx、xxxx/x/x、xxxx-xx-xx、xxxx-x-x
        pattern = re.compile('([0-9]{4}年([0-9]{1,2})月([0-9]{1,2})日)|([0-9]{4}-([0-9]{1,2})-([0-9]{1,2}))|([0-9]{4}/([0-9]{1,2})/([0-9]{1,2}))|([0-9]{4}\.([0-9]{1,2})\.([0-9]{1,2}))')
        search = pattern.search(self.data)
        if search:
            dates = search.group()
            dates = str(dates)
            # 解决带有空格的日期数据抽取问题
            if dates is '':
                pattern_1 = re.compile('([0-9]{4}[\s]+年[\s]+([0-9]{1,2})[\s]+月[\s]+([0-9]{1,2})[\s]+日)')
                search_1 = pattern_1.search(self.data)
                if search_1:
                    dates = str(dates)
                    dates = dates.replace("年", "-")
                    dates = dates.replace("月", "-")
                    dates = dates.replace("日", " ")
                    return dates
                else:
                    return ''
            else:
                dates = dates.replace("年", "-")
                dates = dates.replace("月", "-")
                dates = dates.replace("日", " ")
                return dates
        else:
            return ''

    # 合并抽取结果，以字典形式保存
    def get_result(self):
        result = {"中标人": self.parse_department(), "金额": self.money(), "建造师": self.name(),
                  "证书": self.number(), "日期": self.parse_date()}
        print "中标人:", result["中标人"], len(result["中标人"])
        print "金额:", result["金额"]
        print "建造师:", result["建造师"]
        print "证书:", result["证书"]
        print "日期:", result["日期"]
        return result

# if __name__ == '__main__':
#     prasehtml = ParseHtml(con, ZBR, ZBJ, FER, ZSH,  DATE)
#     prasehtml.get_result()
