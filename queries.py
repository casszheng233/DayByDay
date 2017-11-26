from flask import Flask,flash, redirect,  url_for, render_template
import sys
import MySQLdb
import dbconn2
import id
#process
def createCat(conn,name,color):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into category(name,color) values ({0},{1});'.format(name,color))

def displayCategory(conn,name):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from category where name = {0};'.format(name))
    row = curs.fetchone()
    if row != None:
        return row['name']
    else:
        return None

def createTask(conn,isFinished,userID,taskName,start,end):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into task(isFinished,userID,taskName,start,end) values ({0},{1},{2},{3},{4});'.format(isFinished,userID,taskName,start,end))



def addSubtask(conn,userID,parent,child):#this needs to be an id
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into taskList (userID,parentTaskID,subTaskID) values ({0},{1}，{2});'.format(userID,parent,child))

def displaySubtask(conn,parent):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from taskList where parentTaskID = {0};'.format(parent))
    rows = curs.fetchall()
    return rows
