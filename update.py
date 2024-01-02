import NotionAPI
import requests
from bs4 import BeautifulSoup
import time
import re
from config import *


def DataBase_additem(database_id, body_properties, station):
    body = {
        'parent': {'type': 'database_id', 'database_id': database_id},
    }
    body.update(body_properties)

    url_notion_additem = 'https://api.notion.com/v1/pages'
    notion_additem = requests.post(url_notion_additem, headers=headers, json=body)

    if notion_additem.status_code == 200:
        print(station + '·更新成功')
    else:
        print(station + '·更新失败')


def film_info2(movie_url):
    # 目前想改进的有title，类型，导演

    url = movie_url
    res = requests.get(url, headers=headers, allow_redirects=False)
    url = res.headers['Location'] if res.status_code == 302 else url
    print(url)
    res = requests.get(url, headers=headers, allow_redirects=False)
    bstitle = BeautifulSoup(res.text, 'html.parser')

    moive_content = bstitle.find_all('div', id='content')
    moive_content = moive_content[0]
    # 电影名称与年份
    title = moive_content.find('h1')
    title = title.find_all('span')
    title = title[0].text + title[1].text

    # 电影名称与年份
    title = moive_content.find('h1')
    title = title.find_all('span')
    title = title[0].text + title[1].text

    # 基本信息
    base_information = moive_content.find('div', class_='subject clearfix')
    info = base_information.find('div', id='info').text.split('\n')
    info = ','.join(info)
    # print(info)
    pattern_type = re.compile(r'(?<=类型: )[\u4e00-\u9fa5 /]+', re.S)
    movie_type = re.findall(pattern_type, info)[0].replace(" ", "").split("/")
    # print(movie_type)
    pattern_director = re.compile(r'(?<=导演: )[\u4e00-\u9fa5 /]+', re.I)
    director = re.findall(pattern_director, info)[0].replace(" ", "").split("/")
    # print(director)

    return title, movie_type, director


def download_picture(url):
    headers = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
           'Cookie': 'talionnav_show_app="0"; bid=Cf71zChb_RQ; douban-fav-remind=1; ll="108242"; __gads=ID=0bafb4aeb143fe67-22ec8fe4afdd00e7:T=1682543567:RT=1682543567:S=ALNI_MbYOc1Iz2XRtqDuvMRIvG0ivsYWsQ; __gpi=UID=00000bf1637416d5:T=1682543567:RT=1682543567:S=ALNI_MaOhiuhuE9t248mVM_BfajI0RvLAw; viewed="26848581_36096690_35059158"; push_doumail_num=0; push_noty_num=0; __utmv=30149280.5994; _ga_RXNMP372GL=GS1.1.1701095081.2.1.1701095098.43.0.0; __utmc=30149280; dbcl2="59941972:/x0Ua+y4wtQ"; ck=Dqhb; ap_v=0,6.0; __utma=30149280.406879458.1699907638.1704150147.1704184051.14; __utmz=30149280.1704184051.14.11.utmcsr=movie.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/59941972/wish; __utmb=30149280.2.10.1704184051; frodotk="1d5b0e530a4af33358112af91ee0d999"; talionusr="eyJpZCI6ICI1OTk0MTk3MiIsICJuYW1lIjogIlx1OTRjM1x1OTRkYlx1ODJiMVx1NWYwMFx1NGU4NiJ9"; _ga_Y4GN1R87RG=GS1.1.1704185247.1.0.1704185247.0.0.0; _ga=GA1.2.406879458.1699907638; _gid=GA1.2.764250390.1704185248; Hm_lvt_6d4a8cfea88fa457c3127e14fb5fabc2=1704185248; Hm_lpvt_6d4a8cfea88fa457c3127e14fb5fabc2=1704185248',
           'Host': 'www.douban.com',
           'Referer': 'https://accounts.douban.com/'}
    # 获取网页的源代码
    r = requests.get(url, headers=headers)
    # 利用BeautifulSoup将获取到的文本解析成HTML
    soup = BeautifulSoup(r.text, "lxml")
    # 获取网页中的电影图片
    content = soup.find('div', class_='article')
    images = content.find_all('img')
    # 获取电影图片的名称和下载地址
    # picture_name_list = [image['alt'] for image in images]
    picture_link_list = images[0]['src']

    # 利用urllib.request..urlretrieve正式下载图片
    # for picture_name, picture_link in zip(picture_name_list, picture_link_list):
    #     urllib.request.urlretrieve(picture_link, 'E://douban/%s.jpg' % picture_name)
    return picture_link_list


notion_moives = NotionAPI.DataBase_item_query(databaseid)
for item in notion_moives:
    print(item)
    # title = item['properties']['名称']['title'][0]['plain_text']
    watch_time = item['properties']['观看时间']['date']['start']
    movie_url = item['properties']['影片链接']['url']
    movie_url = movie_url.replace('http://movie.douban.com/subject/', 'https://movie.douban.com/subject/')
    comment = ''
    title, movie_type, director = film_info2(movie_url)
    cover_url = download_picture(movie_url)
    score = "⭐⭐"
    body = {
        'properties': {
            '名称': {
                'title': [{'type': 'text', 'text': {'content': str(title)}}]
            },
            '观看时间': {'date': {'start': str(watch_time)}},
            '评分': {'type': 'select', 'select': {'name': str(score)}},
            '封面': {
                'files': [{'type': 'external', 'name': '封面', 'external': {'url': str(cover_url)}}]
            },
            '有啥想说的不': {'type': 'rich_text',
                             'rich_text': [
                                 {'type': 'text', 'text': {'content': str(comment)}, 'plain_text': str(comment)}]},
            '影片链接': {'type': 'url', 'url': str(movie_url)},
            '类型': {'type': 'multi_select', 'multi_select': [{'name': str(itemm)} for itemm in movie_type]},
            '导演': {'type': 'multi_select', 'multi_select': [{'name': str(itemm)} for itemm in director]},

        }
    }
    print(body)
    NotionAPI.DataBase_additem(databaseid, body, title)
    time.sleep(3)
