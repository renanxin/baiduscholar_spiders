# 根据给定的学者的scholarID，爬取专家主页上专家的合作学者的名字、合作次数和合作学者的机构
from scrapy import selector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import pymongo
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
import datetime
import warnings
warnings.filterwarnings('ignore')
ua = UserAgent(path='fake_useragent.json')      # 下载好的浏览器usergent文件
usr_gent = ua.chrome



def get_co_authors(filename):
    '''
        filename: 存储着想要爬取学者的scholarID的文件，每行一个
    '''
    base_url ='http://xueshu.baidu.com/scholarID/%s'
    mongo_url = 'mongodb://admin:123456@localhost:27017/admin'  # mongodb数据库

    author_ = []
    iter = 0
    headers = {'User-Agent': usr_gent}
    cap = DesiredCapabilities.PHANTOMJS.copy()
    for key, value in headers.items():
        cap['phantomjs.page.customHeaders.{}'.format(key)] = value
    # 不载入图片，爬页面速度会快很多
    cap["phantomjs.page.settings.loadImages"] = False
    browser = webdriver.PhantomJS(desired_capabilities=cap)     # 浏览器初始化，当然也可以使用chrome


    with open(filename) as f:
        author = f.readline()
        while author:
            try:
                scholarID = author.strip()
                if iter % 10 ==0:       # 每爬取10位专家存储一次
                    print(iter,datetime.datetime.now())
                    client = pymongo.MongoClient(mongo_url)
                    db = client['professor']
                    for it in author_:
                        db['professor_net'].insert_one(it)
                    author_ = []
                    if iter % 50 == 0:  # 每爬完50位专家重启一次PhantomJS并更换一个新的header
                        browser.quit()
                        new_usr = ua.chrome
                        while new_usr == usr_gent:
                             new_usr = ua.chrome
                         usr_gent = new_usr
                         headers = {'User-Agent': usr_gent}
                         cap = DesiredCapabilities.PHANTOMJS.copy()
                         for key, value in headers.items():
                             cap['phantomjs.page.customHeaders.{}'.format(key)] = value
                         # 不载入图片，爬页面速度会快很多
                         cap["phantomjs.page.settings.loadImages"] = False
                         browser = webdriver.PhantomJS(desired_capabilities=cap)
                try:
                    a = {}
                    a[scholarID] = []
                    browser.get(base_url % scholarID)
                    WebDriverWait(browser,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.p_name')))
                    try:
                        button = browser.find_element_by_css_selector('.co_author_more')
                        button.click()
                        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.co_relmap_wrapper')))
                        sel = selector.Selector(text=browser.page_source)
                        co_authors = sel.css('.co_person_name')
                        for co_author in co_authors:
                            name = co_author.css('div::text').extract_first()   # 获取姓名
                            num = co_author.xpath('./@paper-count').extract_first() # 获取合作次数
                            affiliate = co_author.xpath('./@affiliate').extract_first() # 获取合作机构
                            a[scholarID].append({'name':name,'num':num,'affiliate':affiliate})
                        author_.append(a)
                    except:
                        print('合作学者不足四位')
                    iter += 1
                except:
                    print('error')
                    browser.quit()
                    new_usr = ua.chrome
                    while new_usr == usr_gent:
                        new_usr = ua.chrome
                    usr_gent = new_usr
                    headers = {'User-Agent': usr_gent}
                    cap = DesiredCapabilities.PHANTOMJS.copy()
                    for key, value in headers.items():
                        cap['phantomjs.page.customHeaders.{}'.format(key)] = value
                    # 不载入图片，爬页面速度会快很多
                    cap["phantomjs.page.settings.loadImages"] = False
                    browser = webdriver.PhantomJS(desired_capabilities=cap)
                finally:
                     author = f.readline()
            except:
                browser.quit()




# 给前端使用，用于生成专家网络图，其中返回的数据为线段长度和线段的旋转角度

# 生成合作学者关系网络，参数为专家的scholarID
import math
import pymongo
def get_chart(scholarID):
    client = pymongo.MongoClient('mongodb://admin:123456@localhost:27017/admin')
    db = client['professor']
    scholar = db['professor_net'].find_one({'key':scholarID})
    co_authors_list = []
    if scholar:
        co_authors_list = scholar[scholarID]
        count = len(co_authors_list)
        min_len = 51.2325
        per_len = 102.465 - min_len
        min_count = float(co_authors_list[-1]['num'])
        max_count = float(co_authors_list[0]['num'])
        co = max_count - min_count
        per_rotate = 360/count
        for index,co_author in enumerate(co_authors_list):
            co_author['line_len'] = min_len + (max_count-float(co_author['num']))/co * per_len
            co_author['rotate'] = index * per_rotate - 90
    return co_authors_list

# 生成合作机构关系网络，参数为专家的scholarID
def get_chart_2(scholarID):
    client = pymongo.MongoClient('mongodb://admin:123456@localhost:27017/admin')
    db = client['professor']
    scholar = db['professor_net'].find_one({'key': scholarID})
    co_authors_list = []
    result = []
    if scholar:
        co_authors_list = scholar[scholarID]
        co_organ = {}
        for co_author in co_authors_list:
            if co_author['affiliate'] in co_organ.keys():
                co_organ[co_author['affiliate']] += float(co_author['num'])
            else:
                co_organ[co_author['affiliate']] = float(co_author['num'])
        result = []
        for key in co_organ.keys():
            result.append({'name':key,'num':co_organ[key]})
        result = sorted(result,key = lambda item:sorted(item['num']),reverse=True)
        count = len(result)
        min_len = 51.2325
        per_len = 102.465 - min_len
        min_count = float(result[-1]['num'])
        max_count = float(result[0]['num'])
        co = max_count - min_count
        per_rotate = 360 / count
        for index, co_author in enumerate(result):
            co_author['line_len'] = min_len + (max_count-float(co_author['num'])) / co * per_len
            co_author['rotate'] = index * per_rotate - 90

    return result
