import requests
from  lxml import etree
import pymongo
import time
import datetime
now = datetime.datetime.now()
timeStamp = int(now.timestamp()*1000)
geshi = "%Y%m%d%H%M%S"
time1 = datetime.datetime.strftime(now,geshi)


from proxies import get_ip
import pymongo
import json
headers = {
    "Accept":"application/json",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Connection":"keep-alive",
    "Host":"m.lagou.com",
    "Cookie":"_ga=GA1.2.841469794.1541152606; user_trace_token=20181102175657-a2701865-de85-11e8-8368-525400f775ce; LGUID=20181102175657-a2701fbd-de85-11e8-8368-525400f775ce; index_location_city=%E5%B9%BF%E5%B7%9E; _gid=GA1.2.311675459.1542615716; _ga=GA1.3.841469794.1541152606; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1542634073,1542634080,1542634122,1542634128; "
             "JSESSIONID=ABAAABAAAGCABCC1B87E5C12282CECED77A736D4CD7FA8A; X_HTTP_TOKEN=aae2d9e96d6a68f72d98ab409a933460; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221672c5c65c01c7-0e8e56366a6cce-3a3a5c0e-2073600-1672c5c65c3bf%22%2C%22%24device_id%22%3A%221672c5c65c01c7-0e8e56366a6cce-3a3a5c0e-2073600-1672c5c65c3bf%22%7D; sajssdk_2015_cross_new_user=1; _gat=1; LGSID=20181119231628-167f7db1-ec0e-11e8-a76a-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fm.lagou.com%2Fsearch.html; PRE_LAND=https%3A%2F%2Fm.lagou.com%2Fjobs%2F5219979.html; "
             "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6={timeStamp}; "
             "LGRID={time}-1c458fde-ec0e-11e8-895f-5254005c3644".format(timeStamp=timeStamp,time=time1),
    "Referer":"https://m.lagou.com/search.html",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest",
}

city = "广州"
positionName = "python"
# pageNo = "1"
pageSize = "15"


def get_detail_url(pageNo,proxies):
    base_url = "https://m.lagou.com/search.json?city={city}&positionName={positionName}&pageNo={pageNo}&" \
               "pageSize={pageSize}".format(city=city,positionName=positionName,pageNo=pageNo,pageSize=pageSize)
    res = requests.get(base_url,headers=headers,proxies=proxies)
    content = res.content.decode()
    dict1 = json.loads(content)
    # print(dict1)
    list1 = dict1['content']['data']['page']['result']
    for i in list1:
        yield "https://m.lagou.com/jobs/{}.html".format(i['positionId'])

 # 职位名称  薪资  工作地点  工作年限  学历要求 企业名字   职位描述
def parse_detail(url,proxies):
    # print(url)
    res = requests.get(url,headers=headers,proxies=proxies)
    content = res.content.decode()
    xml = etree.HTML(content)
    postitle = xml.xpath('//div[@class="postitle"]//h2[@class="title"]//text()') #职位名称
    salary = xml.xpath('//span[@class="item salary"]//span[@class="text"]//text()') # 薪资
    workaddress = xml.xpath('//span[@class="item workaddress"]//span[@class="text"]//text()') #工作地点
    workyear = xml.xpath("//span[@class='item workyear']//span//text()")  # 工作年限
    education=xml.xpath('''//span[@class='item education']//span[@class="text"]//text()''') #学历要求
    companyName=xml.xpath('//div[@class="dleft"]//h2//text()') # 公司名字
    detail = xml.xpath("//div[@class='content']/p//text()") #职位描述
    dict1 = {}
    # print(postitle)
    if len(postitle) != 0 :
        dict1['postitle']=postitle[0]
        dict1['salary']=salary[0]
        dict1['workaddress']=workaddress[0]
        dict1['workyear']=workyear[0]
        dict1['education']=education[0].strip()
        dict1['companyName']=companyName[0].strip()
        dict1['detail']=''.join(detail)  #将列表转化为一串字符串
        return dict1
    else:
        print('请求不到数据，重新请求 睡3秒')
        time.sleep(3)
        ip = get_ip()
        proxies = next(ip)
        parse_detail(url,proxies)


def save_mongodb(dict1):
    print(dict1)
    client = pymongo.MongoClient('localhost', 27017)
    lagou_db = client.lagou
    lagou_db = lagou_db.lagou
    lagou_db.insert(dict1)
    print("保存数据库成功")

def run():

    ip = get_ip()
    proxies1 = next(ip)
    proxies2 = next(ip)
    for i in range(100):
        print("开始爬取第{}页".format(i+1))
        for j,url in enumerate(get_detail_url(i,proxies1)):
            dict1 = parse_detail(url,proxies2)
            save_mongodb(dict1)
            print("爬取第{}页第{}条信息成功".format(i+1,j+1))
    print("已经爬取完")




if __name__ == '__main__':
    run()