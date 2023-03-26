import multiprocessing 

import os,sys
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

import pdfplumber

class parsePdf:
    def __init__(self,pdf_dir) -> None:
        self.pdf = pdfplumber.open(pdf_dir)
        self.pages = self.pdf.pages


    def get_pages_num(self):
        return len(self.pages)


    # def get_words_num(self,):#ignore_text_list=[]):
    #     # ignore_text_list += '\n'
    #     # counts = len(self.pdf.chars)
        
    #     counts = 0
    #     for page in self.pages:
    #         counts += len(page.chars)
    #     counts
    #     # for page in self.pages:
    #     #     page.extract_text
    #     #     counts += 
    #     return counts

    def get_words_num(self,ignore_text_list=[]):
        ignore_text_list += ['\n',' ']
        count = 0
        for page in self.pages:
            text = page.extract_text()
            for ignore_text in ignore_text_list:
                text = text.replace(ignore_text,'')
            count += len(text)
        count
        return count


    def __del__(self):
        self.pdf.close()
        return

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

def parse_pdf(pdf_dir):
    res = {}
    pd = parsePdf(pdf_dir)
    res['pages_num'] = pd.get_pages_num()
    res['words_num'] = pd.get_words_num()
    print(res)
    return res

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
    multi_process(parse_pdf,par_dirs)