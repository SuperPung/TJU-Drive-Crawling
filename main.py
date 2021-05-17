import requests
import json


def crawl():
    postUrl = 'http://pan.tju.edu.cn:9123/v1/link?method=get'
    payloadData = {
        "link": "95A04E31C5BD079C95255EA95D16F10D",
        "password": "bdd5",
        "docid": ""
    }
    payloadHeader = {
        "Content-Type": "text/plain;charset=UTF-8",
        "Referer": "http://pan.tju.edu.cn/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.212 Safari/537.36 "
    }

    s = requests.session()
    r = s.post(postUrl, data=json.dumps(payloadData), headers=payloadHeader)
    print("POST Status code:", r.status_code)

    print(r.text)
    url = 'http://pan.tju.edu.cn:9123/v1/link?method=listdir'
    data = {
        "link": "95A04E31C5BD079C95255EA95D16F10D",
        "password": "bdd5",
        "by": "name",
        "sort": "asc"
    }
    getUrl = s.post(url, data=json.dumps(data), headers=payloadHeader)
    text = getUrl.text
    print(json.loads(text))


if __name__ == '__main__':
    crawl()
