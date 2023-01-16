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
TIMEOUT_TAO = 10 # 二进制指数退避的争用期窗口大小

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took 【 {end - start:.6f} 】seconds.")
        return res

    return wrapper


def get_progress(count,total):
    """[012/100]"""
    max_len = len(str(total))
    count_len = len(str(count))
    count_res = '0'*(max_len-count_len)+str(count)
    return f"[{count_res}/{total}]"


async def post(session, url, data,):
    """
    :return: response.json()
    """ 
    print(f"将要POST：【 {url} 】")
    while True:
        try:
            response = await session.post(url, data, headers=HEADER,proxy=PROXIES,)
        except Exception as e:
            print(e)
            continue
        if res.status==200:
            break
    res = await response.json()
    COUNT_LIST[0] += 1
    print(f"{get_progress(COUNT_LIST[0],TOTAL_LIST[0])} √")
    return res


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

    # time.sleep(random.uniform(1,2)/5)
    timeout_times = 0
    # timeout = TIMEOUT
    while True:
        time.sleep(TIMEOUT_TAO * random.uniform(0,pow(2,timeout_times)-1))
        try:
            response = await session.get(url, headers=HEADER,proxy=PROXIES,)
            file_size_bytes = int(response.headers.get('Content-Length'))

            # 若已下载则跳过
            if os.path.isfile(file_path):
                with open(file_path,'rb')as f:
                    if len(f.read()) == file_size_bytes:
                        COUNT_LIST[0] += 1
                        print(f"{get_progress(COUNT_LIST[0],TOTAL_LIST[0])}  ! 文件已存在：【 {name} 】")
                        return 0
                    else:
                        print(f"× 文件大小异常，准备重新下载： {name} ")

            # 写入
            with open(file_path,'wb')as f:
                f.write(await response.content.read())
                COUNT_LIST[0] += 1
                print(f"{get_progress(COUNT_LIST[0],TOTAL_LIST[0])}  √ 下载完成：【 {name} 】")
            break
        except asyncio.exceptions.TimeoutError:
            timeout_times += 1
            # timeout *= 2
            print(f"第 {timeout_times} 次超时...文件：【 {name} 】")
            continue
        except Exception as e:
            break
            print(e)
    return file_size_bytes/1024/1024


def downloads_tasks(session, names_urls,to_dir):
    if type(to_dir)==str:
        tasks = [asyncio.create_task(download(session, name_url,to_dir)) for name_url in names_urls]
    elif type(to_dir)==list:
        tasks = [asyncio.create_task(download(session, name_url,to_dir0)) for (name_url,to_dir0) in zip(names_urls,to_dir) ]
    # print(tasks)
    return tasks


async def async_posts(urls,datas):    
    start = time.perf_counter()
    COUNT_LIST[0] = 0
    TOTAL_LIST[0] = len(urls)
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(post(session,url,data)) for url,data in zip(urls,datas)]
        jsons = await asyncio.gather(*tasks)    
    return jsons


async def async_downloads(names_urls,to_dir):
    # import getUrls
    # names_urls = getUrls.get_name_url(stack_code, START_DATE, END_DATE,**args)
    start = time.perf_counter()
    COUNT_LIST[0] = 0
    TOTAL_LIST[0] = len(names_urls)
    async with aiohttp.ClientSession() as session:
        tasks = downloads_tasks(session,names_urls,to_dir)
        download_sizes = await asyncio.gather(*tasks)    

        end = time.perf_counter()
        all_size = sum(download_sizes)
        spend_time = end - start
        # print("Finish")
        print(f"共下载 【 {all_size:.3f} 】 MB 数据")
        print(f"共花费 【 {spend_time:.3f} 】 秒")
        print(f"下载速度为 【 {all_size/spend_time:.3f} 】 MB/s")
        return
        


async def async_posts(urls,datas):
    # import getUrls
    import aiohttp
    # names_urls = getUrls.get_name_url(stack_code, START_DATE, END_DATE,**args)
    start = time.perf_counter()
    COUNT_LIST[0] = 0
    TOTAL_LIST[0] = len(names_urls)
    async with aiohttp.ClientSession() as session:
        tasks = downloads_tasks(session,names_urls,to_dir)
        download_sizes = await asyncio.gather(*tasks)    

        end = time.perf_counter()
        all_size = sum(download_sizes)
        spend_time = end - start
        # print("Finish")
        print(f"共下载 【 {all_size:.3f} 】 MB 数据")
        print(f"共花费 【 {spend_time:.3f} 】 秒")
        print(f"下载速度为 【 {all_size/spend_time:.3f} 】 MB/s")
        return

# @timeit
# def async_download_from_code(stack_code, START_DATE, END_DATE,to_dir):
#     asyncio.run(main(to_dir,stack_code, START_DATE, END_DATE,))


if __name__=='__main__':
    import getUrls
    names_urls = getUrls.get_name_url('000045','2011','2023')
    asyncio.run(async_downloads(names_urls,to_dir='./data'))
    names_urls = getUrls.get_name_url('000006','2011','2023')
    asyncio.run(async_downloads(names_urls,to_dir='./data'))
