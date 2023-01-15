import asyncio
import aiohttp
import os
import time
import random



from config import HEADER
from config import PORT


if PORT==-1:
    PROXIES=''
else:
    PROXIES = f"http://127.0.0.1:{PORT}"

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took 【 {end - start:.6f} 】seconds.")
        return res

    return wrapper


async def download(session, name_url, to_dir):
    """返回response.text

    """
    try:
        os.mkdir(to_dir)
        print(f"已创建文件夹{to_dir}")
    except:
        pass

    name,url = name_url
    print(f"将要下载：【 {name} 】")
    
    time.sleep(random.uniform(1,2)/5)
    response = await session.get(url, headers=HEADER,proxy=PROXIES)
    # 写入
    file_path = os.path.join(to_dir,name)
    if os.path.isfile(file_path):
        print("文件已存在！")
        pass
    else:
        with open(file_path,'wb')as f:
            f.write(await response.content.read())
    return

def download_tasks(session, names_urls,to_dir):
    if type(to_dir)==str:
        tasks = [asyncio.create_task(download(session, name_url,to_dir)) for name_url in names_urls]
    elif type(to_dir)==list:
        tasks = [asyncio.create_task(download(session, name_url,to_dir0)) for (name_url,to_dir0) in zip(names_urls,to_dir) ]
    # print(tasks)
    return tasks



# async def async_download_from_code(stack_code, START_DATE, END_DATE,to_dir,**args):
async def async_download(names_urls,to_dir):
# async def main(to_dir,**args):
    # import getUrls
    import aiohttp
    # names_urls = getUrls.get_name_url(stack_code, START_DATE, END_DATE,**args)
    start = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = download_tasks(session,names_urls,to_dir)
        await asyncio.gather(*tasks)    

        end = time.perf_counter()
        print(f"It took 【 {end - start:.6f} 】seconds to download.")
        return
        
# @timeit
# def async_download_from_code(stack_code, START_DATE, END_DATE,to_dir):
#     asyncio.run(main(to_dir,stack_code, START_DATE, END_DATE,))


if __name__=='__main__':
    import getUrls
    names_urls = getUrls.get_name_url('000006','2011','2023')
    asyncio.run(async_download(names_urls,to_dir='./data'))
