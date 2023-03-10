import pandas as pd
import kits.getUrls as getUrls 
import asyncio
import kits.asyncRequests as asyncRequests 
import os




def main():
    global CURRENT_NUM
    # 逐个代码进行
    if MODE == 1:
        for stock_code,row in SELECT_DF.iterrows():
            print('')
            print('')
            print(row)
            print("==================================")
            print(f"【 {stock_code} 】  {CURRENT_NUM}/{len(SELECT_DF)}")
            CURRENT_NUM += 1
            names_urls = getUrls.get_name_url(stock_code,START_DATE,END_DATE)
            asyncRequests.async_downloads(names_urls,to_dir=os.path.join(PAR_DIR,stock_code))
            print(f"【 {stock_code} 】 Done!")
    

    # START_CODE:END_CODE 使用协程进行链接获取
    elif MODE == 3:
        names_urls = []
        to_dirs = []
        print(f"【 [{START_CODE},{END_CODE}) 】")
        stock_code_set = [i[0] for i in SELECT_DF.iterrows()]
        names_urls = getUrls.async_get_names_urls(stock_code_set,START_DATE,END_DATE)
        asyncRequests.async_downloads(names_urls,to_dir=PAR_DIR)
        print(f"【 [{START_CODE},{END_CODE}) 】 All Done!")
        CURRENT_NUM = len(SELECT_DF)


    # START_CODE:END_CODE 同时进行
    elif MODE == 2:
        names_urls = []
        to_dirs = []
        print(f"【 [{START_CODE},{END_CODE}) 】")
        for stock_code,row in SELECT_DF.iterrows():
            print('')
            print('')
            print(row)
            print("==================================")
            print(f"【 {stock_code} 】  {CURRENT_NUM}/{len(SELECT_DF)}")
            CURRENT_NUM += 1
            print(row)
            current_names_urls = getUrls.get_name_url(stock_code,START_DATE,END_DATE)
            names_urls += current_names_urls
            to_dirs += [ os.path.join(PAR_DIR,stock_code) ]*len(current_names_urls)
            
        asyncio.run(asyncRequests.async_downloads(names_urls,to_dir=to_dirs))
        print(f"【 [{START_CODE},{END_CODE}) 】 All Done!")



def my_input():
    res = input("""=====要输入代码请输入:【 '000065' 】，要输入第几行请输入（从0开始）:【 36 】=====
""")
    if res == "" or res == "None" or res == "none":
        print("输入None")
        return None
    elif res[0] in ["'","\"","“","”"]:
        print("已输入字符串")
        res = res[1:-1]
    else:
        print("已输入数字")
        res = int(res)
    return res


def transform_to_index(name,dataframe):
    if type(name)==str:
        index = name
    elif type(name)==int:
        index = dataframe.iloc[name].name
    return index


def pre_presented():
    global START_CODE,NUMS,END_CODE,SELECT_DF,START_input,END_input,MODE,START_DATE,END_DATE,PAR_DIR
    

    code_df = pd.read_csv('./code_orgId.csv',dtype=str,)
    code = code_df.set_index('code')
    print(code.head(5))

    # 起始代码和终止代码，None表示不进行限制，'222222'表示从222222开始
    print("\n:输入起始代码/行号")
    # START_CODE = my_input() #None
    START_input = my_input() #None
    # 转化成index
    START_CODE = transform_to_index(START_input,code)
    print(f"对应的起始代码为：[{START_CODE}")
    print("\n:输入要遍历的行数（int），若要输入结束代码/行号，请直接回车")
    NUMS = my_input()
    if not NUMS:
        print(":输入结束代码/行号（将会在访问该代码前停止，下次请从该代码处开始）")
        END_input = my_input()
        END_CODE = transform_to_index(END_input,code)
        SELECT_DF = code.loc[START_CODE:END_CODE]
        print(f"对应的结束代码为：{END_CODE})")
        print(f"对应的行数为：{len(SELECT_DF)}")
    else:        
        END_input = None
        SELECT_DF = code.loc[START_CODE:].iloc[:NUMS]
        print(SELECT_DF)
        END_CODE = code.loc[START_CODE:].iloc[NUMS].name
        print(f"对应的结束代码为：{END_CODE})")
        print(f"对应的行数为：{len(SELECT_DF)}")

    print("""
:模式：
1： START_CODE:END_CODE 单线程运作
2： START_CODE:END_CODE 仅使用协程下载文件
3： START_CODE:END_CODE 使用协程获取链接和下载文件【注：该方法会将所有文件下载到同一个文件夹中】
""")
    MODE = int(input())

    while True:
        input_num = input(f"""
当前其他配置为:
1： START_DATE = {START_DATE} （开始于 {START_DATE}-01-01 后发布）
2： END_DATE = {END_DATE} （截止至 {END_DATE}-12-31 前发布）
3： PAR_DIR = {PAR_DIR}
要修改请输入对应数字，否则直接回车跳过""")
        if not input_num:
            print("已跳过")
            break
        if input_num == '1':
            START_DATE = input()
        elif input_num == '2':
            END_DATE = input()
        elif input_num == '3':
            PAR_DIR = input()
            

    try:
        os.mkdir(PAR_DIR)
        print(f"已创建文件夹{PAR_DIR}")
    except:
        pass


if __name__=="__main__":
    START_DATE,END_DATE = ['2011','2023']
    PAR_DIR = './data/all_announcements'
    CURRENT_NUM = 1
    pre_presented()
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        print(f'\n本次输入为：【 start：{START_input}, nums：{NUMS}, end：{END_input} 】')
        print(f"本次代码范围为：【 ['{START_CODE}','{END_CODE}'),共{len(SELECT_DF)}条 】")
        print(f'当前为第【 {CURRENT_NUM} 】条')
