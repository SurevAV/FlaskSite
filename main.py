from flask import Flask
from flask import render_template, redirect, url_for, make_response, send_file
from flask import request as r
import os
from os import environ
import module_sql_str as modul_sql
import module_work as work

app = Flask(__name__)


# modul_sql.make_file()


@app.route("/", methods=["Get", "POST"])
@work.make_user_cookie
@work.check_ip
@work.check_request
def main():

    list_pages = [0, 1, 2, 3, 4]
    page = 0

    if r.args.get("page"):
        page = int(r.args.get("page"))
        if page > 2:
            list_pages = [page - 2, page - 1, page, page + 1, page + 2]

    return render_template(
        "main.html",
        list_Articles=modul_sql.list_titles_for_page(page, 10),
        view_page=page,
        for_link="/view?page=" + str(page) + "&id=",
        list_pages=list_pages,
        for_link_page="/?page=",
    )


@app.route("/view", methods=["Get", "POST"])
@work.make_user_cookie
@work.check_ip
@work.check_request
def view():

    if r.method == "POST" and r.form["click"] == "Добавить комментарий":

        modul_sql.make_comments(
            r.form["reply"],
            r.args.get("id"),
            work.user_ip(r),
            r.form["list_to"].replace(" ", ""),
            str(r.cookies.get("user")),
        )

    return render_template(
        "view.html",
        Article=modul_sql.search_article_by_id(r.args.get("id")),
        list_Comments=work.order(modul_sql.search_comments(r.args.get("id"))),
        link_return="/?page=" + r.args.get("page"),
    )


@app.route("/editor", methods=["Get", "POST"])
@work.check_key
@work.check_ip
@work.check_request
def editor():
    title, article, image = modul_sql.return_preview()
    if r.method == "POST":
        item = r.form["click"]

        # if item == 'Очистить SQL':
        #    modul_sql.make_file()

        if item == "Добавить запись":
            modul_sql.make_article(r.form["title"], r.form["article"], r.form["image"])

        elif item == "Найти запись":
            title, article, image = modul_sql.search_article(r.form["title"])

        elif item == "Обновить запись":
            modul_sql.change_article(
                r.form["title"], r.form["article"], r.form["image"]
            )
            modul_sql.change_preview(
                r.form["title"], r.form["article"], r.form["image"]
            )

        elif item == "Удалить запись":
            modul_sql.delete_comments(modul_sql.id_article(r.form["title"]))
            modul_sql.delete_article(r.form["title"])

        elif item == "Список всех записей":
            article, title = modul_sql.article_titles()

        elif item == "Предпросмотр":
            modul_sql.change_preview(
                r.form["title"], r.form["article"], r.form["image"]
            )

            return render_template(
                "preview.html",
                items=[r.form["title"], r.form["article"]],
                link_return="/editor",
            )

    return render_template("editor.html", title=title, article=article, image=image)


@app.route("/users", methods=["Get", "POST"])
@work.check_key
@work.check_ip
@work.check_request
def users():

    list_users = []
    list_block_ip = []
    block_menu = "none"
    if r.method == "GET":

        item = r.args.get("click")
        if item == "Найти комментарии":

            list_users = modul_sql.list_users(
                r.args.get("from"),
                r.args.get("to"),
                r.args.get("ip"),
                r.args.get("number_record"),
                r.args.get("number_comments"),
                r.args.get("contain"),
                r.args.get("id_cookie"),
            )

        elif item == "Удалить комментарии":
            if r.args.get("list_to"):
                for i in r.args.get("list_to").split(","):
                    modul_sql.delete_comments_users(i)

        elif item == "Заблокировать":
            modul_sql.block_ip(
                r.args.get("block_to"), r.args.get("block_ip"), r.args.get("block_text")
            )

        elif item == "Разблокировать":
            modul_sql.delete_ip_from_block(r.args.get("block_ip"))
        elif item == "Список":
            list_block_ip = modul_sql.get_ip_block_list()
            block_menu = "block"

    return render_template(
        "users.html",
        list_Comments=work.order(list_users),
        list_block_ip=list_block_ip,
        block_menu=block_menu,
    )


@app.route("/key", methods=["Get", "POST"])
@work.check_ip
@work.check_request
def key():

    item = 0
    if r.cookies.get("key") == work.key_item:
        item = 1

    if r.method == "POST" and r.form["click"] == "Отправить пароль":
        if r.form["key"] == work.key_item:
            item = 1
        else:
            item = 0
        res = make_response(render_template("key.html", item=item))
        res.set_cookie("key", r.form["key"])
        return res

    return render_template("key.html", item=item)


@app.route("/upload", methods=["Get", "POST"])
@work.check_key
@work.check_ip
@work.check_request
def upload_file():

    uploading = "Файл не выбран"
    try:
        if r.method == "POST":
            os.chdir(os.path.join(os.path.dirname(__file__), "static/images"))
            r.files["file"].save(r.files["file"].filename)
            uploading = "Файл загружен"
    except:
        uploading = "Не получилось загрузить файл"
    return render_template("upload.html", uploading=uploading)


@app.route("/visitors", methods=["Get", "POST"])
@work.check_key
@work.check_ip
@work.check_request
def visitors():

    list_users = modul_sql.get_visitors(r.args.get("from"), r.args.get("to"))

    if len(list_users) > 0:
        csv = open("visitors.csv", "w")
        for item in list_users:
            csv.write(";".join([str(x) for x in item]) + "\n")
        csv.close()
        return send_file("sql/visitors.csv", as_attachment=True)

    return render_template("visitors.html")


if __name__ == "__main__":
    app.run(threaded=True)
