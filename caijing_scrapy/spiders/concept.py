# -*- coding: utf-8 -*-
# ########################################
# 概念板块爬取 腾讯
# by wooght
# 2017 -11
# ########################################
import scrapy
from scrapy.http import Request
from model import T

class ConceptSpider(scrapy.Spider):
    name = 'concept'
    allowed_domains = ['stock.gtimg.cn']
    start_urls = ['http://stock.gtimg.cn/data/view/bdrank.php?&t=02/averatio&p=1&o=0&l=400&v=list_data']
    bkqt_url_models = "http://stock.gtimg.cn/data/index.php?appn=rank&t=pt%s/chr&p=1&o=0&l=400&v=list_data"
    bkqt_name_models = "http://qt.gtimg.cn/q=%s&r=104406769"
    company_dict = {}

    #动态修改配置内容
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 654,           #处理普通静态页面
           'caijing_scrapy.middlewares.Newsmiddlewares.WooghtDownloadMiddleware': None,
        },
        'LOG_LEVEL':'WARNING',
        'CONCURRENT_REQUESTS_PER_DOMAIN':1  #并发为1 只有序进行
    }

    #过程
    #1:读取概念ID
    #2:读取概念ID下 股票ID
    #3:股票对应概念ID组合
    #4:修改股票对应concept
    #5:读取概念ID对应的名字

    def parse(self, response):
        bkqt = response.body.decode('utf8')[4:-3]
        tmp = bkqt.split("data:'")
        bkqt_nums = tmp[1].split(",")
        bkqt_id = [];for_num = 0;bkqu_len = len(bkqt_nums)
        #读取概念ID下对应的股票ID
        for col in bkqt_nums:
            for_num+=1
            bkqt_id.append(col[4:])
            url = self.bkqt_url_models%(bkqt_id[-1])
            if(for_num==bkqu_len):
                metas = {'concept_id':bkqt_id[-1],'last':True}
            else:
                metas = {'concept_id':bkqt_id[-1]}
            wnews_request = Request(url,meta=metas,callback=self.company_parse,priority=int(100000/for_num)) #priority 优先级,数字越大,优先级越高
            yield wnews_request
        print(bkqt_id)
        print('get_name run...')

        #读取概念ID对应概念名称
        new_formart = []
        for_num = 1
        d = T.listed_concept.delete()   #删除原油概念数据
        r = T.conn.execute(d)
        for item in bkqt_id:
            new_formart.append("bkhz"+item)
            #接口一次最多查询15条数据
            if(for_num%15==0 or for_num==len(bkqt_id)-1):
                url_formart = ",".join(new_formart)
                urls = self.bkqt_name_models%(url_formart)
                wnews_request = Request(url=urls,callback=self.bkqt_parse,dont_filter=True)
                new_formart = []
                yield wnews_request
            for_num+=1

    def bkqt_parse(self,response):
        bkqt_str = response.body.decode('gbk').strip().split(';')
        bkqt_dict = []
        del bkqt_str[-1]
        for i in bkqt_str:
            tmp_dict = {}
            tmp = i.split('"')
            tmp2 = tmp[1].split('~')
            tmp_dict['conceptid'] = tmp2[0]
            tmp_dict['name'] = tmp2[1]
            bkqt_dict.append(tmp_dict)
        # self.bkqt_dict = dict(self.bkqt_dict,**bkqt_dict)     #dict合并
        self.update_concept(bkqt_dict)

    def company_parse(self,response):
        list_data = response.body.decode('utf8')[4:-3]
        tmp = list_data.split("data:'")
        company_list = tmp[1].split(",")
        print(company_list)
        for cmp in company_list:
            shsz = cmp[0:2]
            codeid = cmp[2:]
            if(codeid not in self.company_dict.keys()):
                self.company_dict[codeid] = response.meta['concept_id']
            else:
                self.company_dict[codeid]+=','+response.meta['concept_id']
        if('last' in response.meta.keys()):
            print('lastd...')
            self.update_company()

    def update_concept(self,bkqt):
        print(bkqt)
        i = T.listed_concept.insert()
        r = T.conn.execute(i,bkqt)
        if(r.rowcount>0):
            print('concept insert success:',r.rowcount)

    def update_company(self):
        for item in self.company_dict.items():
            print(item,'update run ....')
            u = T.listed_company.update().where(T.listed_company.c.codeid==item[0]).values(concept_id=item[1])
            r = T.conn.execute(u)
