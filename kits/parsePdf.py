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
    res = {}
    pd = parsePdf(pdf_dir)
    res['pages_num'] = pd.get_pages_num()
    res['words_num'] = pd.get_words_num()
    print(f"【 {pdf_dir} 】,【 {res} 】")
    return res