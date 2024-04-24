from DrissionPage import WebPage, ChromiumOptions
import re
import os
import json
import shutil
from redis import StrictRedis
from dotenv import load_dotenv


def find_dotenv():
    # 当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.sep)
    # print(root_dir, current_dir)
    dotenv_file_name = '.env'

    # 开始向上搜索.env文件
    while current_dir != root_dir:
        dotenv_path = os.path.join(current_dir, dotenv_file_name)
        if os.path.isfile(dotenv_path):
            return dotenv_path
        # 向上移动到父目录
        current_dir = os.path.dirname(current_dir)
    return None


dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    print("未找到.env文件")
    exit()
username = os.getenv("GIF2024_USERNAME")
password = os.getenv("GIF2024_PASSWORD")
# print(username, password)

isLoggined = False
baseUrl = "https://gif2024.cc"
rds = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
redisPrefix = 'gif2024_'
failedUrlsKey = redisPrefix + 'failedUrls'
successItemsKey = redisPrefix + 'successItems'
newestIdKey = redisPrefix + 'newestID'

# 将抓取的第一个的id 记录下来 也就是最新的记录
isFirst = True
# stopCraw = False
prevLatestID = rds.get(newestIdKey)


def saveGif(gifUrl, gifSavePath):
    page.get(gifUrl, allow_redirects=False)
    res = page.response
    if res is None:
        print(gifUrl+"跳过了")
        return False
    if res.status_code == 302:
        page.download.add(
            res.headers['location'], gifSavePath)


def getPage(pageUrl):
    # global stopCraw
    global isFirst
    # if stopCraw:
    #     print(f"最新 id 为 {prevLatestID} 全部都抓取完了")
    #     return
    page.get(pageUrl)
    nextPage = page.s_ele('.next-page')
    # class 内容中以 excerpt 打头的项 page.eles('.^excerpt')
    for article in page.s_eles('t:article'):
        focus = article.s_ele('.focus')
        detailUrl = focus.attr('href')
        title = focus.s_ele('t:img').attr('alt')
        if not title:
            print("无 title 跳过")
            continue
        if '开通vip' in title or 'APP客户端' in title or '搜番号必备' in title or '福利汇总' in title:
            print('包含违禁词，跳过')
            continue
        id = detailUrl.split('/')[-1].split('.')[0]

        # 如果存在上次抓取的最新 id 且跟当前这个一样 那就直接 return
        if prevLatestID and id == prevLatestID:
            print(f"最新 id 为 {prevLatestID} 全部都抓取完了")
            stopCraw = True
            return

        gifSavePath = id

        if isFirst:
            rds.set(newestIdKey, id)
            isFirst = False

        if rds.getbit(successItemsKey, id):
            print(id + '已经抓成功了')
            continue
        if not os.path.exists(id):
            os.makedirs(id, exist_ok=True)
        else:
            shutil.rmtree(id)
            os.makedirs(id, exist_ok=True)

        # thumb 下载
        thumbUrl = focus.s_ele('t:img').attr('src')
        page.download.add(thumbUrl, gifSavePath)

        page.get(detailUrl)
        desc = page.s_ele('tag:meta@name=description').attr('content')

        metaData = {"title": title, "description": desc,
                    "id": id, "url": detailUrl}
        match = re.search(r'\[erphpdown\] (.*?) \[/erphpdown\]', desc)
        if match:
            metaData['avNum'] = match.group(1)

        metaPath = os.path.join(id, "meta.json")
        with open(metaPath, 'w') as mf:
            mf.write(json.dumps(metaData))
        gifs = page.ele('.article-content').s_eles("t:img")
        if gifs:
            for gif in gifs:
                gifUrl = gif.attr('src')
                # 处理 302
                res = saveGif(gifUrl, gifSavePath)
                if not res:
                    continue
        rds.setbit(successItemsKey, id, 1)
        print(detailUrl, title)
    print(pageUrl + '完成')
    if nextPage and nextPage.text:
        nextPageUrl = nextPage.child('t:a').attr('href')
        print(nextPageUrl + '开始了')
        getPage(nextPageUrl)


page = WebPage()
print(page.mode)
page.get(baseUrl)
for item in page.cookies(as_dict=False):
    ckName = item.get('name')
    if ckName and ckName.startswith("wordpress_logged_in_"):
        isLoggined = True

if not isLoggined:
    print("未登录")
    page.get(baseUrl + "/usercenter")
    page.wait.ele_displayed('.signin-loader')
    page.actions.move_to('.signin-loader').click().move_to('#inputEmail').type(
        username).move_to("#inputPassword").click().type(password).move_to("#site_login").click()

print("已登录")
page.get(baseUrl)
page.change_mode('s')
print(page.mode)

getPage(baseUrl)

page.quit()
