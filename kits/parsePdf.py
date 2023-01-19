import pdfplumber

class parsePdf:
    def __init__(self,pdf_dir) -> None:
        self.pdf = pdfplumber.open(pdf_dir)
        self.pages = self.pdf.pages


    def get_pages_num(self):
        return len(self.pages)


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


def parse_pdf(pdf_dir):
    """res['pages_num'] = pd.get_pages_num()
    res['words_num'] = pd.get_words_num()
    """
    res = {}
    pd = parsePdf(pdf_dir)
    res['pages_num'] = pd.get_pages_num()
    res['words_num'] = pd.get_words_num()
    print(f"【 {pdf_dir} 】,【 {res} 】")
    return res


def parse_pdf_mp(pdf_dir,mp_value,total_num,mp_lock):
    res = {}
    pd = parsePdf(pdf_dir)
    res['pages_num'] = pd.get_pages_num()
    res['words_num'] = pd.get_words_num()
    with mp_lock:
        temp_v = mp_value.get()+1
        mp_value.set(temp_v)
        print(f"[{temp_v}/{total_num}]【 {pdf_dir} 】,【 {res} 】")

    return res
    

if __name__ == '__main__':
    import multiprocessing
    value = multiprocessing.Manager().Value('i',0)
    lock = multiprocessing.Manager().Lock()
    lock = multiprocessing.Lock()
    from kits.multi_process import multi_process_star
    a = ['11.2','3.4','55.6']
    total_num =3
    pool = multiprocessing.Pool(8)
    res_all = []
    # for par_dir in par_dirs:
    #     res = pool.apply_async(parse_pdf,(par_dir,))
    #     res_all.append(res)
    res_all = pool.starmap(parse_pdf_mp,[(a,1,2)]*3)


    multi_process_star(parse_pdf_mp,a)
    multi_process_star(parse_pdf_mp,list(zip(a,[value]*3,[total_num]*3,[lock]*3)))
    parse_pdf_mp(a[0],value,total_num)
    b = value.get()
    print(b)
    value.set(b+1)
