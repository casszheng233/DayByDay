import dbconn2
import MySQLdb
import os
from flask import (Flask, render_template, url_for, request, flash)

DSN  = { 'host': 'localhost',
                   'user' :  'rpyktel',
                   'passwd' :'G2O2HUprzpi6xUl',
                   'db': 'rpyktel_db'}


DATABASE = 'rpyktel_db'

def cursor(database=DATABASE):
    DSN['db'] = database
    conn = dbconn2.connect(DSN)
    return conn.cursor(MySQLdb.cursors.DictCursor)

def getCats():
    curs = cursor(DATABASE)
    curs.execute('select * from category;')
    allCats = curs.fetchall()
    return allCats

def addCat(name,color):
    curs = cursor(DATABASE)
    try:
        curs.execute('insert into category(name, color) values ("{0}","{1}");'.format(name, color))
        print "successful insert"
        flash("Inserted " + name + " successfully!")
    except:
        print "todo"
        print "did not work"


def addTask(isFinished,userID,taskName,start,end):
    curs = cursor(DATABASE)
    try:
        curs.execute('select * from task where taskName = "{0}" and start = "{1}" and end = "{2}";'.format(taskName,start,end))
        row = curs.fetchone()
        if row == None:
            curs.execute('insert into task(isFinished,userID,taskName,start,end) values ("{0}","{1}","{2}","{3}","{4}");'.format(isFinished,userID,taskName,start,end))
            print 'successfullt insert'
            flash ("Inserted "+taskName +" successfully!")
        else:
            flash ("task existed in the database")
    except:
        print "to do: not working"
def checkTaskID(taskName,start,end):
    curs = cursor(DATABASE)
    try:
        #curs.execute('insert into task(isFinished,userID,taskName,start,end) values ("{0}","{1}","{2}","{3}","{4}");'.format(isFinished,userID,taskName,start,end))
        curs.execute('select * from task where taskName = "{0}" and start = "{1}" and end = "{2}";'.format(taskName,start,end))
        row = curs.fetchone()
        return row
    except:
        print "to do: not working"

def addSubtask(userID,parent,child):#this needs to be an id
    curs = cursor(DATABASE)
    curs.execute('insert into taskList (userID,parentTaskID,subTaskID) values ("{0}","{1}", "{2}");'.format(userID,parent,child))
