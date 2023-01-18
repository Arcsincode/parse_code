import time
import re
import pandas as pd


def extra_range(string):
    """
4,5 → [4, 5]

-2,5 → [-2, 5]

3, → [3, None]

,7 → [None, 7]
    """
    res = list(re.findall("(-?\d*)\W+(-?\d*)",string)[0])
    for i in range(len(res)):
        if res[i]:
            res[i] = int(res[i])
        else:
            res[i] = None
    return res


# def select_range(res_dicts):
#     """对传入列表进行裁剪"""
#     print(f"满足条件的共有：【 {len(res_dicts)}条 】")
#     range_input = input("""请选择处理的范围,如：
# 【 0,3 】表示从第0条开始到第2条(左闭右开),
# 【 3, 】表示从3开始到最后一个,
# 【 ,-1 】表示从第0个到倒数第2个
# """)
#     l,r = extra_range(range_input)
#     res_dicts = res_dicts[l:r]
#     return res_dicts


def maintain_or_not(string,reject_list):
    """若string中存在任意reject_list中的值,则返回false"""
    for reject in reject_list:
        if reject in string:
            return False
    return True


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


if __name__ == "__main__":
    while True:
        print(extra_range(input()))