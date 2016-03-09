# -*- coding:utf-8 -*-
'''
======================
@author Vincent
======================
'''
import tornado.web
import tornado.httpclient, textwrap, urllib2, re
from tornado import gen
from parsehtml import *
from setting import *


class ReverseHandler(tornado.web.RequestHandler):
    def head(self, frob, frob_id):
        # frob = retrieve_from_db(frob_id)
        print int(frob_id)
        if int(frob_id) > 20:
            self.set_status(200)
        else:
            self.set_status(2001)

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error." % status_code)

    def get(self, input, ints):

        temp = {"data": input[::-1]}

        self.write(temp)


class BookModule(tornado.web.UIModule):
    def render(self, book):
        return self.render_string(
            "modules/book.html",
            book=book,
        )

    def css_files(self):
        return "/static/css/recommended.css"

    def javascript_files(self):
        return "/static/js/recommended.js"


class WrapHandler(tornado.web.RequestHandler):

    def post(self):
        text = self.get_argument('url')
        width = self.get_argument('width', 40)
        self.write(textwrap.fill(text, int(width)))


class ParseHtmls(tornado.web.RequestHandler):

    def post(self):
        content = self.get_argument('content').encode('utf-8')
        print content
        result = ParseHtml(content, ZBR, ZBJ, FER, ZSH,  DATE)
        self.write(result.get_result())


class IndexHandler(tornado.web.RequestHandler):

    # @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        # query = self.get_argument('keywords')
        res = []
        # mongodb 模糊查询
        n = self.application.db.resultcollection.find({'project': 'test5'})
        for item in (yield n.to_list(length=100)):
            # print item['result']['content']
            if item['result']['content'] is not None:
                result = ParseHtml(item['result']['content'].encode('utf-8'), ZBR, ZBJ, FER, ZSH,  DATE)
                dic = result.get_result()
                dic['项目名称'] = item['result']['title'].encode('utf-8')
                dic['url'] = item['url']
                res.append(dic)

        self.write({'data': res})


class HtmlExtract:
    """docstring for HtmlExtract"""
    def __init__(self, url='', blkSize=3):
        # super(HtmlExtract, self).__init__()
        '''
         * record the web page's url
         * @type string
        '''
        self.url = url
        '''
        * record the web page's source code
        * @type string
        '''
        self.rawPageCode = ''

        '''
         * record the text after preprocessing
         * @type list
        '''
        self.textLines = []

        '''
         * record the length of each block
         * @type list
        '''
        self.blksLen = []

        '''
         * record the final extracted text
         * @type string
        '''
        self.text = ''

        '''
         * set the size of each block ( regards how many single lines as a block )
         * it is the only parameter of this method
         * @type int
        '''
        self.blkSize = blkSize

        '''
         * record whether the web page's encoding is 'gb*'
         * @var bool
        '''
        self.isGB = True

    def getPageCode(self):
            response = urllib2.urlopen(self.url)
            self.rawPageCode = response.read()

    def procEncoding(self):
        # print self.rawPageCode
        patt = re.compile(r'[\s\S]*charset(\s*?)=(\s*?)[\"]?(.*?)\"', re.I)
        if patt.match(self.rawPageCode) is None:
            self.isGB = False
        else:
            tmp = patt.match(self.rawPageCode).group(3)[:2]
            if tmp.upper() != 'GB':
                self.isGB = False
                # replacement = 'charset="GBK"'
                # self.rawPageCode = \
                # re.sub(r'charset[\s]*?=[\s]*?\".*?\"',replacement,self.rawPageCode)
            else:
                self.isGB = True

    def preProcess(self):
        content = self.rawPageCode
        # DTD information
        content = re.sub(r'<!DOCTYPE[\s\S]*?>', '', content)
        # 2. HTML comment
        content = re.sub(r'<!--[\s\S]*?-->', '', content)
        # 3. Java Script
        content = re.sub(r'<script[\s\S]*?>[\s\S]*?<\/script>', '', content)
        # 4. CSS
        content = re.sub(r'<style[\s\S]*?>[\s\S]*?<\/style>', '', content)
        # 5. HTML TAGs
        content = re.sub(r'<[\s\S]*?>', '', content)
        # 6. some special charcaters
        content = re.sub(r'&.{1,5};|&#.{1,5};', '', content)
        return content

    """
    Split the preprocessed text into lines by '\n'
    after replacing "\r\n", '\n', and '\r' with '\n'
    @param string @rawText
    @return void
    """

    def getTextLines(self, rawText):
        # do some replacement
        adict = {"\r\n": r'\n', "\n": r'\n', "\r": '\n'}
        rawText = self.multiple_replace(rawText, adict)
        lines = rawText.split(r'\n')
        for line in lines:
            # remove the blanks in each line
            tmp = re.sub('\s+', '', line)
            self.textLines.append(tmp)

    def multiple_replace(self, text, adict):
        rx = re.compile('|'.join(map(re.escape, adict)))

        def one_xlat(match):
            return adict[match.group(0)]
        return rx.sub(one_xlat, text)

        '''
        Calculate the blocks' length
        @return void
        '''
    def calBlocksLen(self):
        textLineNum = len(self.textLines)
        blkLen = 0
        # print self.blkSize,self.textLines
        for i in xrange(self.blkSize):
            blkLen += len(self.textLines[i])
        self.blksLen.append(blkLen)

        # calculate the other block's length using Dynamic Programming method
        for i in xrange(1, (textLineNum - self.blkSize)):
            blkLen = self.blksLen[i-1] + len(self.textLines[i - 1 + self.blkSize]) - len(self.textLines[i - 1])
            self.blksLen.append(blkLen)

    def getPlainText(self):
        self.getPageCode()
        self.procEncoding()
        preProcText = self.preProcess()
        self.getTextLines(preProcText)
        self.calBlocksLen()
        start = end = -1
        i = maxTextLen = 0

        blkNum = len(self.blksLen)
        while (i < blkNum):
            while (i < blkNum and self.blksLen[i] == 0):
                i += 1
            if i >= blkNum:
                break
            tmp = i

            curTextLen = 0
            portion = ''
            while (i < blkNum and self.blksLen[i] != 0):
                if self.textLines[i] != '':
                    portion += self.textLines[i]
                    portion += '<br />'
                    curTextLen += len(self.textLines[i])
                i += 1
            if curTextLen > maxTextLen:
                self.text = portion
                maxTextLen = curTextLen
                start = tmp
                end = i - 1

        return self.text
