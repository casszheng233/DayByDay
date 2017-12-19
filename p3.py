# CS304 Final Project
# Beta Version
# p3.py
# Rosie Pyktel and Cassandra Zheng

import dbconn2
import MySQLdb
import os
from flask import (Flask, render_template, url_for, request, flash)
from DSN import *
# import id

#a helper function to get connection
def getConnection():
    dsn = rpyktel_dsn
    conn = dbconn2.connect(dsn)
    return conn

#a helper function to check if the username and password match with the database record
#used in login
def checkUser(conn,username,passwd):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    # print 'connected'
    curs.execute('select * from user where username = %s and psswd = %s;',(username,passwd,))
    row = curs.fetchone()
    return row

#a helper function to check if a username has already been used in DATABASE
#used in registering new users
def checkUsername(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    print 'connected'
    curs.execute('select * from user where username = %s;',(username,))#check if the username is in the database already
    row = curs.fetchone()
    if row == None:
        return True
    else:
        return False
#a helper function to create a new user
#used in user registration
def createUser(conn,username,passwd):
    curs  = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into user (username,psswd) values (%s,%s);',(username,passwd,))

#a helper function to get the corresponding color of the indicated category stoerd by the user
def getCatColors(conn,userID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select name, color from category where userID = %s;',(userID,))
    colorsDict = curs.fetchall()
    d = {}
    for obj in colorsDict:
        d[str(obj['name'])] = str(obj['color'])
    # print d
    return d

# create data structure containing information on all of the user's tasks
def rightPanelTask(conn,userID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    getColors = getCatColors(conn,userID)
    curs.execute('select distinct parentTaskID, subTaskID from taskList where userId = %s;',(userID,))
    buildAssociation = curs.fetchall()
    finalData = []
    taskDic = {}
    for object in buildAssociation:
        parentTask = str(object['parentTaskID'])
        subTask = str(object['subTaskID'])
        if (parentTask in taskDic):
            taskDic[parentTask].append(subTask)
        else:
            taskDic[parentTask] = [subTask]
    for obj in taskDic.keys():
        taskHolder = []
        #check for parent task
        curs.execute('select isFinished, taskName, taskID, start, end, name from task where taskID = %s',(obj,))
        parent = curs.fetchall()

        parentDic = {'name': str(parent[0]['taskName']),
                    'isFinished': parent[0]['isFinished'],
                    'taskID': str(parent[0]['taskID']),
                    'start': parent[0]['start'],
                    'end': parent[0]['end'],
                    'catColor': getColors[str(parent[0]['name'])],
                    'cat': str(parent[0]['name'])}

        subDics = []
        #check for subtasks
        for subID in taskDic[obj]:
            curs.execute('select taskName, isFinished, taskID, end, name from task where taskID = %s;',(subID,))
            subTask = curs.fetchall()

            if (curs.rowcount == 0):
                subDic = {}
            else:
                subDic = {'name': str(subTask[0]['taskName']),
                          'isFinished': subTask[0]['isFinished'],
                          'taskID': str(subTask[0]['taskID']),
                          'end': subTask[0]['end'],
                          'catColor': getColors[str(parent[0]['name'])],
                          'cat': str(parent[0]['name'])}


            subDics.append(subDic)
        taskHolder = [parentDic,subDics]
        finalData.append(taskHolder)
    #convert to a javascript-friendly format
    clean1 = str(finalData).replace('datetime.date(','[')
    clean2 = str(clean1).replace(')',']')
    clean3 = str(clean2).replace('None','0')
    return clean3

#a helper to build dropdown in base.html
def buildDropdown(timeSelection,dataSelection):
    data = [['value="day"','Day View'],['value="week"','Week View'],['value="month"','Month View']]
    return data

#check for all categories stored by a user
def getCats(conn,userID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from category where userID = %s;',(userID,))
    allCats = curs.fetchall()
    if allCats!=None:
        return allCats
    else:
        return []

#a helper to insert category into database
def addCat(conn,name,color,userID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('insert into category(name, color,userID) values (%s,%s,%s);',(name, color,userID,))
        print "successful insert"
    except:
        return "error"

#insert tasks
def addTask(conn,isFinished,userID,taskName,start,end,cat):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('select * from task where taskName = %s and start = %s and end = %s and userID = %s;',(taskName,start,end,userID,))
        row = curs.fetchone()
        if row == None:
            curs.execute('insert into task(isFinished,userID,taskName,start,end,name) values (%s,%s,%s,%s,%s,%s);',(isFinished,userID,taskName,start,end,cat,))
            print 'successfullt insert'
            flash ("Inserted "+taskName +" successfully!")
        else:
            flash ("task existed in the database")
            return {"error":"Duplicate task!"}
    except:
        flash("check your input!")
        print "empty inputs"

#recursively delete tasks, not used but should work
def deleteSubtask(conn,taskID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from taskList where parentTaskID = %s;',(taskID,))
    rows = curs.fetchall()
    if len(rows)!=0:
        for row in rows:
            subTaskID = row['subTaskID']
            deleteSubtask(subTaskID)
            curs.execute('delete from taskList where parentTaskID = %s and subTaskID = %s;',(taskID,subTaskID,))
        curs.execute('delete from task where taskID = %s;',(taskID,))
    else:
        curs.execute('delete from taskList where subTaskID = %s;',(taskID,))
        curs.execute('delete from task where taskID  = %s;',(taskID,))

#delete tasks
def deleteTask(conn,userID,taskName,start,end,cat):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    taskID = checkTaskID(taskName,start,end)
    if taskID is not None:
        deleteSubtask(taskID['taskID'])
        flash('deleted')
    else:
        flash('Such task does not exist')

#a helper function to report the system assigned taskID given necessary information
def checkTaskID(conn,taskName,start,end):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('select * from task where taskName = %s and start = %s and end = %s;',(taskName,start,end,))
        row = curs.fetchone()
        return row
    except:
        flash('please check your input')
        print "to do: not working"

#update isFinished status in task
def tickBox(conn,taskID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select isFinished from task where taskID =' + taskID[4:])
    row = curs.fetchone()
    isFin = 1
    if (row['isFinished']):
        isFin = 0

    #curs2 = conn.cursor(MySQLdb.cursors.DictCursor)
    print 'update task set isFinished=' + str(isFin) + ' where taskID = ' + taskID[4:] + ';'
    curs.execute('update task set isFinished=' + str(isFin) + ' where taskID = ' + taskID[4:] + ';')

#a helper to add subtask
def addSubtask(conn,userID,parent,child):#this needs to be an id
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into taskList (userID,parentTaskID,subTaskID) values (%s,%s,%s);',(userID,parent,child,))

#handles special case when a task doesn't have any subtasks
def addSubtaskNull(conn,userID,parent):#this needs to be an id
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into taskList (userID,parentTaskID,subTaskID) values (%s,%s,NULL);',(userID,parent,))

#a helper to check all categories/colors from a user's database
def checkCatColor(conn,userID):#check all colors
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from category where userID = %s;',(userID,))
    rows = curs.fetchall()
    return rows

#helper: adding log
def addLog(conn,cat,hours,userID,taskDate):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from category where name = %s;',(cat,))#check if category exists
    row = curs.fetchone()
    if row != None:
        curs.execute('select * from logEntry where name = %s and taskDate = %s and userID = %s;',(cat,taskDate,userID,))
        row = curs.fetchone()
        if row == None:#new log, needs to add in database
            curs.execute('insert into logEntry values (%s,%s,%s,%s);',(cat,hours,userID,taskDate,))
        else:#existing log, needs to update in table
            curs.execute('update logEntry set hours = hours + %s where name = %s and taskDate = %s and userID = %s;',(hours,cat,taskDate,userID,))
            flash('log has been updated ')
    else:#cannot find category
        flash('please input an existing category')

#a helper to query database on information based one specific category
def checkLog(conn,logType,userID,cat):#given logType and category, returns [[yyyy,mm,dd,hours]]
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    if cat == 'all':
        if logType == 'day':
            #sum of hours of all categories per day
            curs.execute('select taskDate,sum(hours) as hours from logEntry where userID = %s group by taskDate;',(userID,))
        if logType == 'week':
            #sum of hours of all categories per week
            curs.execute('select taskDate, sum(hours) as hours from logEntry where userID = %s group by YEARWEEK(taskDate);',(userID,))
        if logType == 'month':
            #sum of hours of all categories per month
            curs.execute('select taskDate, sum(hours) as hours from logEntry where userID = %s group by YEAR(taskDate), MONTH(taskDate);',(userID,))
    else:
        if logType == 'day':
            #entered hours of a specifc category per day
            curs.execute('select taskDate,hours from logEntry where userID = %s and name = %s group by taskDate;',(userID,cat,))
        if logType == 'week':
            #entered hours of a specifc category per week
            curs.execute('select taskDate, hours from logEntry where userID = %s and name = %s group by YEARWEEK(taskDate);',(userID,cat,))
        if logType == 'month':
            #entered hours of a specifc category per month
            curs.execute('select taskDate, hours from logEntry where userID = %s and name = %s group by YEAR(taskDate), MONTH(taskDate);',(userID,cat,))
    rows = curs.fetchall()
    result = []
    #result: [[yyyy,mm,dd,hours]]
    if rows!=None:
        for eachrow in rows:
            recDate = eachrow['taskDate']
            if recDate!=None:
                cleanRec = [recDate.year,recDate.month,recDate.day]
                cleanRec.append(int(eachrow['hours']))
                result.append(cleanRec)
    return result

#a helper (for ajax) returns a list of four dictionaries of:
#logDictDay: log record of all categories on a daily basis {cat:hours}
#logDictWeek: log record of all catergories on a weekily basis {cat:hours}
#logDictMonth: log record of all categories on a monthly basis {cat:hours}
#colorDict:a record of all categories and their corresponding colors {cat:color}
def allLog(conn,userID,allCats):
    logDictDay = {}
    logDictDay['all'] = checkLog(conn,'day',userID,'all')#sum of log hours, same as below
    for eachCat in allCats:
        cat = eachCat['name']
        catInfo = checkLog(conn,'day',userID,cat)#log hours of a specific cat, same as below
        logDictDay[str(cat)] = checkLog(conn,'day',userID,cat)

    logDictWeek = {}
    logDictWeek['all'] = checkLog(conn,'week',userID,'all')
    for eachCat in allCats:
        cat = eachCat['name']
        catInfo = checkLog(conn,'week',userID,cat)
        logDictWeek[str(cat)] = checkLog(conn,'week',userID,cat)

    logDictMonth = {}
    logDictMonth['all'] = checkLog(conn,'month',userID,'all')
    for eachCat in allCats:
        cat = eachCat['name']
        catInfo = checkLog(conn,'month',userID,cat)
        logDictMonth[str(cat)] = checkLog(conn,'month',userID,cat)

    colorRows = checkCatColor(conn,userID)
    colorDict = {}
    colorDict['all']='000000'#all (sum of every categories): black
    if colorRows != None:
        for eachRow in colorRows:
            colorDict[str(eachRow['name'])]=str(eachRow['color'])
    return [logDictDay,logDictWeek,logDictMonth,colorDict]

#adding new event for a user given eventName, eventDate, start and end
def addEvent(conn,userID,eventName,eventDate,start,end):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    #checking if there exists any potential conflict
    curs.execute('select * from event where eventDate = %s and (%s between start and end or %s between start and end);',(eventDate,start,end,))
    row = curs.fetchone()
    if row == None:#if no conflict, then insert the new event
        curs.execute('insert into event (userID,eventDate,start,end,name) values (%s,%s,%s,%s,%s);',(userID,eventDate,start,end,eventName,))
        print 'successfullt insert'
        flash ("Inserted "+eventName +" successfully!")
    else:#flash error message if conflict happens
        print "conflict!"
        flash('there seems to be a scheduling conflict')
        return "error"



def rightPanelEvent(conn,   userID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from event where userId = %s;',(userID,))
    buildAssociation = curs.fetchall()
    finalData = []
    eventDic = {}
    for object in buildAssociation:
        eventID = str(object['eventID'])
        eventName = str(object['name'])
        eventDate = object['eventDate']
        startTime = str(object['start'])
        endTime = str(object['end'])

        eventDic = {'eventName': eventName,
                    'eventID':eventID,
                    'eventDate': eventDate,
                    'startTime': startTime,
                    'endTime': endTime}
        finalData.append(eventDic)

    clean1 = str(finalData).replace('datetime.date(','[')
    clean2 = str(clean1).replace(')',']')
    clean3 = str(clean2).replace('None','0')
    clean4 = str(clean3).replace('datetime.timedelta(','[')
    return clean4
