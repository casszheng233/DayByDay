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
    curs.execute('select * from p_category;')
    allCats = curs.fetchall()
    return allCats

def addCat(name,color):
    curs = cursor(DATABASE)
    try:
        curs.execute('insert into p_category(name, color) values ("{0}","{1}");'.format(name, color))
        print "successful insert"
        flash("Inserted " + name + " successfully!")
    except:
        print "todo"
        print "did not work"
