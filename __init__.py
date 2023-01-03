###################################################################
# Tips: Changes                                                   #
# 1.students.user -> students.users                               #
# 2.In line 50                                                    #
# 3.In line 45 in gl():if not int(i[0]) > 100 -> no 'int(' and ')'#
#     i[1] -> i[0]                                                #
# 4.In line 46~47 in gl()                                         #
# 5.In line 61 -> x[0](Please change)                             #
#                                                                 #
#                                                                 #
#                                                                 #
#                                                                 #
#                                                                 #
###################################################################
from flask import *
from itertools import *
import pymysql
import socket

app = Flask(__name__)
app.secret_key = "SleepyDinosaur2?!"
d = []
blogs_max = -100; notice_max = -100


class User:
    def __init__(self, username: str, user_id: int, password: str, logged_in: str, login_ip, little_bit: str, mod_user: str):
        self.username = username
        self.id = user_id
        self.password = password
        self.logged_in = True if logged_in == "yes" else False
        self.login_ip = login_ip
        self.little_bit = little_bit
        self.mod_user = True if mod_user == "1" else False


class Blog:
    def __init__(self, _username, _title, _message, _len):
        self.username = _username
        self.title = _title
        self.message = _message
        self.len = _len


def init_user():
    global d
    x = find_from_database("STUDENTS.USER")
    for i in range(0, len(x)):
        d.append(User(x[i][0], x[i][1], x[i][2], x[i][3], x[i][4], x[i][5], x[i][6]))
        # d.append(User(x[i][1], x[i][0], x[i][2], x[i][3], x[i][4], x[i][5], x[i][6]))


def init_blog():
    global blogs_max, flag;flag=0
    x = find_from_database("blogs.blog")
    for i in range(0, len(x)):
        if int(x[i][3]) > blogs_max:
            blogs_max = int(x[i][3]);flag=1
    if not flag:
        blogs_max = 0


def init_notice():
    global notice_max, flag;flag=0
    x = find_from_database("notices.notice")
    for i in range(0, len(x)):
        if int(x[i][0]) > notice_max:
            notice_max = int(x[i][0]);flag=1
    if not flag:
        notice_max = 0


def execute(executes):
    conn = pymysql.connect(host="127.0.0.1",
                           user='root',
                           passwd="root",
                           port=3306,
                           charset='utf8'
                           )
    cur = conn.cursor()
    cur.execute(executes)
    f = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return f


def find_from_database(database):
    conn = pymysql.connect(host="127.0.0.1",
                           user='root',
                           passwd="root",
                           port=3306,
                           charset='utf8'
                           )
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + database)
    f = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return f


lenss = len(execute("SELECT * FROM notices.notice"))


def got_lens(lens):
    i = 0
    lac = []
    xxx = 0
    if lenss < 5:
        xxx = lenss
    else:
        xxx = 5
    while i < xxx:
        lac.append([lens[i][0], lens[i][1], lens[i][2]])
        i += 1
    return lac


@app.route('/', methods=['GET', 'POST'])
def index():
    global logged_in
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    return render_template("index.html", a=" ", messages=got_lens(execute("SELECT * FROM notices.notice")), logged_in=logged_in)


@app.route('/blogs')
def blog():
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    return render_template("blog.html", a=" - 博客", blogs=find_from_database("blogs.blog"), logged_in=logged_in)


@app.route('/login', methods=['GET', 'POST'])
def login():
    flag = False
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        for i in d:
            if username == i.username:
                if pwd == i.password:
                    i.logged_in = True
                    execute("UPDATE STUDENTS.USER SET logged_in='yes' WHERE username='" + username + "'")
                    i.login_ip = request.remote_addr
                    execute("UPDATE STUDENTS.USER SET login_ip='" + request.remote_addr + "' WHERE username='" + username + "'")
                    init_user()
                    flag = True
                    flash("", "success")
                    return redirect(url_for('index'))
        if not flag:
            flash("出错了~", 'error')
        return redirect(url_for('login'))
    return render_template('login.html', a=" - 登录")


@app.route('/logout/<username>')
def logout(username):
    execute("UPDATE STUDENTS.USER SET logged_in='no',login_ip='0.0.0.0' WHERE username='" + username + "'")
    for i in d:
        if username == i.username:
            i.logged_in = False
            i.login_ip = '0.0.0.0'
    init_user()
    return redirect(url_for('login'))


@app.route("/blog/<username>/post/new/write", methods=['GET', 'POST'])
def write_blog(username):
    if request.method == 'POST':
        title = request.form["title"]
        content = request.form["input-blog_content_md"]
        execute("INSERT INTO BLOGS.BLOG (who_create_this, title, message, id) VALUES ('" + username + "', '" + title + "', '" + content + "', '" + str(blogs_max + 1) + "')")
        init_blog()
        return redirect(url_for("blog"))
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    return render_template('new_blog.html', a=' - 新博客', logged_in=logged_in, that=username)


@app.route("/how_to_use_the_blog")
def use():
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    return render_template('use.html', a=' - 如何使用博客', logged_in=logged_in)


@app.route("/blogs/<post>", methods=['GET', 'POST'])
def blogs(post):
    global logged_in, this, pinglun
    ip = request.remote_addr
    this = [None, None, None]
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    if int(post) > blogs_max:
        return redirect('index')
    xs = execute("SELECT * FROM blogs.blog")
    for i in xs:
        if int(i[3]) == int(post):
            this = i
    pinglun = None
    for i in execute("SELECT * FROM blog_pl.pinglun"):
        if int(i[2]) == int(post):
            pinglun = []
            break
    if pinglun == []:
        for i in execute("SELECT * FROM blog_pl.pinglun"):
            if int(i[2]) == int(post):
                pinglun.append(i)
    if request.method == "POST":
        msg = request.form['input']
        execute("INSERT INTO blog_pl.pinglun (whu, msg, what_blog) VALUES ('" + logged_in[1] + "', '" + msg + "', '" + post + "')")
        return redirect(url_for("blog"))
    return render_template('_blog.html', a=' - ' + str(this[0]) + '的博客', logged_in=logged_in, name=this[0], message=this[2],
                           title=this[1], pinglun=pinglun, post=post)


@app.route("/users/<name>")
def user(name):
    global logged_in, id_, jianjie, mod
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    user = False
    for i in d:
        if i.username == name:
            user = True
            id_ = i.id
            jianjie = i.little_bit
            if i.mod_user:
                mod = "管理员"
            else:
                mod = "普通用户"
            break
    return render_template('user.html', logged_in=logged_in, name=name, user=user, id=id_, jianjie=jianjie, mod=mod)


@app.route("/user/<name>/modify-profile", methods=['GET', 'POST'])
def modify_profile(name):
    global logged_in
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    if request.method == 'POST':
        msg = request.form['jianjie']
        execute("UPDATE STUDENTS.USER SET little_bit='" + msg + "' WHERE username='" + name + "'")
        init_user()
        for i in d:
            if i.username == name:
                i.little_bit = msg
        return redirect(url_for("index"))
    return render_template('modify.html', logged_in=logged_in, a='- 更改资料', name=name)


@app.route("/guanli_students", methods=['GET', 'POST'])
def gl():
    global logged_in
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    flag2 = 0
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['passwd']
        i_d_ = request.form['_id']
        for i in d:
            if i.username == name:
                i.password = password
                i.id = i_d_
                flag2 = 1
                execute("UPDATE STUDENTS.USER SET ID='" + i_d_ + "', PWD='" + password + "' WHERE USERNAME='" + name + "'")
                init_user()
                break
            if i.id == i_d_:
                i.password = password
                i.username = name
                flag2 = 1
                execute("UPDATE STUDENTS.USER SET USERNAME='" + name + "', PWD='" + password + "' WHERE ID='" + i_d_ + "'")
                init_user()
                break
        if flag2:
            flash("更改成功", "color: blue;")
            return redirect(url_for("gl"))
        else:
            execute("INSERT INTO STUDENTS.USER (id, username, pwd, logged_in, login_ip, little_bit, mod_user) VALUES ('" + i_d_ + "', '" + name + "', '" + password + "', 'no', '0.0.0.0', '无', '0')")
            init_user()
    users = []
    for i in execute("SELECT * FROM STUDENTS.USER"):
        if not int(i[1]) >= 100:
            users.append([i[0], i[1], i[2]])
            # users.append([i[1], i[0], i[2]])
    return render_template('gl.html', logged_in=logged_in, a='- 管理学生（管理员才能用的功能）', users=users)


@app.route('/notices')
def notices():
    global logged_in
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    notice = []
    for i in execute('SELECT * FROM notices.notice'):
        notice.append([i[0], i[2], i[1]])
    empty = 0
    if len(notice) < 1:
        empty = 1
    return render_template('notices.html', logged_in=logged_in, a='- 公告', notices=notice, empty=empty)


@app.route('/notice/<username>/write', methods=['GET', 'POST'])
def write_notice(username):
    global logged_in, lenss
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    if request.method == 'POST':
        title = request.form["title"]
        content = request.form["input-blog_content_md"]
        init_notice()
        execute(
            "INSERT INTO NOTICES.NOTICE (id, who, title, msg) VALUES ('" + str(notice_max+1) + "', '" + username + "', '" + title + "', '" + content + "')")
        init_notice()
        lenss += 1
        return redirect(url_for("index"))
    return render_template('new_notice.html', logged_in=logged_in, a='- 写公告', that=username)


@app.route('/notices/<post>')
def notice(post):
    global logged_in, this
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    if int(post) > notice_max:
        return redirect('index')
    xs = execute("SELECT * FROM notices.notice")
    for i in xs:
        if int(i[0]) == int(post):
            this = i
    return render_template('notice.html', logged_in=logged_in, a='- 公告', title=this[2], name=this[1], message=this[3])


@app.errorhandler(404)
def page_not_found(error):
    global logged_in
    ip = request.remote_addr
    flag = 0
    for i in d:
        if i.login_ip == ip:
            if i.logged_in == True:
                flag += 1
                logged_in = [True, i.username]
                if i.mod_user == True:
                    logged_in.append(True)
                else:
                    logged_in.append(False)
    if flag == 0:
        logged_in = [False, None, False]
    return render_template('404.html', logged_in=logged_in, a='- 404'), 404


if __name__ == '__main__':
    init_user()
    init_blog()
    init_notice()
    res = socket.gethostbyname(socket.gethostname())
    app.run(port=80, debug=True, host=res)
