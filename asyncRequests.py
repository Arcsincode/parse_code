import asyncio
import aiohttp
import os
import time
import random



from requests_config import HEADER
from requests_config import PORT


if PORT==-1:
    PROXIES=''
else:
    PROXIES = f"http://127.0.0.1:{PORT}"


COUNT_LIST = [0]
TOTAL_LIST = [1]
TIMEOUT_TAO = 5 # 二进制指数退避的争用期窗口大小

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took 【 {end - start:.6f} 】seconds.")
        return res

    return wrapper


def random_time_out(timeout_times,):
    if timeout_times > 0:
        time.sleep(TIMEOUT_TAO * random.uniform(0,pow(2,timeout_times)-1))
    timeout_times += 1
    return timeout_times


def get_progress(count,total):
    """[012/100]"""
    max_len = len(str(total))
    count_len = len(str(count))
    count_res = '0'*(max_len-count_len)+str(count)
    return f"[{count_res}/{total}]"



async def get_json(session, url,):
    """
    :return: response.json()
    """ 
    print(f"将要POST：【 {url} 】")
    timeout_times = 0
    while True:
        timeout_times = random_time_out(timeout_times,)
        try:
            response = await session.get(url,headers=HEADER,proxy=PROXIES,)
            if response.status == 200:
                break
        except Exception as e:
            print(e)
            continue
        
    res = await response.json()
    COUNT_LIST[0] += 1
    print(f"{get_progress(COUNT_LIST[0],TOTAL_LIST[0])} √ POST")
    return res



async def post_json(session, url, data,):
    """
    :return: response.json()
    """ 
    print(f"将要POST：【 {url} 】")
    timeout_times = 0
    while True:
        timeout_times = random_time_out(timeout_times,)
        try:
            response = await session.post(url, data=data, headers=HEADER,proxy=PROXIES,)
            if response.status == 200:
                break
        except Exception as e:
            print(e)
            continue
        
    res = await response.json()
    COUNT_LIST[0] += 1
    print(f"{get_progress(COUNT_LIST[0],TOTAL_LIST[0])} √ POST")
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
    file_size_bytes = 0
    # timeout = TIMEOUT
    while True:
        timeout_times = random_time_out(timeout_times,)
        try:
            response = await session.get(url, headers=HEADER,proxy=PROXIES,)
            file_size_bytes = int(response.headers.get('Content-Length'))
            
            if response.status == 200:
                pass
            else:
                raise asyncio.exceptions.TimeoutError
            
            # 若已下载则跳过
            if os.path.isfile(file_path):
                with open(file_path,'rb')as f:
                    if len(f.read()) == file_size_bytes:
                        COUNT_LIST[0] += 1
                        print(f"{get_progress(COUNT_LIST[0],TOTAL_LIST[0])}  ! 文件已存在：【 {name} 】")
                        return file_path,0
                    else:
                        print(f"× 文件大小异常，准备重新下载： {name} ")

            # 写入
            with open(file_path,'wb')as f:
                f.write(await response.content.read())
                COUNT_LIST[0] += 1
                print(f"{get_progress(COUNT_LIST[0],TOTAL_LIST[0])}  √ 下载完成：【 {name} 】")

            break

        except asyncio.exceptions.TimeoutError:
            print(f"第 {timeout_times} 次超时...文件为：【 {name} 】")
            continue
        except Exception as e:
            print(e)
            if timeout_times < 5:
                continue
            else:
                break


    return file_path,file_size_bytes/1024/1024


def downloads_tasks(session, names_urls,to_dir):
    if type(to_dir)==str:
        tasks = [asyncio.create_task(download(session, name_url,to_dir)) for name_url in names_urls]
    elif type(to_dir)==list:
        tasks = [asyncio.create_task(download(session, name_url,to_dir0)) for (name_url,to_dir0) in zip(names_urls,to_dir) ]
    # print(tasks)
    return tasks


# async def async_gets_jsons_temp(urls):
#     COUNT_LIST[0] = 0
#     TOTAL_LIST[0] = len(urls)
#     async with aiohttp.ClientSession() as session:
#         tasks = [asyncio.create_task(get_json(session,url)) for url in urls]
#         jsons = await asyncio.gather(*tasks)    
#     return jsons


@timeit
def async_gets_jsons(urls):
    async def _async_gets_jsons(urls):
        COUNT_LIST[0] = 0
        TOTAL_LIST[0] = len(urls)
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(get_json(session,url)) for url in urls]
            jsons = await asyncio.gather(*tasks)    
        return jsons
    # return asyncio.run(_async_gets_jsons(urls))
    return asyncio.run(_async_gets_jsons(urls))


@timeit
def async_posts_jsons(urls,datas):  
    async def _async_posts(urls,datas):    
        COUNT_LIST[0] = 0
        TOTAL_LIST[0] = len(urls)
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(post_json(session,url,data)) for url,data in zip(urls,datas)]
            jsons = await asyncio.gather(*tasks)    
        return jsons
    return asyncio.run(_async_posts(urls,datas))


@timeit
def async_downloads(names_urls,to_dir):
    async def _async_downloads(names_urls,to_dir):
        # import getUrls
        # names_urls = getUrls.get_name_url(stack_code, START_DATE, END_DATE,**args)
        start = time.perf_counter()
        COUNT_LIST[0] = 0
        TOTAL_LIST[0] = len(names_urls)
        async with aiohttp.ClientSession() as session:
            tasks = downloads_tasks(session,names_urls,to_dir)
            res = await asyncio.gather(*tasks)    
        download_dir,download_sizes = list(zip(*res))
        end = time.perf_counter()
        all_size = sum(download_sizes)
        spend_time = end - start
        print(f"共下载 【 {all_size:.3f} 】 MB 数据")
        print(f"共花费 【 {spend_time:.3f} 】 秒")
        print(f"下载速度为 【 {all_size/spend_time:.3f} 】 MB/s")
        return download_dir
    return asyncio.run(_async_downloads(names_urls,to_dir))
        

if __name__=='__main__':
    import getUrls
    names_urls = getUrls.get_name_url('000045','2011','2023')
    async_downloads(names_urls,to_dir='./data')
    # asyncio.run(async_downloads(names_urls,to_dir='./data'))
    # names_urls = getUrls.get_name_url('000010','2011','2023')
    # asyncio.run(async_downloads(names_urls,to_dir='./data'))
