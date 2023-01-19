import os
_config_text = {
# 查询请求参数
"query_config":"""# 该字典为查询条件（设定为可自定义的部分），可以修改值value，但请勿更改关键字key
query_dict = {
    # 搜索的关键词，如【'企业社会责任'】
    'searchkey':None,
    # 发布起始时间，如【'2023-01-04'】【''表示不进行限制 】 
    'sdate':'', 
    # 发布截止时间，如【'2023-02-24'】【''表示不进行限制 】
    'edate':'', 
    # 是否进行全文搜索，【'false'为只搜索标题，'true'为搜索全文 】
    'isfulltext':'false', 
    # 板块筛选，【''为全部板块，'shj'为深沪京，'s'为三板... 】
    'type':None, 
}
if None in query_dict.values():
    raise Exception("请配置query_config文件")
""",

# 数据库
"database_config":"""connect_config = {
    'host':None,
    'user':'root',
    'password':None,

}
# mysql_config
# oracle config
if None in connect_config.values():
    raise Exception("请配置database_config文件")
""",

# 请求接口
"requests_config":"""HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
PORT = -1
""",

}


def _exist_or_create(config_name_string="requests_config"):
    config_par_dir = 'config/'
    config_path = config_par_dir + config_name_string + '.py'
    if not os.path.isfile(config_path):
        text = _config_text[config_name_string]
        try:
            with open(config_path,'w')as f:
                f.write(text)
            print(f"√ 成功创建配置文件【 {config_name_string} 】，请根据实际情况前往【 {config_par_dir} 】下进行配置")
        except Exception as e:
            print(f"× 创建配置文件【 {config_name_string} 】失败，错误原因如下：")
            print(e)
    # else:
    #     print(f"√ 配置文件【 {config_name_string} 】已存在，可前往【 {config_par_dir} 】下进行配置")
    return


for config_name_string in _config_text.keys():
    _exist_or_create(config_name_string)
