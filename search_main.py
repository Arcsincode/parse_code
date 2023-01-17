from reFormat import remove_em,to_dataframe
from reFormat import myTime
import normRequests as requests
from asyncRequests import async_gets_jsons,async_downloads
from parsePdf import parse_pdf
from multi_process import multi_process
import time


def query_all_dicts(param_dict):
    """
    返回所有查询结果（字典列表）
    """

    def get_json_from_juchao(search_dict):

        for key,value in search_dict.items():
            if type(value) == list:
                multi_key = key
                values_list = value
                search_dict[multi_key] = f"""{{{multi_key}}}"""
                mode = "coroutine"
                break
        else:
            mode = "singal" 
        # 获取url
        url = 'http://www.cninfo.com.cn/new/fulltextSearch/full?searchkey={searchkey}'\
            '&sdate={sdate}'\
            '&edate={edate}'\
            '&isfulltext={isfulltext}'\
            '&sortName={sortName}'\
            '&sortType={sortType}'\
            '&pageNum={pageNum}&type={type}'.format(**search_dict)
        if mode == "singal":
            response = requests.get(url,)
            res = response.json()
        elif mode == "coroutine":
            urls = [url.format(**{multi_key:value}) for value in values_list]
            res = async_gets_jsons(urls)
        return res
        

    def get_num_pages_from_json(json_dict):
        import math
        return math.ceil(json_dict['totalAnnouncement']/10)


    json_res = get_json_from_juchao(search_dict=param_dict)
    num_pages = get_num_pages_from_json(json_res)

    num_pages = 1

    param_dict['pageNum'] = [i+1 for i in range(num_pages)]
    json_of_pages = get_json_from_juchao(search_dict=param_dict)
    
    dicts_list = []
    for json_of_page in json_of_pages:
        announcements_list = json_of_page['announcements']
        # res_dicts = [reformat_dict(announcement) for announcement in announcements_list]
        dicts_list += announcements_list
    return dicts_list
    

def reformat_dict(an_dict):
    # {'id': None, 'secCode': '000039', 'secName': '中集集团', 
    # 'orgId': 'gssz0000039', 'announcementId': '1204526484', 
    # 'announcementTitle': '中集集团：2017年<em>社会</em>责任暨环境、<em>社会</em><em>及</em><em>管治</em>报告', 
    # 'announcementTime': 1522166400000, 'adjunctUrl': 'finalpage/2018-03-28/1204526484.PDF', 
    # 'adjunctSize': 2190, 'adjunctType': 'PDF', 'storageTime': None, 
    # 'columnId': '09020202||250101||251302', 'pageColumn': 'SZZB', 
    # 'announcementType': '01010503||010112||01239999', 'associateAnnouncement': None, 
    # 'important': None, 'batchNum': None, 'announcementContent': None, 'orgName': None, 
    # 'announcementTypeName': None}
    res_dict = {
        'secCode':an_dict['secCode'],
        'secName':an_dict['secName'],
        'orgId':an_dict['orgId'],
        'announcementId':an_dict['announcementId'],
        'announcementTitle':an_dict['announcementTitle'],
        'announcement_title':remove_em(an_dict['announcementTitle']),
        'announcementTime':an_dict['announcementTime'],
        'announcement_year':myTime(an_dict['announcementTime']/1000).year, # 实际时间如'2018-03-28 00:00:10'
        'adjunctUrl':an_dict['adjunctUrl'],
        'record_time':myTime(time.time()).date, # 记录日期
    }
    print(remove_em(an_dict['announcementTitle']))
    return res_dict


if __name__=='__main__':
    param_dict = {
        # 搜索的关键词，如【'企业社会责任'】
        'searchkey':'社会及管治',
        # 发布起始时间，如【'2023-01-04'】【''表示不进行限制 】 
        'sdate':'', 
        # 发布截止时间，如【'2023-02-24'】【''表示不进行限制 】
        'edate':'', 
        # 是否进行全文搜索，【'false'为只搜索标题，'true'为搜索全文 】
        'isfulltext':'false', 
        # 按什么进行排序，【'pubdate'为按时间排序，'stockcode_cat'为按代码排序，'nothing'为按相关度排序 】
        'sortName':'stockcode_cat', 
        # 升序还是降序，【'asc'为升序，'desc'为降序 】
        'sortType':'asc', 
        # 页码，【如'1'】
        'pageNum':'1', 
        # 板块筛选，【''为全部板块，'shj'为深沪京，'s'为三板... 】
        'type':'shj', 
    }

    # 返回搜索结果（字典列表）
    dicts = query_all_dicts(param_dict=param_dict)
    # 格式化搜索结果——将存入csv的格式
    res_dicts = [reformat_dict(announcement) for announcement in dicts]
    
    # 将结果转化为csv
    df = to_dataframe(res_dicts)
    
    # 生成所有announcement的pdf文件的名称和下载列表，将用于协程下载
    pdf_urls = [(dict0['announcement_title']+'.pdf','http://static.cninfo.com.cn/'+dict0['adjunctUrl']) for dict0 in res_dicts]
    # 使用协程下载pdf文件，并返回所有文件下载到的路径（类型：tuple）
    dirs = async_downloads(pdf_urls,'./data/search_res')

    # 使用多进程分析pdf列表，返回结果字典列表（每个字典对应一个pdf的分析结果）
    parse_res = multi_process(parse_pdf,dirs)
    pages_nums = [res['pages_num'] for res in parse_res]
    words_nums = [res['words_num'] for res in parse_res]
    df['pages_num'] = pages_nums
    df['words_num'] = words_nums
    # 将csv存到本地（可选）
    df.to_csv('./res/announcements.csv',index=False,)

    # 统计并存到本地
    df2 = df.groupby(['secCode','announcement_year'])['announcementTitle'].count()
    df2.to_csv('./res/times_per_code_per_year.csv')


