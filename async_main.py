import pandas as pd
import getUrls 
import asyncio
import downloadFromCode
import os


def main():
    try:
        os.mkdir(PAR_DIR)
        print(f"已创建文件夹{PAR_DIR}")
    except:
        pass

    code_df = pd.read_csv('./code_orgId.csv',dtype=str,)
    code = code_df.set_index('code')
    # 逐个代码进行
    if MODE == 1:
        for stock_code,row in code.loc[START_CODE:END_CODE].iterrows():
            print(row)
            print(f"【 {stock_code} 】")
            names_urls = getUrls.get_name_url(stock_code,START_DATE,END_DATE)
            asyncio.run(downloadFromCode.async_download(names_urls,to_dir=os.path.join(PAR_DIR,stock_code)))
            print(f"【 {stock_code} 】 Done!")
    
    # START_CODE:END_CODE 同时进行
    elif MODE == 2:
        names_urls = []
        to_dirs = []
        print(f"【 {START_CODE,END_CODE} 】")
        for stock_code,row in code.loc[START_CODE:END_CODE].iterrows():
            print(row)
            current_names_urls = getUrls.get_name_url(stock_code,START_DATE,END_DATE)
            names_urls += current_names_urls
            to_dirs += [ os.path.join(PAR_DIR,stock_code) ]*len(current_names_urls)
            
        asyncio.run(downloadFromCode.async_download(names_urls,to_dir=to_dirs))
        print(f"【 {START_CODE,END_CODE} 】 All Done!")



if __name__=="__main__":
    START_DATE,END_DATE = ['2011','2023']
    PAR_DIR = './data/'
    # 起始代码和终止代码，None表示不进行限制，'222222'表示从222222开始
    START_CODE = '000065' #None
    END_CODE = None

    # 模式：
        # 1表示 START_CODE:END_CODE 逐一进行
        # 2表示 START_CODE:END_CODE 同时进行
    MODE = 2
    main()
    
