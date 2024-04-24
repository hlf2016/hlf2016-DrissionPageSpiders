import os
from DownloadKit import DownloadKit
from DrissionPage import WebPage

page = WebPage('s')

page.get(
    'https://list.wulishe.cc/d/1899/giftujie/2024/202403/20230513165817.gif', allow_redirects=False)
print(page.response.headers['location'])

page.get("https://gif2024.cc/wp-content/uploads/2023/03/20221103-2148-3607-220x150.gif")
print(page.response.raw)

page.download.add(
    'https://gif2024.cc/wp-content/uploads/2023/03/20221103-2148-3607-220x150.gif', './')

print(os.path.join("a", "b.jpg", "c"))

# d = DownloadKit()
# res = d.add(
#     "https://list.wulishe.cc/d/1899/giftujie/2024/202403/20230513165817.gif", "./", headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}).wait()
# print(res)
