from flask import request as r
import module_sql_str as modul_sql
from datetime import datetime
from functools import wraps
import uuid
from flask import render_template, redirect, url_for, make_response
from timeit import default_timer


class class_list_requests_users:
    def __init__(self):
        self.ip_dict = {}

    def check_request(self, ip):
        if self.ip_dict.get(ip):

            if default_timer() < self.ip_dict[ip][2]:
                return 1

            self.ip_dict[ip][1] += 1
            if self.ip_dict[ip][1] >= 10:

                if default_timer() - self.ip_dict[ip][0] < 10:
                    self.ip_dict[ip][2] = default_timer() + 20
                else:
                    self.ip_dict[ip][1] = 0
                    self.ip_dict[ip][0] = default_timer()
        else:
            self.ip_dict[ip] = [default_timer(), 0, 0]


list_requests_users = class_list_requests_users()


key_item = "12345"


def user_ip(r):

    # if r.environ.get('HTTP_X_FORWARDED_FOR') is None:
    #    ip = r.environ['REMOTE_ADDR']
    # else:
    #    ip = r.environ['HTTP_X_FORWARDED_FOR']

    if r.environ.get("HTTP_X_FORWARDED_FOR"):
        ip = r.environ["HTTP_X_FORWARDED_FOR"]
    else:
        ip = r.environ["REMOTE_ADDR"]
    return ip


def order(list_Replys):
    for i in range(len(list_Replys)):
        for n in range(i):
            if list_Replys[n].Id in list_Replys[i].ListTo:
                list_Replys[n].Replys.append(list_Replys[i].Id)
    return list_Replys


def check_request(func):
    @wraps(func)
    def wrapper():
        ip = user_ip(r)
        if list_requests_users.check_request(ip):
            return ip
        else:
            return func()

    return wrapper


def make_user_cookie(func):
    @wraps(func)
    def wrapper():
        res = func()

        if not r.cookies.get("user"):
            res = make_response(res)
            res.set_cookie("user", str(uuid.uuid4()))

        return res

    return wrapper


def check_ip(func):
    @wraps(func)
    def wrapper():
        ip = user_ip(r)
        modul_sql.make_ip(ip, "", str(r.cookies.get("user")))
        is_block = modul_sql.get_ip_block(ip)
        if is_block and datetime.today().strftime("%Y-%m-%d %H:%M:%S") <= is_block[2]:
            return render_template("block_page.html", item=is_block)
        return func()

    return wrapper


def check_key(func):
    @wraps(func)
    def wrapper():
        if r.cookies.get("key") != key_item:
            return "Что ты тут делаешь?"
        return func()

    return wrapper
