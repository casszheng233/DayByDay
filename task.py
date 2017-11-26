#!/usr/local/bin/python2.7

#CS304 Final Project Draft
#Rosie Pyktel and Cassandra Zheng

from flask import Flask, render_template, request, flash
import MySQLdb
import os
import id


app = Flask(__name__)
app.secret_key = 'this is the secret key'

dsn = id.czheng_dsn

conn = dbconn2.connect(dsn)


def checkTask(isFinished,start,end):#check if all inputs are valid
    res = True
    finMiss = (isFinished.strip()=='')
    startMiss = (start.strip()=='')
    endMiss = (end.strip()=='')
    if finMiss:#missing nm
        res = False
        flash("missing input: finished status is missing")#flash error msg
    if startMiss:
        res = False
        flash("missing input: start is missing")
    if endMiss:
        res = False
        flash("missing input: end is missing")
    return res

def checkEvent(name,start,end):#check if all inputs are valid
    res = True
    nameMiss = (name.strip()=='')
    startMiss = (start.strip()=='')
    endMiss = (end.strip()=='')
    if nameMiss:#missing nm
        res = False
        flash("missing input: name is missing")#flash error msg
    if startMiss:
        res = False
        flash("missing input: start is missing")
    if endMiss:
        res = False
        flash("missing input: end is missing")
    return res

def checkLog(isFinished,start,end):#check if all inputs are valid
    res = True
    finMiss = (nm.strip()=='')
    startMiss = (name.strip()=='')
    endMiss = (dob.strip()=='')
    if finMiss:#missing nm
        res = False
        flash("missing input: finished status is missing")#flash error msg
    if startMiss:
        res = False
        flash("missing input: start is missing")
    if endMiss:
        res = False
        flash("missing input: end is missing")
    return res


@app.route('/')
def landingPage():
    render_template('base.html')

@app.route('/createTask/',methods = ['POST','GET'])
def createTask():
    if request.method =='POST':
        try:
            isFinished = request.form['isFinished']
            #CHECK THIS PART
            #parent = request.form['parentTaskID']
            #child = request.form['childTaskID']
            start = request.form['start']
            end = request.form['end']
            if not checkTask(isFinished,start,end):
    	        return render_template('task.html')
            else:
                curs = conn.cursor(MySQLdb.cursors.DictCursor)
                #NEED TO CHANGE TO A INSERT STATEMENT
		        curs.execute('insert into taskList (isFinished,start,end) values (%s,%s,%s)',(isFinished,start,end,))#insert the message
                return render_template('task.html')

        except Exception as Error:#exception, go back to the original form
            print Error
            print 'error'
        return render_template('task.html')


    else:
        return render_template('task.html')#initial:go back to the original form


@app.route('/createEvent/',methods = ['POST','GET'])
def createEvent():
    if request.method =='POST':
        try:
            #isFinished = request.form['isFinished']
            name = request.form['name']
            start = request.form['start']
            end = request.form['end']
            if not check(isFinished,start,end):
    	        return render_template('event.html')
            else:
                curs = conn.cursor(MySQLdb.cursors.DictCursor)
                #NEED TO CHANGE TO A INSERT STATEMENT

		        curs.execute('insert into event (name,start,end) values (%s,%s,%s)',(name,start,end,))#insert the message
                return render_template('event.html')

        except Exception as Error:#exception, go back to the original form
            print Error
            print 'error'
        return render_template('event.html')


    else:
        return render_template('event.html')#initial:go back to the original form


@app.route('/createLog/',methods = ['POST','GET'])
def createLog():
    if request.method =='POST':
        try:
            #isFinished = request.form['isFinished']
            hour = request.form['hour']
            taskDate = request.form['taskDate']
            if not checkLog(isFinished,start,end):
    	        return render_template('event.html')
            else:
                curs = conn.cursor(MySQLdb.cursors.DictCursor)
                #NEED TO CHANGE TO A INSERT STATEMENT

		        curs.execute('insert into event (name,start,end) values (%s,%s,%s)',(name,start,end,))#insert the message
                return render_template('event.html')

        except Exception as Error:#exception, go back to the original form
            print Error
            print 'error'
        return render_template('event.html')


    else:
        return render_template('event.html')#initial:go back to the original form




if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
