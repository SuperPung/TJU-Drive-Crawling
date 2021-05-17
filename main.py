import requests
import json
import os
import time

url = 'http://pan.tju.edu.cn:9123/v1/link?method=listdir'
payload_header = {
    "Content-Type": "text/plain;charset=UTF-8",
    "Referer": "http://pan.tju.edu.cn/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/90.0.4430.212 Safari/537.36 "
}
NAME_MAP = {
    'docid': 'docid',
    'modified': '目录修改时间',
    'name': '名称',
    'rev': 'rev',
    'size': '大小/字节',
    'client_mtime': '文件修改时间'
}


def crawl(pan_url, password):
    link = get_link(pan_url)
    data = get_data(link, password)
    text = get_text(data)

    with open('./json/root.json', 'w') as f:
        json.dump(text, f)

    display_dict(json.loads(text))


def display_dict(root_dic):
    for key in root_dic:
        dir_file_list = root_dic[key]
        if not isinstance(dir_file_list, list):
            return
        elif key == 'dirs':
            print('/********** 目录列表 **********/')
        elif key == 'files':
            print('/********** 文件列表 **********/')

        for dir_file_dict in dir_file_list:
            if not isinstance(dir_file_dict, dict):
                return
            for attribute, content in dir_file_dict.items():
                if attribute == 'modified' or attribute == 'client_mtime':
                    content = sec2time(int(content))
                print(NAME_MAP[attribute], ':', content)
            print('/------------------/')


def get_sub_dir(link, password, docid):
    data = get_data_with_docid(link, password, docid)


def get_text(data):
    s = requests.session()
    get_root = s.post(url, data=json.dumps(data), headers=payload_header)
    print("POST Status code:", get_root.status_code)
    return get_root.text


def get_data(link, password):
    data = {
        "link": link,
        "password": password,
        "by": "name",
        "sort": "asc"
    }
    return data


def get_data_with_docid(link, password, docid):
    data = {
        "link": link,
        "password": password,
        "docid": docid,
        "by": "name",
        "sort": "asc"
    }
    return data


def sec2time(million_seconds):
    time_stamp = round(million_seconds / 1000000)
    time_array = time.localtime(time_stamp)
    style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return style_time


def get_link(pan_url: str):
    paths = pan_url.split('/')
    return paths[len(paths) - 1]


if __name__ == '__main__':
    filename = './json/root.json'
    if not os.path.exists(filename):
        with open(filename, 'w'):
            print(filename, '创建成功')

    crawl('http://pan.tju.edu.cn/#/link/95A04E31C5BD079C95255EA95D16F10D', 'bdd5')
