import sqlite3

if __name__ == "__main__":

    con_sq3 = sqlite3.connect("seyryan_np.db")
    cur_sq3 = con_sq3.cursor()

    sql_select = "SELECT NUM_IID FROM ITEM"
    cur_sq3.execute(sql_select)
    item = cur_sq3.fetchall()

    con_ob = sqlite3.connect("seyryan.db")
    cur_ob = con_ob.cursor()

    for t in item:
        #print("SELECT POSITION FROM ITEM WHERE NUM_IID=%d"%t)
        cur_ob.execute("SELECT POSITION FROM ITEM WHERE NUM_IID=%d"%t)
        pos = cur_ob.fetchall()
        if pos:
            if pos[0][0] != "XXXX":
                print("UPDATE ITEM SET POSITION='%s' WHERE NUM_IID=%d"%(pos[0][0],t[0]))
                cur_sq3.execute("UPDATE ITEM SET POSITION='%s' WHERE NUM_IID=%d"%(pos[0][0],t[0]))

    con_sq3.commit()
    con_sq3.close()

    con_ob.close()
