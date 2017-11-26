from flask import Flask,flash, redirect,  url_for, render_template
import sys
import MySQLdb
import dbconn2
import id
#process
def createCat(conn,name,color):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into category(name,color) values (%s,%s)',(name,color))

def displayCategory(conn,name):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from category where name = name',(name,))
    row = curs.fetchone()
    if row != None:
        return row['name']
    else:
        return None

def createTask(conn,isFinished,userID,taskName,start,end):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into task(isFinished,userID,taskName,start,end) values (%s,%s,%s,%s,%s)',(isFinished,userID,taskName,start,end,))


def addSubtask(conn,userID,parent,child):#this needs to be an id
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into taskList (userID,parentTaskID,subTaskID) values (%s,%s,%s)',(userID,parent,child))

    







curs.execute('insert into taskList(isFinished,userID,parentTaskID,subTaskID,start,end)
values (%s,%s,%s)',(isFinished,userID,parentTaskID,subTaskID,start,end,))
