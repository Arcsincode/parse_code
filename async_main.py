import pandas as pd
import getUrls 
import asyncio
import downloadFromCode
import os




if __name__=="__main__":
    START_DATE,END_DATE = ['2011','2023']
    PAR_DIR = './data/'
    # 起始代码
    START_CODE = ''
    
    try:
        os.mkdir(PAR_DIR)
        print(f"已创建文件夹{PAR_DIR}")
    except:
        pass
    
    code_df = pd.read_csv('./code_orgId.csv',dtype=str,)
    code = code_df.set_index('code')
    for stock_code,row in code.loc[START_CODE:].iterrows():
        print(row)
        print(f"【 {stock_code} 】")
        names_urls = getUrls.get_name_url(stock_code,START_DATE,END_DATE)
        asyncio.run(downloadFromCode.async_download(names_urls,to_dir=os.path.join(PAR_DIR,stock_code)))
        print(f"【 {stock_code} 】 Done!")