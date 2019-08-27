#!/usr/bin/python3  
# -*- coding: utf-8 -*-  

from flask import Flask, request, redirect, url_for, session, flash

from flask import render_template
from flask_bootstrap import Bootstrap

import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
bootstrap = Bootstrap(app)


@app.route("/login")
def hello_world():
    return render_template("login.html")


def query_db(database, index):
    con = sqlite3.connect(database)
    cur = con.cursor()

    # sql_select = "select NUM_IID from ITEM where OUTER_ID='ZM6466'"
    sql_select = "select NUM_IID,OUTER_ID,CLIENT_NAVIGATION_TYPE,STOCK_STATUS, STORE_NAME, POSITION,PIC_URL from ITEM where OUTER_ID LIKE "
    sql_select += "'%" + index +"%"+ "'"

    # 显示全部内容
    cur.execute(sql_select)
    num_iid = cur.fetchall()
    cur.close()

    # print(num_iid)

    return num_iid


def save_pos(database, position, num_iid):
    con = sqlite3.connect(database)
    cur = con.cursor()

    sql_update = "UPDATE ITEM SET POSITION='%s' where NUM_IID = %s" % (position, num_iid)
    print(sql_update)
    cur.execute(sql_update)

    con.commit()

    con.close()

#@app.route("/", methods=['post'])
#def save_pos():


@app.route("/", methods=['post', 'get'])
def index():
    # user_agent = request.headers.get("User_Agent")
    item = ''

    # 几个提交按钮共用一个POST处理方法
    if request.method == 'POST':  # 注意POST为大写
        if "submit_outer_id" in request.form:
            outer_id = request.form.get('outer_id')
            # print(username)
            if outer_id:
                item = query_db("./database/seyryan.db", outer_id)
                # num_iid += query_db("/home/pi/Documents/flaskDemo/database/APPITEM.DAT.TT", username, store="彤彤店")
                # num_iid += query_db("/home/pi/Documents/flaskDemo/database/APPITEM.DAT.NT", username, store="女童店")
                # num_iid += query_db("/home/pi/Documents/flaskDemo/database/APPITEM.DAT.HD", username, store="憨豆店")
                if item:
                    session['outer_id'] = outer_id
                    session['num_iid'] = item
                else:
                    flash("商品不存在！")
                # return redirect(url_for('index'))
                render_template('index.html', u=item)

        if "submit_save" in request.form:
            position = request.form.get('position')
            # num_iid = request.form.get("num_iid")   # 隐藏的表单
            num_iid = session.get("num_iid")
            print(position)
            print(num_iid)
            if position:
                for t in num_iid:
                    save_pos("./database/seyryan.db", position, t[0])
                item = query_db("./database/seyryan.db", session.get("outer_id"))
                flash("货位号保存成功!")
                return render_template('index.html', u=item)

    return render_template('index.html', u=item)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
