# coding=utf-8

import os,sys,re,time
import hashlib
from fake_useragent import UserAgent
# sys.path.append(os.path.abspath(os.path.dirname("./ThreadPool")))
# os.chdir("./ThreadPool")

import requests, pymysql
from bs4 import BeautifulSoup
from ThreadTool.ThreadPool import ThreadPool,AutoStopThreadPool
from ThreadTool.Task import Task
from ThreadTool.ThreadSafeQueue import ThreadSafeQueue

# 由于任务函数会继续生产任务,所以这里写一个新的线程池将任务队列解耦,从线程池中分离出来
class MyThreadPool(ThreadPool):
    def __init__(self,task_queue,pool_size=0):
        super(MyThreadPool, self).__init__(pool_size)
        self.task_queue=task_queue
        # print(123)

# 咨询 1; 曝光 2;投诉 3;
start_urls={
    "https://www.fx112.com/brokers/rights/consulting/":1,
    "https://www.fx112.com/brokers/rights/exposure/":3,
    "https://www.fx112.com/brokers/rights/complaints/":2
}

# mysql参数
db_conf = {
    "host":"127.0.0.1",
    "user":"root",
    "password":"573234044",
    "charset":"utf8",
    "database":"fx285",
    "cursorclass":pymysql.cursors.DictCursor
}

def timetostr(strTime):
    # 先转换为时间数组
    timeArray = time.strptime(strTime, "%Y-%m-%d %H:%M:%S")

    # 转换为时间戳
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def dl_img(pic_url,dir_path="./uploads/fx112/full"):
    if not pic_url:
        return

    try:
        ua = UserAgent()
        headers = {"User-Agent":ua.random}
        r = requests.get(pic_url,headers=headers)
        if r.status_code==200:
            dir_path = dir_path.replace("\\","/").strip("/")
            real_dir_path = os.path.abspath(dir_path).replace("\\","/")
            m=hashlib.md5()
            m.update(pic_url.encode())
            fn = m.hexdigest()
            fn = fn[8:24]+".jpg"
            real_img_path = real_dir_path+"/"+fn
            with open(real_img_path,"wb") as f:
                f.write(r.content)

            return dir_path.strip(r".")+"/"+fn
        else:
            return False
    except:
        return False

# 构建任务函数
class Crawler:
    def __init__(self,base_url,start_urls,task_queue):
        self.base_url = base_url
        self.start_urls = start_urls
        self.task_queue = task_queue
        self.crawled_list_links = set()
        self.crawled_detail_links = set()

        conn = pymysql.connect(**db_conf)
        cursor = conn.cursor()
        sql = "select url from brokers_art"
        cursor.execute(sql)
        res = cursor.fetchall()
        for url in res:
            self.crawled_detail_links.add(url['url'])

        print(self.crawled_detail_links)

        self.create_db_pool()

    # 生成连接池
    def create_db_pool(self):
        self.db_pool = ThreadSafeQueue(10)      # 生成10个连接
        for i in range(10):
            conn = pymysql.connect(**db_conf)
            self.db_pool.put(conn)
            print("生成mysql连接")

    def start(self):
        for url,type in start_urls.items():
            self.crawl_list(url,type)

    def url_concat(self,uri):
        return self.base_url.strip(r"/")+"/"+uri

    def crawl_detail(self,url,type):
        if url in self.crawled_detail_links:
            print("%s 已经采集过了!" % url)
            return
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"html.parser")
        field = {}

        try:
            field['id'] = re.findall("(\d+)\.html", url)[0]
            field['title'] = soup.find("div",class_="title").find("h2").get_text()
            field['type']=type
            field['mark']=str(soup.find("div",class_="mark"))
            field['content']=str(soup.find("div",class_="content"))
            field['content'] = re.sub("<div class=\"Imgs\">.*?</div>","",field['content'],flags=re.DOTALL)
            field['content'] = re.sub("<p style=\"font-size: 14px; margin-top:40px; line-height: 30px; text-indent: 2em; color: #AEAEAE;\">.*?</p>","",field['content'],flags=re.DOTALL)
            field['url'] = url
            field['reply']= str(soup.find("div",class_="comment-text"))
            img_tags = soup.findAll("div",class_="Imgs")
            field['img']=[]
            for img in img_tags:
                field['img'].append(self.url_concat(img.find("img")['src']))

            field['img']=",".join(field['img'])
            field['create_time']=timetostr(soup.find("p",class_="time").findAll("em")[-1].get_text())
            field['reply_time']=timetostr(soup.find("p",class_="comment-time").get_text())
            field['is_reply']=1
        except BaseException as e:
            print("Error:%s" % url)
            print(e)
            return

        # 爬取图片任务
        print("Img:%s" % url)
        field['img']=self.crawl_imgs(field['img'])


        # 添加数据入库任务
        self.insert_db(field)

        print(field)

    def insert_db(self,field):
        # 从连接池取出连接
        conn = self.db_pool.pop()
        cursor = conn.cursor()
        sql = "insert ignore into brokers_art (id,type,title,mark,content,img,url,reply,create_time,reply_time,is_reply) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cursor.execute(sql,(field["id"],field["type"],field["title"],field["mark"],field["content"],field["img"],field["url"],field["reply"],field["create_time"],field["reply_time"],field["is_reply"]))
            conn.commit()
            self.crawled_detail_links.add(field['url'])
        except BaseException as e :
            print(field['url'])
            print(e)
        cursor.close()
        self.db_pool.put(conn)      # 回收连接

    def crawl_imgs(self,imgs):
        if not imgs:
            return
        imgs = imgs.split(",")
        img_list=[]
        # print(imgs)
        for img in imgs:
            im = dl_img(img)
            if im:
                img_list.append(im)
        imgs=",".join(img_list)

        return imgs

    def crawl_list(self,url,type):   # 爬取列表页
        list_base_url = re.sub(r"\d+.html","",url)
        print(222)
        print(list_base_url)
        print(22)
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"html.parser")

        # 爬取详情页链接
        ul=soup.find("div",class_="content").find("ul")
        li_tags = ul.findAll("li")

        # 爬取下一页列表页链接
        try:
            list_link = list_base_url+soup.find("li",class_="thisclass").find_next().find("a")["href"]
            if list_link in self.crawled_list_links:
                list_link=None
        except:     # 没有下一页的情况
            list_link=None

        print(list_link)
        for li_tag in li_tags:
            # links.append()
            art_link = self.url_concat(li_tag.find("a")["href"])

            # 添加爬取详情任务
            task_detail = Task(self.crawl_detail,type=type,url=art_link)
            self.task_queue.put(task_detail)
            print("添加详情页任务 %s " % art_link)

        # 添加爬取列表页任务
        if list_link:
            task_list = Task(self.crawl_list, list_link, type)
            self.task_queue.put(task_list)
            self.crawled_list_links.add(list_link)
            print("添加列表页任务 %s " % list_link)


# 创建任务队列
task_queue = ThreadSafeQueue()

# 创建连接池
pool = MyThreadPool(task_queue)

# 创建线程并开始运行线程
pool.init_thread()
pool.start()

# # 开始往任务队列中放任务
crawler = Crawler(base_url="https://www.fx112.com",start_urls=start_urls,task_queue=task_queue)
crawler.start()

# crawler.crawl_detail("https://www.fx112.com/brokers/rights/complaints/5144.html",3)