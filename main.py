import requests
import json


def crawl():
    # POST 01
    post_url = 'http://pan.tju.edu.cn:9123/v1/link?method=get'
    payload_data = {
        "link": "95A04E31C5BD079C95255EA95D16F10D",
        "password": "bdd5",
        "docid": ""
    }
    payload_header = {
        "Content-Type": "text/plain;charset=UTF-8",
        "Referer": "http://pan.tju.edu.cn/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.212 Safari/537.36 "
    }

    s = requests.session()
    r = s.post(post_url, data=json.dumps(payload_data), headers=payload_header)
    print("POST Status code:", r.status_code)
    display_json(r.text)
    # POST 02
    content_url = 'http://pan.tju.edu.cn:9123/v1/link?method=listdir'
    content_data = {
        "link": "95A04E31C5BD079C95255EA95D16F10D",
        "password": "bdd5",
        "by": "name",
        "sort": "asc"
    }
    get_url = s.post(content_url, data=json.dumps(content_data), headers=payload_header)
    display_json(get_url.text)


def display_json(json_str):
    result = json.loads(json_str)
    for key in result:
        print(key, ":", result[key])


if __name__ == '__main__':
    crawl()
