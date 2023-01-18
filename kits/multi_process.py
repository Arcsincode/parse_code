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
def multi_process(parse_pdf,par_dirs):
    pool = multiprocessing.Pool(8)
    res_all = []
    # for par_dir in par_dirs:
    #     res = pool.apply_async(parse_pdf,(par_dir,))
    #     res_all.append(res)
    res_all = pool.map(parse_pdf,par_dirs)
    # print(res_all)
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