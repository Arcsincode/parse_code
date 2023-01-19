import config
from config import database_config
import pymysql
from func_timeout import func_timeout,FunctionTimedOut
connect_dict = database_config.connect_config


def rt_print(f):
    def wrapper(*args,**kwargs):
        res = f(*args,**kwargs)
        print(res)
        return res
    return wrapper


class MyDb(pymysql.connect):

    def keep_alive(self,func):

        def wrapper(*args,**kwargs):
            try:
                res = func_timeout(self.timeout,func,args,kwargs)
                print("SQL语句正常完成")
            except FunctionTimedOut:
                print("已检测到MySQL连接断开...正在重新连接")
                self.connect()
                res = func(*args,**kwargs)
                print("已重新建立MySQL连接并成功执行SQL语句")
            return res
        return wrapper


    def __init__(self,database=None) -> None:
        print("正在建立MySQL连接...")
        pymysql.connect.__init__(self,database=database,**connect_dict)
        print("已建立MySQL连接")
        self.cursor = self.cursor()
        self.execute = self.keep_alive(self.cursor.execute)
        # self.prtexecute = 
        # self.rtexecute = 
        self.fetch = self.cursor.fetchall
        self.pfetch = rt_print(self.cursor.fetchall)
        self.timeout = 20

        if database:
            self.execute(f"use {database}")
            print(f"已选择数据库【 {database} 】")
        pass

    
    def close(self):
        pymysql.connect.close(self)
        print("已关闭MySQL连接")


def generate_create_sql(table_name,columns_infos_dict,primary_key):
    """For Example:
    columns_infos_dict = {
    'secCode':'VARCHAR(20) NOT NULL',
    'secName':'VARCHAR(30) NOT NULL',
    'orgId':'VARCHAR(50)',
    'announcementId':'VARCHAR(30) NOT NULL',
    'announcementTitle':'VARCHAR(100) NOT NULL',
    'announcement_title':'VARCHAR(100) NOT NULL',
    'announcementTime':'BIGINT UNSIGNED',
    'announcement_year':'YEAR', # 实际时间如'2018'
    'adjunctUrl':'VARCHAR(100) NOT NULL',
    'record_time':'DATE', # 记录日期
    'pages_num':'INT UNSIGNED',
    'words_num':'BIGINT UNSIGNED'
}"""
    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}`" + """(
    """ + ',\n    '.join( [f"`{key}` {value}" for key,value in columns_infos_dict.items()] ) +f""",
    PRIMARY KEY ( `{primary_key}` )
)CHARSET=utf8;"""
    return sql
        

def generate_values(input_dict):
    values = '(' + ','.join([f"""\"{value}\"""" for value in input_dict.values()]) + ')'
    return values
    

def generate_insert_sql(table_name,input_args):
    """可传入一个字典或多个共同键的字典列表"""
    if type(input_args) == list:
        column_names = ','.join(input_args[0].keys())
    elif type(input_args) == dict:
        column_names = ','.join(input_args.keys())
    valuess = ','.join([generate_values(input_dict) for input_dict in input_args])
    sql = f"INSERT IGNORE INTO `{table_name}` ( {column_names} ) VALUES {valuess};"
    return sql


if __name__=="__main__":
    db = MyDb('Juchao')
    db.execute("SHOW TABLES")
    db.fetch()
    db.execute("SELECT * FROM 社会及ok")
    db.pfetch()