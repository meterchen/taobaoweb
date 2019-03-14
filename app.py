#!/usr/bin/python3  
# -*- coding: utf-8 -*-  

from flask import Flask,request,redirect,url_for,session

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

    #sql_select = "select NUM_IID from ITEM where OUTER_ID='ZM6466'"
    sql_select = "select NUM_IID,OUTER_ID,CLIENT_NAVIGATION_TYPE,STOCK_STATUS, STORE_NAME, POSITION from ITEM where OUTER_ID LIKE "
    sql_select += "'%"+index+"'"

    # 显示全部内容
    cur.execute(sql_select)
    num_iid = cur.fetchall()
    cur.close()

    #print(num_iid)

    return num_iid
            
def save_pos(database, position, num_iid):
    con = sqlite3.connect(database)
    cur = con.cursor()
    
    sql_update = "UPDATE ITEM SET POSITION='%s' where NUM_IID = %s" %(position,num_iid)
    print(sql_update)
    cur.execute(sql_update)

    con.commit()

    con.close()

@app.route("/",methods=['post','get'])
def index():
    #user_agent = request.headers.get("User_Agent")
    item = ''
    if request.method == 'POST': # 注意POST为大写
        outer_id = request.form.get('outer_id')
        #print(username)
        if outer_id:
            #企业店
            item = query_db("/home/pi/Documents/flaskDemo/database/seyryan.db", outer_id)
            #num_iid += query_db("/home/pi/Documents/flaskDemo/database/APPITEM.DAT.TT", username, store="彤彤店")
            #num_iid += query_db("/home/pi/Documents/flaskDemo/database/APPITEM.DAT.NT", username, store="女童店")
            #num_iid += query_db("/home/pi/Documents/flaskDemo/database/APPITEM.DAT.HD", username, store="憨豆店")
            session['name'] = outer_id
            #return redirect(url_for('index'))

        position = request.form.get('position')
        num_iid = request.form.get("num_iid")
        print(position)
        print(num_iid)
        if position:
            save_pos("/home/pi/Documents/flaskDemo/database/seyryan.db", position, num_iid)
            item = query_db("/home/pi/Documents/flaskDemo/database/seyryan.db", session.get("name"))
            return render_template('index.html',u=item)



    return render_template('index.html',u=item)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
