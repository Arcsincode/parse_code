import time
import pandas
from kits import reFormat  
from kits.reFormat import myTime
import kits.normRequests as requests
from kits.asyncRequests import async_gets_jsons,async_downloads
from kits.parsePdf import parse_pdf_mp
from kits.multi_process import multi_process_star
from kits import quickDb
import config
from config import query_config
QUERY_DICT = query_config.query_dict

TABLE_INFO = {
    'secCode':'VARCHAR(20) NOT NULL',
    'secName':'VARCHAR(30) NOT NULL',
    'orgId':'VARCHAR(50)',
    'type':'VARCHAR(20)',
    'announcementId':'VARCHAR(30) NOT NULL',
    'announcementTitle':'VARCHAR(100) NOT NULL',
    'announcement_title':'VARCHAR(100) NOT NULL',
    'announcementTime':'BIGINT UNSIGNED',
    'announcement_year':'YEAR', # 实际时间如'2018'
    'adjunctUrl':'VARCHAR(100) NOT NULL',
    'record_time':'DATE', # 记录日期
    'pages_num':'INT UNSIGNED',
    'words_num':'BIGINT UNSIGNED'
}
TABLE_PRIMARY = 'announcementId'



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


def query_all_dicts(param_dict):
    """
    返回所有查询结果（字典列表）
    """
    # 该字典为查询条件，值为None的表明可被param_dict更新，但请勿更改关键字key
    Fix_query_dict = {
        # 搜索的关键词，如【'企业社会责任'】
        'searchkey':None,
        # 发布起始时间，如【'2023-01-04'】【''表示不进行限制 】 
        'sdate':None, 
        # 发布截止时间，如【'2023-02-24'】【''表示不进行限制 】
        'edate':None, 
        # 是否进行全文搜索，【'false'为只搜索标题，'true'为搜索全文 】
        'isfulltext':None, 
        # 按什么进行排序，【'pubdate'为按时间排序，'stockcode_cat'为按代码排序，'nothing'为按相关度排序 】
        'sortName':'stockcode_cat', 
        # 升序还是降序，【'asc'为升序，'desc'为降序 】
        'sortType':'asc', 
        # 页码，【如'1'】
        'pageNum':'1', 
        # 板块筛选，【''为全部板块，'shj'为深沪京，'s'为三板... 】
        'type':None, 
    }
    Fix_query_dict.update(param_dict)
    json_res = get_json_from_juchao(search_dict=Fix_query_dict)
    num_pages = get_num_pages_from_json(json_res)
    Fix_query_dict['pageNum'] = [i+1 for i in range(num_pages)]
    json_of_pages = get_json_from_juchao(search_dict=Fix_query_dict)
    
    dicts_list = []
    for json_of_page in json_of_pages:
        announcements_list = json_of_page['announcements']
        dicts_list += announcements_list
    
    [dict_.update({'type':Fix_query_dict['type']}) for dict_ in dicts_list]
    return dicts_list
    

def reformat_dict(an_dict):
    """用于格式化字典:会将格式化后的关键字作为dataframe的columns
    """
    # {'id': None, 'secCode': '000039', 'secName': '中集集团', 
    # 'orgId': 'gssz0000039', 'announcementId': '1204526484', 
    # 'announcementTitle': '中集集团：2017年<em>社会</em>责任暨环境、<em>社会</em><em>及</em><em>管治</em>报告', 
    # 'announcementTime': 1522166400000, 'adjunctUrl': 'finalpage/2018-03-28/1204526484.PDF', 
    # 'adjunctSize': 2190, 'adjunctType': 'PDF', 'storageTime': None, 
    # 'columnId': '09020202||250101||251302', 'pageColumn': 'SZZB', 
    # 'announcementType': '01010503||010112||01239999', 'associateAnnouncement': None, 
    # 'important': None, 'batchNum': None, 'announcementContent': None, 'orgName': None, 
    # 'announcementTypeName': None}

    # 关系到columns的一致性，请谨慎更改该字典
    res_dict = {
        'secCode':an_dict['secCode'],
        'secName':an_dict['secName'],
        'orgId':an_dict['orgId'],
        'type':an_dict['type'],
        'announcementId':an_dict['announcementId'],
        'announcementTitle':an_dict['announcementTitle'],
        'announcement_title':reFormat.remove_em(an_dict['announcementTitle']),
        'announcementTime':an_dict['announcementTime'],
        'announcement_year':myTime(an_dict['announcementTime']/1000).year, # 实际时间如'2018'
        'adjunctUrl':an_dict['adjunctUrl'],
        'record_time':myTime(time.time()).date, # 记录日期
    }
    l = len(res_dict.keys())
    # 确保写入的一致性
    assert list(res_dict.keys()) == list(TABLE_INFO.keys())[:l]
    # print(remove_em(an_dict['announcementTitle']))
    return res_dict


def filter_dicts(res_dicts,reject_list):
    res_dicts = [res_dict for res_dict in res_dicts 
                    if reFormat.maintain_or_not(res_dict['announcement_title'],reject_list=reject_list)]
    return res_dicts


def download_from_dicts(res_dicts,to_dir):
    """将传入的res_dicts中的每一项提取其中的pdf链接进行下载,返回下载完成后对应的文件路径(列表)"""
    pdf_urls = [(dict0['announcement_title']+'.pdf','http://static.cninfo.com.cn/'+dict0['adjunctUrl']) for dict0 in res_dicts]
    # 使用协程下载pdf文件，并返回所有文件下载到的路径（类型：tuple）
    dirs = async_downloads(pdf_urls,to_dir)
    return dirs


if __name__=='__main__':

    db = quickDb.MyDb()
    db.close()

    TABLE_NAME_search = QUERY_DICT['searchkey']
    # 返回搜索结果（字典列表）
    dicts = query_all_dicts(param_dict=QUERY_DICT)
    # 格式化搜索结果→将存入csv/数据库的格式
    res_dicts = [reformat_dict(announcement) for announcement in dicts]
    # 筛掉一部分含某些关键词的，如"英文版"
    res_dicts = filter_dicts(res_dicts,reject_list=['英文版',])
    # 对传入的res_dicts进行裁剪（可用于分布式）
    print(f"满足条件的共有：【 {len(res_dicts)}条 】")
    l,r = reFormat.extra_range(input("""请选择处理的范围,如：
    【 0,3 】表示从第0条开始到第2条(左闭右开),
    【 3, 】表示从3开始到最后一个,
    【 ,-1 】表示从第0个到倒数第2个
    """))
    res_dicts = res_dicts[l:r]
    # 赋值SEARCH_RES_NAME作为保存此次分析结果的id，形如"社会及管治___false_shj_0_10"

    # 生成所有announcement的pdf文件的名称和下载列表，将用协程下载
    #SEARCH_RES_NAME = f"{'_'.join(QUERY_DICT.values())}_{l}_{r}"
    SEARCH_RES_NAME = f"{'_'.join(QUERY_DICT.values())}"
    dirs = download_from_dicts(res_dicts,f'./data/search_res/{SEARCH_RES_NAME}')

    # multiprocess
    import multiprocessing

    # 使用多进程分析pdf列表，返回结果字典列表（每个字典对应一个pdf的分析结果）
    value = multiprocessing.Manager().Value('i',0)
    lock = multiprocessing.Manager().Lock()
    total_num = len(dirs)
    args_list = list(zip(dirs,[value]*total_num,[total_num]*total_num,[lock]*total_num))
    parse_res = multi_process_star(parse_pdf_mp,args_list)
    # 用pdf列表的分析结果更新res_dicts
    [res_dict.update(pdf_res_dict) for pdf_res_dict,res_dict in zip(parse_res,res_dicts)]

    # 确保写入的一致性
    assert list(res_dicts[0].keys()) == list(TABLE_INFO.keys())


    db = quickDb.MyDb('Juchao')
    db.execute(quickDb.generate_create_sql(table_name=TABLE_NAME_search,columns_infos_dict=TABLE_INFO,primary_key=TABLE_PRIMARY))
    # 写入announcements结果
    db.execute(quickDb.generate_insert_sql(table_name=TABLE_NAME_search,input_args=res_dicts))
    db.commit()
    db.close()

