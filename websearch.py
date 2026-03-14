# Created by Charles on 2018/10/10, Modified by MewCo-AI on 2026/03/14
import requests as rq
from bs4 import BeautifulSoup

ABSTRACT_MAX_LENGTH = 300
HEADERS = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
           "Content-Type": "application/x-www-form-urlencoded",
           "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
           "Referer": "https://www.baidu.com/",
           "Accept-Encoding": "gzip, deflate",
           "Accept-Language": "zh-CN,zh;q=0.9"}
baidu_host_url = "https://www.baidu.com"
baidu_search_url = "https://www.baidu.com/s?ie=utf-8&tn=baidu&wd="
session = rq.Session()
session.headers = HEADERS


def search(keyword, num_results=10):  # 搜索
    if not keyword:
        return None
    list_result = []
    page = 1
    next_url = baidu_search_url + keyword
    while len(list_result) < num_results:
        data, next_url = parse_html(next_url, rank_start=len(list_result))
        if data:
            list_result += data
        if not next_url:
            break
        page += 1
    return list_result[: num_results] if len(list_result) > num_results else list_result


def parse_html(url, rank_start=0):  # 解析html
    try:
        res = session.get(url=url)
        res.encoding = "utf-8"
        root = BeautifulSoup(res.text, "lxml")
        list_data = []
        div_contents = root.find("div", id="content_left")
        for div in div_contents.contents:
            if type(div) != type(div_contents):
                continue
            class_list = div.get("class", [])
            if not class_list:
                continue
            if "c-container" not in class_list:
                continue
            title, url, abstract = '', '', ''
            try:
                if "xpath-log" in class_list:
                    if div.h3:
                        title = div.h3.text.strip()
                        url = div.h3.a['href'].strip()
                    else:
                        title = div.text.strip().split("\n", 1)[0]
                        if div.a:
                            url = div.a['href'].strip()
                    if div.find("div", class_="c-abstract"):
                        abstract = div.find("div", class_="c-abstract").text.strip()
                    elif div.div:
                        abstract = div.div.text.strip()
                    else:
                        abstract = div.text.strip().split("\n", 1)[1].strip()
                elif "result-op" in class_list:
                    if div.h3:
                        title = div.h3.text.strip()
                        url = div.h3.a['href'].strip()
                    else:
                        title = div.text.strip().split("\n", 1)[0]
                        url = div.a['href'].strip()
                    if div.find("div", class_="c-abstract"):
                        abstract = div.find("div", class_="c-abstract").text.strip()
                    elif div.div:
                        abstract = div.div.text.strip()
                    else:
                        abstract = div.text.strip().split("\n", 1)[1].strip()
                else:
                    if div.get("tpl", "") != "se_com_default":
                        if div.get("tpl", "") == "se_st_com_abstract":
                            if len(div.contents) >= 1:
                                title = div.h3.text.strip()
                                if div.find("div", class_="c-abstract"):
                                    abstract = div.find("div", class_="c-abstract").text.strip()
                                elif div.div:
                                    abstract = div.div.text.strip()
                                else:
                                    abstract = div.text.strip()
                        else:
                            if len(div.contents) >= 2:
                                if div.h3:
                                    title = div.h3.text.strip()
                                    url = div.h3.a['href'].strip()
                                else:
                                    title = div.contents[0].text.strip()
                                    url = div.h3.a['href'].strip()
                                if div.find("div", class_="c-abstract"):
                                    abstract = div.find("div", class_="c-abstract").text.strip()
                                elif div.div:
                                    abstract = div.div.text.strip()
                                else:
                                    abstract = div.text.strip()
                    else:
                        if div.h3:
                            title = div.h3.text.strip()
                            url = div.h3.a['href'].strip()
                        else:
                            title = div.contents[0].text.strip()
                            url = div.h3.a['href'].strip()
                        if div.find("div", class_="c-abstract"):
                            abstract = div.find("div", class_="c-abstract").text.strip()
                        elif div.div:
                            abstract = div.div.text.strip()
                        else:
                            abstract = div.text.strip()
            except:
                continue
            if ABSTRACT_MAX_LENGTH and len(abstract) > ABSTRACT_MAX_LENGTH:
                abstract = abstract[:ABSTRACT_MAX_LENGTH]
            rank_start += 1
            list_data.append({"title": title, "abstract": abstract, "url": url, "rank": rank_start})
        next_btn = root.find_all("a", class_="n")
        if len(next_btn) <= 0 or u"上一页" in next_btn[-1].text:
            return list_data, None
        next_url = baidu_host_url + next_btn[-1]["href"]
        return list_data, next_url
    except:
        return None, None
