# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 01:42:51 2019
通过网页的爬取获得最终的pdf地址，并且写入到最后的csv文件
@author: herr_kun
"""

# coding = utf-8

import csv
import math
import os
import time
import kits.normRequests as requests
import pandas as pd

OUTPUT_FILENAME = 'report'
# 板块类型：沪市：shmb；深市：szse；深主板：szmb；中小板：szzx；创业板：szcy；
PLATE = 'szzx;'
# 公告类型：category_scgkfx_szsh（首次公开发行及上市）、category_ndbg_szsh（年度报告）、category_bndbg_szsh（半年度报告）
CATEGORY = 'category_ndbg_szsh;'

URL = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'


MAX_PAGESIZE = 50
MAX_RELOAD_TIMES = 5
RESPONSE_TIMEOUT = 10


def standardize_dir(dir_str):
    assert (os.path.exists(dir_str)), 'Such directory \"' + str(dir_str) + '\" does not exists!'
    if dir_str[len(dir_str) - 1] != '/':
        return dir_str + '/'
    else:
        return dir_str



### 获取定制query部分

SZ_LIST = ['300','301','000','001','002','003']
SH_LIST = ['601','603','605','688','689','600']

code_df = pd.read_csv('./code_orgId.csv',dtype=str,)
code = code_df.set_index('code')

def get_s_query_dict(stock_code):
    stock_code = str(stock_code)
    orgId = code.loc[stock_code]['orgId']
    if stock_code[:3] in SZ_LIST:
        # sz创业
            res = {
                "stock":str(stock_code)+","+orgId,
                "column":"szse",
                'plate': 'sz',

            }
    elif stock_code[:3] in SH_LIST:
        # sh创业
            res = {
                "stock":str(stock_code)+","+orgId,
                "column":"sse",
                'plate': 'sh',

            }
    return res





# 参数：页面id(每页条目个数由MAX_PAGESIZE控制)，是否返回总条目数(bool)
def get_response(page_num,stock_code,return_total_count=False,START_DATE = '2013-01-01',END_DATE = '2018-01-01'):

    def get_query_from_code(stock_code,):
        q_dict = get_s_query_dict(stock_code,)
        # print(q_dict)
        query_new = {
                'tabName': 'fulltext', 
                'pageSize': MAX_PAGESIZE,
                'pageNum': page_num,
                'category': CATEGORY,
                'seDate': START_DATE + '~' + END_DATE,
                'searchkey': '',
                'secid':'',
                'trade': '',
                'sortName': '',
                'sortType': '',
                'isHLtitle':'true'
                }
        q_dict.update(query_new)
        return q_dict

        
    query = get_query_from_code(stock_code,)

    result_list = []
    reloading = 0
    while True:
        try:
            r = requests.post(URL, query,timeout=RESPONSE_TIMEOUT)
            # print(r)
        except Exception as e:
            print(e)
            continue
        if r.status_code == requests.codes.ok and r.text != '':
            break
    my_query = r.json()
    try:
        r.close()
    except Exception as e:
        print(e)
    if return_total_count:
        return my_query['totalRecordNum']
    else:
        for each in my_query['announcements']:
            file_link = 'http://static.cninfo.com.cn/' + str(each['adjunctUrl'])
            file_name = __filter_illegal_filename(
                str(each['secCode']) + str(each['secName']) + str(each['announcementTitle']) + '.'  + '(' + str(each['adjunctSize'])  + 'k)' +
                file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
            )
            if file_name.endswith('.PDF') or file_name.endswith('.pdf'):
                if '取消' not in file_name and '摘要' not in file_name and '年度' in file_name and\
                '更正' not in file_name and '英文' not in file_name and '补充' not in file_name:
                    result_list.append([file_name, file_link])
        return result_list


# def __log_error(err_msg):
#     err_msg = str(err_msg)
#     print(err_msg)
#     # with open(error_log, 'a', encoding='gb18030') as err_writer:
#     with open(error_log, 'a', encoding='utf-8') as err_writer:
#         err_writer.write(err_msg + '\n')


def __filter_illegal_filename(filename):
    illegal_char = {
        ' ': '',
        '*': '',
        '/': '-',
        '\\': '-',
        ':': '-',
        '?': '-',
        '"': '',
        '<': '',
        '>': '',
        '|': '',
        '－': '-',
        '—': '-',
        '（': '(',
        '）': ')',
        'Ａ': 'A',
        'Ｂ': 'B',
        'Ｈ': 'H',
        '，': ',',
        '。': '.',
        '：': '-',
        '！': '_',
        '？': '-',
        '“': '"',
        '”': '"',
        '‘': '',
        '’': ''
    }
    for item in illegal_char.items():
        filename = filename.replace(item[0], item[1])
    return filename



def get_name_url(stock_code,START_DATE,END_DATE):
    START_DATE=START_DATE+'-01-01'
    END_DATE=END_DATE+'-01-01'
    urls = []
    
    start=time.time()
    
    # 获取记录数、页数
    item_count = get_response(1,stock_code,True,START_DATE = START_DATE,END_DATE = END_DATE)
    assert (item_count != []), 'Please restart this script!'
    begin_pg = 1
    end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
    print('Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
    time.sleep(2)

    # 逐页抓取
    #with open(output_csv_file, 'w', newline='', encoding='gb18030') as csv_out:
        #writer = csv.writer(csv_out)
    for i in range(begin_pg, end_pg + 1):
        row = get_response(i,stock_code,START_DATE = START_DATE,END_DATE = END_DATE)
        urls += (row)
        last_item = i * MAX_PAGESIZE if i < end_pg else item_count
        print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(last_item) + ')/' + str(item_count) + '.')
    # csv_out.close()
    
    end=time.time()
    
    print('========== time to open processing all files are {} =========='.format((end-start)))
    
    return urls


def async_get_names_urls(stock_code_set,START_DATE,END_DATE):
    from kits.asyncRequests import async_posts_jsons

    def get_query_from_code(stock_code,page_num):
        q_dict = get_s_query_dict(stock_code,)
        query_new = {
                'tabName': 'fulltext', 
                'pageSize': MAX_PAGESIZE,
                'pageNum': page_num,
                'category': CATEGORY,
                'seDate': START_DATE + '~' + END_DATE,
                'searchkey': '',
                'secid':'',
                'trade': '',
                'sortName': '',
                'sortType': '',
                'isHLtitle':'true'
                }
        q_dict.update(query_new)
        return q_dict
    
    def get_records_list():
        urls = [URL] * len(stock_code_set)
        datas = [get_query_from_code(stock_code,1) for stock_code in stock_code_set]
        print("正在获取全部记录数和页数...")
        res_get_page = async_posts_jsons(urls=urls,datas=datas)
        records_list = [res['totalRecordNum'] for res in res_get_page]
        return records_list

    def get_urls_from_json(my_query):
        # 从某一页的返回json中获取所有符合条件的链接list
        result_list = []
        for each in my_query['announcements']:
            file_link = 'http://static.cninfo.com.cn/' + str(each['adjunctUrl'])
            file_name = __filter_illegal_filename(
                str(each['secCode']) + str(each['secName']) + str(each['announcementTitle']) + '.'  + '(' + str(each['adjunctSize'])  + 'k)' +
                file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
            )
            if file_name.endswith('.PDF') or file_name.endswith('.pdf'):
                if '取消' not in file_name and '摘要' not in file_name and '年度' in file_name and\
                '更正' not in file_name and '英文' not in file_name and '补充' not in file_name:
                    result_list.append([file_name, file_link])
        return result_list

    START_DATE=START_DATE+'-01-01'
    END_DATE=END_DATE+'-12-31'

    # 获取记录数→页数，存于列表
    records_list = get_records_list()
    pages_num_list = [int(math.ceil(item_count / MAX_PAGESIZE)) for item_count in records_list]
    
    # 生成所有请求url
    urls = []
    datas = []
    all_res = []
    # urls_num = []
    for i in range(len(stock_code_set)):
        stock_code = stock_code_set[i]
        data = [get_query_from_code(stock_code,page) for page in range(1,pages_num_list[i]+1)]
        datas += data
        # urls_num.append(len())
    urls = [URL] * len(datas)    

    print("正在获取全部链接...")
    jsons = async_posts_jsons(urls=urls,datas=datas)
    for json in jsons:
        all_res += get_urls_from_json(json)
    return all_res

def get_names_urls(stock_code_set,START_DATE,END_DATE):
    START_DATE=START_DATE+'-01-01'
    END_DATE=END_DATE+'-01-01'
    urls = []
    
    start=time.time()
    
    for stock_code in stock_code_set:
        # 获取记录数、页数
        item_count = get_response(1,stock_code,True,START_DATE = START_DATE,END_DATE = END_DATE)
        assert (item_count != []), 'Please restart this script!'
        begin_pg = 1
        end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
        print('Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
        time.sleep(2)

        for i in range(begin_pg, end_pg + 1):
            row = get_response(i,stock_code,START_DATE = START_DATE,END_DATE = END_DATE)
            # urls.append(row)
            urls += row
            last_item = i * MAX_PAGESIZE if i < end_pg else item_count
            print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                    str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(last_item) + ')/' + str(item_count) + '.')
    # csv_out.close()
    
    end=time.time()
    
    # print('********time to open processing all files are {}*********'.format((end-start)))
    print('========== time to open processing all files are {} =========='.format((end-start)))
    
    return urls


if __name__=='__main__':
    START_DATE,END_DATE = ['2011','2023']
    stock_code_set = ['000006','000007','000008']
    current_names_urls = async_get_names_urls(stock_code_set,START_DATE,END_DATE)
    print(current_names_urls)