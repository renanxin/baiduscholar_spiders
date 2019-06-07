import pymongo
from scrapy import Selector
from urllib import  request
from pyquery import PyQuery as pq
import datetime
import time
import random
import os
import requests
from fake_useragent import UserAgent

location = os.getcwd() + '/fake_useragent.json'
ua = UserAgent(path=location)
usr_gent = ''


base_url = 'http://xueshu.baidu.com/usercenter/paper/show?paperid=%s'
req = request.Request('http://xueshu.baidu.com/usercenter/paper/show?paperid=48ea05ae09a4b81ff9243c74ede5c338')
req.add_header('User-Agent', ua.chrome)
mongo_url = "mongodb://localhost:27017"

def is_Chinese(word):
    '''
        判断给定的word是否包含中文，如果包含返回True
    '''
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def get_paperid(ID):
    '''
        根据给定的scholarID获取专家所对应的全部论文的paperID，返回结果为包含所有paperID的集合，scholarID和专家的姓名
    '''
    client = pymongo.MongoClient(mongo_url)
    db = client['author']
    result = db['authors'].find_one({'scholarID':ID})
    paper_set = None
    scholarID = None
    name = None
    if result:
        paper_set = result['papers']
        scholarID = result['scholarID']
        name = result['name']
    else:
        paper_set = None
        scholarID = None
        name = None
    client.close()
    return paper_set,scholarID,name


# 根据给定的author.txt获取文档中存储的所有scholarID学者对应的papers
def get_all_papers():
    iter = 0
    papers = []
    with open('author.txt') as f:
        ID = f.readline().strip()
        while ID:
            paper_set,scholarID,author_name = get_paperid(ID)
            if paper_set == None:
                continue
            for paper_id in paper_set:
#                每100位专家获取打印一次
#                if iter % 100 ==0 :
#                    print(datetime.datetime.today(),''*6,iter)
#                    pass
                iter += 1
                if iter % 30 == 0:      # 每30位专家换一次浏览器的user-gent
                    new_gent = ua.chrome
                    while new_gent == usr_gent:
                        new_gent = ua.chrome
                    usr_gent = new_gent
                page_resource = requests.get('http://xueshu.baidu.com/usercenter/paper/show',params={'paperid':paper_id},
                                             headers = {'User-Agent': usr_gent})

                if page_resource:
                    paper = {}
                    data = page_resource.text
                    select = Selector(text=data)
                    paper['paperid'] = paper_id
                    paper['title'] = select.css('.main-info h3 a::text').extract_first()
                    paper['abstract'] = select.css('.main-info .abstract_wr .abstract::text').extract_first()
                    if paper['abstract']:
                        paper['abstract'] = pq('<html>' + paper['abstract'] + '</html>').text()
                    paper['authors'] = []
                    authors = select.css('.main-info .c_content .author_wr .author_text span')
                    for author in authors:
                        paper['authors'].append(author.css('a::text').extract_first())
                    paper['quote_num'] = select.css('.main-info .c_content .ref-wr-num a::text').extract_first()
                    paper['date'] = select.css('.journal_content::text').extract_first()
                    if paper['date']:
                        paper['date'] = paper['date'].replace(' ', '').replace('\n', '')
                    if paper['quote_num']:
                        paper['quote_num'] = paper['quote_num'].replace(' ', '').replace('\n', '')
                    if paper['abstract']:
                        if paper['title'] and is_Chinese(paper['title']):
                            paper['abstract'] = paper['abstract'].replace(' ', '').replace('\n', '')
                        else:
                            paper['abstract'] = paper['abstract'].replace('\n', '')
                    key_words = []
                    keys = select.css('.c_content .kw_main span')
                    for key in keys:
                        key_word_ = key.css('a::text').extract_first()
                        key_words.append(key_word_)
                    paper['key_words'] = key_words
                    paper['resource'] = select.css('.container_right .journal_title::text').extract_first()
                    button = select.css('.paper_src_wr a[class="src_tabitem savelink-tar"]')  # 用于判断是否存在免费资源
                    if button != []:
                        sources = select.css('.paper_src_wr #savelink_wr span a')
                        free_sources = []
                        for source in sources:
                            free_source = source.xpath('./@href').extract_first()
                            free_sources.append(free_source)
                            if (len(free_sources) > 9):    break
                        paper['free_sources'] = free_sources
                    else:
                        paper['free_source'] = None
                    paper['authors_id'] = {}
                    papers.append(paper)
                    time.sleep(random.random() * 0.5)

            print("***\n***\n***\n")
            client = pymongo.MongoClient(mongo_url)
            db = client['author_paper']
            for item in papers:
                author_results = db['paper'].find({'paperid':item['paperid']})
                results = []
                for p in author_results:
                    results.append(p)
                if len(results) == 0:
                    item['authors_id'][author_name] = scholarID
                    db['paper'].insert_one(item)
                else:
                    authors_id = results[0]['authors_id']
                    authors_id[author_name]=scholarID
                    db['paper'].update_one({'paperid':item['paperid']},{'$set':{'authors_id':authors_id}})

            papers = []
            time.sleep(random.random()*1)

            ID = f.readline().strip()
