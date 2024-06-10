
import time
import requests
from bs4 import BeautifulSoup
import feedparser
import os
from datetime import date
import pandas as pd
import hashlib
import concurrent
import concurrent.futures



# 定义不同分类的URL列表和分类名称
url_lists = [
    {
        'name': 'google_news_财经新闻',
        'urls': ['https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en&topic=b']
    },
    # {
    #     'name': 'google_news_技术新闻',
    #     'urls': ['https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en&topic=tc']
    # },
    # {
    #     'name':'开发者头条',
    #     'urls':['https://plink.anyfeeder.com/toutiao.io']
    # },
]

# 创建当天日期的文件夹
today = date.today()
folder_name = today.strftime('新闻数据\\' + "%Y-%m-%d")
os.makedirs(folder_name, exist_ok=True)

for category in url_lists:
    category_name = category['name']
    category_folder_path = os.path.join(folder_name, category_name)
    os.makedirs(category_folder_path, exist_ok=True)

    for url in category['urls']:
        feed = feedparser.parse(url)
        news = []
        print('初始化完成')
        print(news)

        for entry in feed.entries:
            response = requests.get(url, verify=True, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
                                    timeout=30,
                                    allow_redirects=True, stream=True, cert=False,
                                    )
            content = response.text

            # # 提取来源信息
            # pubDate = entry.pubDate.text if entry.pubDate else None

            news_data = {
                # 'title': entry.title,
                'link': entry.link,
                'title': entry.title,
                # 'time': pubDate,
                'description':entry.description
                # 添加其他字段，如发布时间、作者等

            }
            news.append(news_data)
            print(news)
        print('已完成对新闻的检索')

        df = pd.DataFrame(news)

        print('已完成新闻的写入列表操作')

        # 生成Excel文件的路径和名称
        url_folder_path = os.path.join(category_folder_path)
        os.makedirs(url_folder_path, exist_ok=True)

        print('已完成文件夹的创建')
        excel_filename = os.path.join(url_folder_path, category_name + '_' + f'{today.strftime("%d")}.xlsx')
        csv_filename = os.path.join(url_folder_path, category_name + '_' + f'{today.strftime("%d")}.csv')
        # 创建一个Excel写入器（writer）
        writer = pd.ExcelWriter(excel_filename, engine='xlsxwriter')

        # 将DataFrame写入Excel文件的Sheet1工作表中
        df.to_excel(writer, sheet_name='原始数据', index=False)
        print('已完成对工作表的写入')

        # 保存并关闭Excel写入器
        writer._save()

        # 把excel表格转化为csv格式
        df_1 = pd.read_excel(excel_filename)
        df_1.to_csv(csv_filename,index=False)
        print('已经保存csv文件')

#百度翻译

        def translate_title(title, APP_KEY, APP_SECRET):
            url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
            lang_from = 'auto'
            lang_to = 'zh'
            data = {'q': title, 'from': lang_from, 'to': lang_to}
            addAuthParams(APP_KEY, APP_SECRET, data)
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            res = perform_request(url, header, data, 'post')
            response_json = res.json()
            if 'error_code' in response_json:
                # If 'error_code' is present, there was an error in the API response.
                print(f"翻译失败，错误码：{response_json['error_code']}，错误信息：{response_json.get('error_msg', '')}")
                return None
            else:
                # The translation was successful.
                translated_title = response_json['trans_result'][0]['dst']
                print(translated_title)
                return translated_title


        def perform_request(url, header, params, method):
            if 'get' == method:
                return requests.get(url, params=params, headers=header)
            elif 'post' == method:
                return requests.post(url, data=params, headers=header)


        def addAuthParams(appKey, appSecret, params):
            salt = str(int(time.time() * 1000))
            sign_str = appKey + params['q'] + salt + appSecret
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            params['appid'] = appKey
            params['salt'] = salt
            params['sign'] = sign


        def translate_excel_titles(csv_filename,filename, sheet_name, title_column, APP_KEY, APP_SECRET):
            df = pd.read_excel(filename, sheet_name=sheet_name)
            titles = df[title_column].tolist()
            print(titles)

            translated_titles = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(translate_title, title, APP_KEY, APP_SECRET) for title in titles]
                for future, title in zip(concurrent.futures.as_completed(futures), titles):
                    translated_title = future.result()

                    if translated_title is not None:
                        translated_titles.append(translated_title)
                        translated_title_list = list(translated_title)
                        print(f"Original Title: {title}")
                        print(f"Translated Title: {translated_title_list}")
                    else:
                        translated_titles.append('')
                        print(f"Translation failed for Title: {title}")

            df['translate_title'] = translated_titles
            translated_filename = filename.split('.xlsx')[0] + '_中文版.xlsx'
            df.to_excel(translated_filename, index=False)
            print(f"翻译完成，已保存为'{translated_filename}'文件。")
            csv_tran_file = csv_filename.split('.csv')[0] + '_中文版.csv'
            df_2 = pd.read_excel(translated_filename)
            df_2.to_csv(csv_tran_file, index=False)
            print('已经保存csv文件')


        # 请将APP_KEY和APP_SECRET替换为实际的值
        APP_KEY =  ''
        APP_SECRET = ''
        filename = excel_filename
        translated_filename = filename.split('.xlsx')[0] + '_中文版.xlsx'
        sheet_name = '原始数据'
        title_column = 'title'
        csv_filename=csv_filename
        translate_excel_titles(csv_filename,filename, sheet_name, title_column, APP_KEY, APP_SECRET)

        # 读取 Excel 文件
        df = pd.read_excel(translated_filename, engine='openpyxl')

        # 创建一个空的列表，用于存储解析后的数据
        data = []

        # 遍历 "description" 列中的 HTML 内容
        for html_content in df["description"]:
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # 在链接为a中寻找所有相关链接
            links = soup.find_all('a')

            # 创建一个空的字符串，用于存储当前 HTML 内容中的链接信息
            combined_info = ""

            # 遍历所有链接
            for link in links:
                title = link.text  # 获取链接的文本
                url = link['href']  # 获取链接的URL
                font_tag = link.find('font')

                # 提取来源信息
                source = font_tag.text if font_tag else None

                # 将标题、链接和来源信息添加到 combined_info
                combined_info += f"标题: {title}\n链接: {url}\n来源: {source}\n\n"

            # 将当前 HTML 内容中的链接信息添加到 data 列表中
            data.append(combined_info)

        # 创建一个新的 DataFrame
        new_df = pd.DataFrame({'相关链接': data})

        # 将新的数据追加到原始 Excel 文件中，包括列名
        excel_filename1 = filename.split('.xlsx')[0] + '_追加_中文版.xlsx'
        df['相关链接（来源于description）'] = data
        df.to_excel(excel_filename1, index=False)

        print("信息已成功提取并追加到 Excel 文件")


print('全部程序已完成')
