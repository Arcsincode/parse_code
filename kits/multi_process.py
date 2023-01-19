import multiprocessing 
import time


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took 【 {end - start:.6f} 】seconds.")
        return res
    return wrapper


@timeit
def multi_process(func,arg_list,process_num=8):
    pool = multiprocessing.Pool(process_num)
    res_all = []
    res_all = pool.map(func,arg_list)
    pool.close()
    pool.join()
    return res_all


@timeit
def multi_process_star(func,args_list,process_num=8):
    pool = multiprocessing.Pool(process_num)
    res_all = []
    res_all = pool.starmap(func,args_list)
    pool.close()
    pool.join()
    return res_all
    


if __name__=='__main__':
    par_dirs = ['./data/search_res/中集集团：2017年社会责任暨环境、社会及管治报告.pdf',
 './data/search_res/中集集团：2018社会责任暨环境、社会及管治报告.pdf',
 './data/search_res/中集集团：社会责任暨环境、社会及管治报告（2019）.pdf',
 './data/search_res/中集集团：2016年环境、社会及管治报告.pdf',
 './data/search_res/申万宏源：2018年度环境、社会及管治报告.pdf',
 './data/search_res/珠海港：珠海港股份有限公司2020年度环境、社会及管治（ESG）报告.pdf',
 './data/search_res/珠海港：2021年度环境、社会及管治（ESG）报告.pdf',
 './data/search_res/丽珠集团：2020年度环境、社会及管治报告.pdf',
 './data/search_res/丽珠集团：2021年度环境、社会及管治报告.pdf',
 './data/search_res/丽珠集团：2017年度环境、社会及管治报告.pdf']
    from parsePdf import parse_pdf
    multi_process(parse_pdf,par_dirs)
