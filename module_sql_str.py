import os
import sqlite3
import uuid
from datetime import datetime
from dto import *


def work(string, item=()):
    """
    Выполняет работу
    """
    os.chdir(os.path.join(os.path.dirname(__file__), "sql"))
    con = sqlite3.connect("main.db", check_same_thread=False)
    cur = con.cursor()
    response = list(cur.execute(string, item))
    con.commit()
    con.close()
    return response


def article_titles():
    """
    Возвращает список названий всех статей
    """
    article = ""
    for i in work("SELECT Title FROM Articles GROUP BY Title"):
        article = article + i[0] + "\n"
    title = "Список всех записей"
    return article, title


def delete_article(title):
    """
    Удаляет запись по названию
    """
    return work("DELETE FROM Articles WHERE Title=?", (title,))


def id_article(title):
    """
    Находит ид записи по названию
    """
    return work("SELECT Id FROM Articles WHERE Title=?", (title,))[0][0]


def delete_comments(id_article):
    """
    Удаляет комментарии по ид записи
    """
    return work("DELETE FROM Replys WHERE IdArticle=?", (id_article,))


def change_article(title, article, image):
    """
    Изменяет запись найденную по названию
    """
    return work(
        "UPDATE Articles SET Title=?, Article=?, Image=? WHERE Title=?",
        (title, article, image, title),
    )


def search_article(title):
    """
    Ищет запись по названию
    """
    item = work("SELECT * FROM Articles WHERE Title=?", (title,))
    if len(item) > 0:
        return item[0][0], item[0][1], item[0][3].split("/")[-1]
    else:
        return "", "", ""


def make_article(title, article, image):
    """
    Добавляет запись
    """
    return work(
        "INSERT INTO Articles VALUES (?, ?, ?, ?, ?)",
        (
            title,
            article,
            datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            image,
            str(uuid.uuid4()),
        ),
    )


def make_file():
    """
    Удаляет старый и добавляет новый файл
    """
    os.chdir(os.path.join(os.path.dirname(__file__), "sql"))
    os.remove("main.db")

    work(
        "CREATE TABLE Articles (Title text, Article text, DateString text, Image text, Id text)"
    )
    work(
        "CREATE TABLE Replys (Reply text, DateString text, IdArticle text, Id text, Ip text, ListTo text, IdCookie text)"
    )
    work("CREATE TABLE Preview (Id text, Title text, Article text, Image text)")
    work("INSERT INTO Preview VALUES ('preview', '', '', '')")
    work("CREATE TABLE Users (Ip text, DateString text, Url text, IdCookie text)")
    work("CREATE TABLE BlockList (Ip text, DateFrom text, DateTo text, Reply text)")


def make_ip(ip, url, id_cookie):
    """
    Добавляет запись посетителя
    """
    return work(
        "INSERT INTO Users VALUES (?, ?, ?, ?)",
        (ip, datetime.today().strftime("%Y-%m-%d %H:%M:%S"), url, id_cookie),
    )


def change_preview(title, article, image):
    """
    Изменяет запись предпросмотра
    """
    return work(
        "UPDATE Preview SET Title=?, Article=?, Image=? WHERE Id='preview'",
        (title, article, image),
    )


def return_preview():
    """
    Возвращает запись предпросмотра
    """
    item = work("SELECT * FROM Preview WHERE Id='preview'")[0]
    return item[1], item[2], item[3]


def search_article_by_id(id_item):
    """
    Ищет запись по ид
    """
    item = work("SELECT Title, Article FROM Articles WHERE Id=?", (id_item,))[0]

    return Articles(Title=item[0], Article=item[1])


def search_comments(id_item):
    """
    Ищет комментарии записи по ид
    """
    items = work(
        "SELECT * FROM Replys WHERE IdArticle=? ORDER BY DateString", (id_item,)
    )
    return [
        Replys(
            Reply=i[0],
            DateString=i[1],
            IdArticle=i[2],
            Id=i[3],
            Ip=i[4],
            ListTo=i[5],
            IdCookie=i[6],
        )
        for i in items
    ]


def make_comments(reply, id_item, ip, to, id_cookie):
    """
    Добавляет комментарий для записи
    """
    return work(
        "INSERT INTO Replys VALUES(?, ?, ?, ?, ?, ?, ?)",
        (
            reply,
            datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            id_item,
            str(uuid.uuid4()),
            ip,
            to,
            id_cookie,
        ),
    )


def list_titles_for_page(page, items_on_page):
    """
    Возвращает список записей для номера страницы
    """
    items = work(
        "SELECT Title, Image, Id FROM Articles ORDER BY DateString DESC LIMIT ? OFFSET ?",
        (str(items_on_page), str(page * items_on_page)),
    )

    return [Articles(Title=i[0], Image=i[1], Id=i[2]) for i in items]


def list_users(
    from_date, to_date, ip, number_record, number_comments, contain, id_cookie
):
    """
    Возвращает список коментариев для users
    """
    string_item = ""
    if ip:
        string_item = string_item + " AND Ip='" + ip + "'"
    if id_cookie:
        string_item = string_item + " AND IdCookie='" + id_cookie + "'"
    if number_record:
        string_item = string_item + " AND IdArticle='" + number_record + "'"
    if number_comments:
        string_item = string_item + " AND Id='" + number_comments + "'"
    if contain:
        string_item = string_item + " AND Reply LIKE '%" + contain + "%'"
    if from_date and to_date:
        items = work(
            "SELECT * FROM Replys WHERE DateString>=? AND DateString<=?"
            + string_item
            + " ORDER BY DateString",
            (from_date, to_date),
        )

        return [
            Replys(
                Reply=i[0],
                DateString=i[1],
                IdArticle=i[2],
                Id=i[3],
                Ip=i[4],
                ListTo=i[5],
                IdCookie=i[6],
            )
            for i in items
        ]
    else:
        return []


def delete_comments_users(id_item):
    """
    Удаляет комментарии по ид комментария
    """
    return work("DELETE FROM Replys WHERE Id=?", (id_item,))


def block_ip(block_to, ip, block_text):
    """
    Добавляет ип в блок лист
    """
    if block_to and ip and block_text:
        work(
            "INSERT INTO BlockList VALUES (?, ?, ?, ?)",
            (ip, datetime.today().strftime("%Y-%m-%d %H:%M:%S"), block_to, block_text),
        )


def delete_ip_from_block(ip):
    """
    Удаляет ип из блок листа
    """
    if ip:
        work("DELETE FROM BlockList WHERE Ip=?", (ip,))


def get_ip_block_list():
    """
    Возвращает список всех заблокированных ип
    """
    items = work("SELECT * FROM BlockList")
    return [BlockList(Ip=i[0], DateFrom=i[1], DateTo=i[2], Reply=i[3]) for i in items]


def get_ip_block(ip):
    """
    Возвращает заблокированый ип
    """
    item = work("SELECT * FROM BlockList WHERE Ip=?", (ip,))
    if len(item) > 0:
        return item[0]


def get_visitors(from_date, to_date):
    """
    Возвращает список всех посетителей
    """
    items = work(
        "SELECT * FROM Users WHERE DateString>=? AND DateString<=?",
        (from_date, to_date),
    )
    return [list(i) for i in items]
