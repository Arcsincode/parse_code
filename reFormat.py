import time
import re
import pandas as pd


def remove_em(string):
    """
    去除搜索结果中的标记
    如将
    '香港中华煤气：环境、<em>社会</em><em>及</em><em>管治</em>报告2019'
    变为
    '香港中华煤气：环境、社会及管治报告2019'
    """
    string = string.replace('<em>','').replace('</em>','')
    return string


def to_realtime(timestamp):
    """return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))"""
    import time
    time_local = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S",time_local)

class myTime:
    def __init__(self,timestamp) -> None:
        time_local = time.localtime(timestamp)
        self.date_time = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        self.date = time.strftime("%Y-%m-%d",time_local)
        self.year = time.strftime("%Y",time_local)
        self.month = time.strftime("%m",time_local)
        self.day = time.strftime("%d",time_local)



def to_dataframe(res_dicts):
    """传入值为字典的列表"""
    # res_dicts = [reformat_dict(announcement) for announcement in dicts]
    ress_dicts = [list(res_dict.values()) for res_dict in res_dicts]    
    return pd.DataFrame(ress_dicts,columns=list(res_dicts[0].keys()))