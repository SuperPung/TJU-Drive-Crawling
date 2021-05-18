import requests
import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import conf

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
    return analysis(link, password, text, old_dict)


def analysis(link, password, text, old_dict):
    with open('./json/root.json', 'w') as f:
        json.dump(text, f)
    return display_dict('.', link, password, json.loads(text), old_dict)


def display_dict(path, link, password, root_dic, old_dict):
    global name, modified, docid, client_mtime, size
    new_dict = {}
    message_update = []
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
                if docid not in old_dict or modified != old_dict[docid]:
                    print('UPDATE', message)
                    message_update.append(message)
                data = get_data_with_docid(link, password, docid)
                text = get_text(data)
                new_path = path + '/' + name
                (new_dict_ret, message_update_ret) = display_dict(new_path, link, password, json.loads(text), old_dict)
                new_dict.update(new_dict_ret)
                message_update.extend(message_update_ret)

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
                if docid not in old_dict or client_mtime != old_dict[docid]:
                    print('UPDATE', message)
                    message_update.append(message)
    return new_dict, message_update


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


def send_email(message_subject, message_content):
    # 第三方 SMTP 服务
    mail_host = conf.Config.mail_host  # 设置服务器
    mail_user = conf.Config.mail_user  # 用户名
    mail_pass = conf.Config.mail_pass  # 口令

    sender = conf.Config.sender
    receiver = conf.Config.receiver

    message = MIMEText(message_content, 'plain', 'utf-8')
    message['From'] = conf.Config.from_name + ' <' + sender + '>'
    message['To'] = receiver

    subject = message_subject
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp_obj = smtplib.SMTP_SSL(mail_host)
        smtp_obj.connect(mail_host, 465)  # 25 在服务器上不能跑
        smtp_obj.login(mail_user, mail_pass)
        smtp_obj.sendmail(sender, receiver, message.as_string())
        print("邮件发送成功")

    except smtplib.SMTPException:
        print("发生错误: 无法发送邮件")


def format_message(message_list):
    if not isinstance(message_list, list) or message_list == []:
        return ''
    message = '下面是本次更新的内容，请查收：\n\n\n'
    for mes in message_list:
        message += mes + '\n\n'
    return message


if __name__ == '__main__':
    filename = './json/root.json'
    if not os.path.exists(filename):
        with open(filename, 'w'):
            print(filename, '创建成功')
    else:
        with open(filename, 'r', encoding='UTF-8') as f:
            try:
                old_dict = json.load(f)
            except json.decoder.JSONDecodeError:
                old_dict = {}

    new_dict, message_to_send = crawl(conf.Config.tju_pan_url, conf.Config.password, old_dict)

    json_str = json.dumps(new_dict)
    with open(filename, 'w') as f:
        f.write(json_str)
    if format_message(message_to_send) != '':
        send_email('网盘更新提醒', format_message(message_to_send))
