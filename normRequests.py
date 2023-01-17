import requests 
from requests_config import HEADER
from requests_config import PORT


if PORT==-1:
    PROXIES={}
else:
    PROXIES = {
        "http":f"127.0.0.1:{PORT}",
        "https":f"127.0.0.1:{PORT}"
    }



def get(url,**args):
    return requests.get(url,headers=HEADER,proxies=PROXIES,**args)


def post(url,data,**args):
    return requests.post(url=url,data=data,headers=HEADER,proxies=PROXIES,**args)


codes = requests.codes