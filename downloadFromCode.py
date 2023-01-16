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


COUNT_LIST = [0]
TOTAL_LIST = [0]


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
    print(f"将要下载：【 {name} | {url} 】")
    
    file_path = os.path.join(to_dir,name)
    # if os.path.isfile(file_path):
    #     print("=> ! 文件已存在")
    #     return 0

    time.sleep(random.uniform(1,2)/5)
    response = await session.get(url, headers=HEADER,proxy=PROXIES,timeout=30)
    print(response)
    # 写入
    with open(file_path,'wb')as f:
        f.write(await response.content.read())
        COUNT_LIST[0] += 1
        print(f"[{COUNT_LIST[0]}/{TOTAL_LIST[0]}]  √ 【 {name} 】下载完成")
    return int(response.headers.get('Content-Length'))/1024/1024

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
    TOTAL_LIST[0] = len(names_urls)
    async with aiohttp.ClientSession() as session:
        tasks = download_tasks(session,names_urls,to_dir)
        download_sizes = await asyncio.gather(*tasks)    

        end = time.perf_counter()
        # print("Finish")
        print(f"共下载 【 {sum(download_sizes)} 】 MB 数据")
        print(f"共花费 【 {end - start:.6f} 】 秒")
        return
        
# @timeit
# def async_download_from_code(stack_code, START_DATE, END_DATE,to_dir):
#     asyncio.run(main(to_dir,stack_code, START_DATE, END_DATE,))


if __name__=='__main__':
    import getUrls
    names_urls = getUrls.get_name_url('000070','2011','2023')
    asyncio.run(async_download(names_urls,to_dir='./data'))
