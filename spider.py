#encoding=utf-8
from urllib import request
from urllib import parse
from fake_useragent import UserAgent
import random
import time
import re
import csv

class DouBanSpider :
    def __init__(self, url) :
        self.baseurl = url
    
    def get_ua(self) :
        ua = UserAgent()
        headers = {
        'User-Agent' : ua.chrome
        }
        return headers
    
        
    def get_html(self, url) :
        info_list_top = []
        info_list_films = []
        info_list_actors = []
        info_list_comments = []
        # 发送请求
        req = request.Request(url=url, headers=self.get_ua())
        response = request.urlopen(req)
        html = response.read().decode('utf-8')
        # 爬取top250 
        re_exp = '<div class="info".*?href="(.*?)"' +\
                 '.*?<span class="title">(.*?)</span>' +\
                 '.*?<div class="bd".*?<p class="">.*?(\d*)&nbsp;/&nbsp;(.*?)&nbsp;/&nbsp;(.*?)\n.*?</p>'
        info_list_top = self.parse_html(str=html, re_exp=re_exp)
        
        for info in info_list_top : 
            film_title = info[1]
            
            req = request.Request(url=info[0], headers=self.get_ua())
            response = request.urlopen(req)
            html = response.read().decode('utf-8')
        
            # 爬取简介,影评链接,演职员列表
            comment_num = 2
            re_exp =  '<div class="indent".*?<span class="all hidden">\n(.*?)</span>' +\
                      '.*?<div id="celebrities".*?<a href="(.*?)"'+\
                      '.*?<div class="main-bd".*?<h2><a href="(.*?)"' * comment_num +\
                      '|<div class="indent".*?<span property.*?>\n(.*?)</span>' +\
                      '.*?<div id="celebrities".*?<a href="(.*?)"'+\
                      '.*?<div class="main-bd".*?<h2><a href="(.*?)"' * comment_num
            info_tuple_film = self.parse_html(str=html, re_exp=re_exp)[0]
     
            # 爬取内容处理
            # 删除空元组
            if(info_tuple_film[0] == '') :
                info_tuple_film = info_tuple_film[comment_num+2:]
            else :
                info_tuple_film = info_tuple_film[:comment_num+2]
            # 删除多余字符
            info_list_tmp = list(info_tuple_film)
            info_list_tmp[0] = info_list_tmp[0].replace('\n', '').replace(' ', '').replace('\u3000','').replace('<br />', '').replace('<br/>', '')
            info_list_tmp.insert(0, film_title)
            info_tuple_film = tuple(info_list_tmp)
            info_list_films.append(info_tuple_film)
            
            # 爬取演职员列表内容
            actor_ref = info_tuple_film[2]
            req = request.Request(url='https://movie.douban.com'+actor_ref, headers=self.get_ua())
            response = request.urlopen(req)
            html = response.read().decode('utf-8') 
            
            # 分三次进行解析
            # 获得演员部分范围
            re_exp = 'Cast</h2>.*?<ul class="cele.*?line">(.*?)</ul>' 
            actor_list_range_str = self.parse_html(str=html, re_exp=re_exp)[0]
            # 获得每个演员信息
            re_exp = '<li class="cele.*?<div class="info".*?title="(.*?)"'+\
                     '.*?title="(.*?)"'+\
                     '.*?<span class="works">(.*?)</span>'
            actors_list = self.parse_html(str=actor_list_range_str, re_exp=re_exp)
            # 获得演员代表作
            for i in range(0, len(actors_list)) :
                works_range_str = actors_list[i][2]
                re_exp = 'title=(.*?)>'
                works_list = self.parse_html(str=works_range_str, re_exp=re_exp)
                actor_list = list(actors_list[i])
                actor_list.pop()
                actor_list = actor_list + works_list
                actors_list[i] = tuple(actor_list)
            
            info_list_actors.append(tuple(['<'+film_title+'>']))
            for actor in actors_list :
                info_list_actors.append(actor)
            actors_list.insert(0, film_title)
            info_list_actors.append(tuple(['</'+film_title+'>']))
          
                                
            # 爬取影评内容
            comments_list = []
            comments_list.append(film_title)
            for comment_ref in info_tuple_film[3:] : 
                req = request.Request(url=comment_ref, headers=self.get_ua())
                response = request.urlopen(req)
                html = response.read().decode('utf-8')
                
                re_exp = '<div class="review-content.*?>(.*?)</div>'
                info_str_comment = self.parse_html(str=html, re_exp=re_exp)[0]
                
                info_str_comment = info_str_comment.replace(' ', '').replace('\n', '').replace('<p>', '').replace('</p>', '').replace('<br>', '').replace('&nbsp;', '')
                comments_list.append(info_str_comment)
            info_list_comments.append(tuple(comments_list))
            
        return [info_list_top, info_list_films, info_list_actors, info_list_comments]
    
    def parse_html(self, str, re_exp) :
        pattern = re.compile(re_exp, re.S)
        info_list = pattern.findall(str)
        return info_list
    
    # 用于本地分析html构成
    def save_html(self, filename, str, mod='w') :
        filename = filename + '.html'
        with open(filename, mod, encoding='utf-8') as f :
            f.write(str)
    
    def save_csv(self, filename, content, mod='w') :
        filename =  filename + '.csv'
        with open(filename, mod, newline='', encoding='utf-8') as f :
            writer = csv.writer(f)
            writer.writerows(content)
            
    def run(self, start, end) :
        start_time = time.time()
        for page in range(start, end+1) :
            start_time_epoch = time.time()
            # 查询参数编码
            index = (page - 1) * 25 
            params = {
                'start' : str(index)
            }
            params = parse.urlencode(params)
            url = self.baseurl.format(params)
            
            # 发起请求
            info = self.get_html(url=url)
            print('第%d页爬取成功'%page)
            try :
                # 保存电影top250
                if(len(info[0]) != 0) :
                    filename = 'data/top250'
                    self.save_csv(filename=filename, content=info[0], mod='a')
                
                # 保存电影简介及影评地址
                if(len(info[1]) != 0) :
                    filename = 'data/films'
                    self.save_csv(filename=filename, content=info[1], mod='a')       
                
                # 保存电影演员及相关信息
                if(len(info[2]) != 0) :
                    filename = 'data/actors'
                    self.save_csv(filename=filename, content=info[2], mod='a')
                    
                # 保存影评
                if(len(info[3]) != 0) :
                    filename= 'data/comments'
                    self.save_csv(filename=filename, content=info[3], mod='a')
                print('第%d页保存成功'%page)
            except :
                print('保存失败')
            time.sleep(random.randint(1, 2))
            end_time_epoch = time.time()
            print('Time used every epoch is %fs'%(end_time_epoch-start_time_epoch))
        end_time = time.time()
        print('All time used is %fs'%(end_time-start_time))                
    

if __name__ == '__main__' :
    baseurl = 'https://movie.douban.com/top250?{}'
    DouBanSpider = DouBanSpider(url=baseurl)
    start_index = 1
    end_index = 10
    DouBanSpider.run(start=start_index, end=end_index)




