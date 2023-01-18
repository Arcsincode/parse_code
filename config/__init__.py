import os
config_text = {
# 数据库
"database_config":"""config = {
    'host':None,
    'user':'root',
    'password':None,
    'database':'',

}
# mysql_config
# oracle config
""",

# 请求
"requests_config":"""HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
PORT = -1
""",

}


def exist_or_create(config_name_string="requests_config"):
    config_par_dir = 'config/'
    config_path = config_par_dir + config_name_string + '.py'
    if not os.path.isfile(config_path):
        text = config_text[config_name_string]
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


for config_name_string in config_text.keys():
    exist_or_create(config_name_string)