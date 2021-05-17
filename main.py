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


def crawl(pan_url, password, old_dict):
    link = get_link(pan_url)
    data = get_data(link, password)
    text = get_text(data)
    new_dict = analysis(link, password, text, old_dict)
    return new_dict


def analysis(link, password, text, old_dict):
    with open('./json/root.json', 'w') as f:
        json.dump(text, f)
    new_dict = display_dict('.', link, password, json.loads(text), old_dict)
    return new_dict


def display_dict(path, link, password, root_dic, old_dict):
    global name, modified, docid, client_mtime, size
    new_dict = {}
    for key in root_dic:
        dir_file_list = root_dic[key]
        if not isinstance(dir_file_list, list):
            return
        elif key == 'dirs' and dir_file_list != []:
            for dir_dict in dir_file_list:
                if not isinstance(dir_dict, dict):
                    return
                for attribute, content in dir_dict.items():
                    if attribute == 'modified':
                        modified = sec2time(int(content))
                    elif attribute == 'name':
                        name = content
                    elif attribute == 'docid':
                        docid = content
                message = path + '【目录】' + name + '，修改于 ' + modified
                print(message)
                new_dict[docid] = modified
                if modified != old_dict[docid]:
                    print('UPDATE', message)
                data = get_data_with_docid(link, password, docid)
                text = get_text(data)
                new_path = path + '/' + name
                new_dict.update(display_dict(new_path, link, password, json.loads(text), old_dict))

        elif key == 'files':
            for file_dict in dir_file_list:
                if not isinstance(file_dict, dict):
                    return
                for attribute, content in file_dict.items():
                    if attribute == 'modified':
                        modified = sec2time(int(content))
                    elif attribute == 'name':
                        name = content
                    elif attribute == 'docid':
                        docid = content
                    elif attribute == 'client_mtime':
                        client_mtime = sec2time(int(content))
                    elif attribute == 'size':
                        size = str(content)
                message = path + '【文件】' + name + '，修改于 ' + modified + '，所在目录修改于 ' + client_mtime + '，文件大小为 ' + size + ' 字节'
                print(message)
                new_dict[docid] = client_mtime
                if client_mtime != old_dict[docid]:
                    print('UPDATE', message)
    return new_dict


def get_text(data):
    s = requests.session()
    get_root = s.post(url, data=json.dumps(data), headers=payload_header)
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
    return str(style_time)


def get_link(pan_url: str):
    paths = pan_url.split('/')
    return paths[len(paths) - 1]


if __name__ == '__main__':
    filename = './json/root.json'
    if not os.path.exists(filename):
        with open(filename, 'w'):
            print(filename, '创建成功')
    global old_dict
    with open(filename, 'r', encoding='UTF-8') as f:
        old_dict = json.load(f)

    ############################### 下方为可修改区域 ###############################
    tju_pan_url = 'http://pan.tju.edu.cn/#/link/95A04E31C5BD079C95255EA95D16F10D'
    passwd = 'bdd5'
    ############################### 上方为可修改区域 ###############################

    new_dict = crawl(tju_pan_url, passwd, old_dict)

    json_str = json.dumps(new_dict)
    with open(filename, 'w') as f:
        f.write(json_str)
