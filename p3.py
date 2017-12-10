import dbconn2
import MySQLdb
import os
from flask import (Flask, render_template, url_for, request, flash)

# DSN  = { 'host': 'localhost',
#                    'user' :  'czheng',
#                    'passwd' :'MkC8oFMvMUTXc9O',
#                    'db': 'czheng_db'}
# DATABASE = 'czheng_db'

DSN  = { 'host': 'localhost',
                   'user' :  'rpyktel',
                   'passwd' :'G2O2HUprzpi6xUl',
                   'db': 'rpyktel_db'}
DATABASE = 'rpyktel_db'

def cursor(database=DATABASE):
    DSN['db'] = database
    conn = dbconn2.connect(DSN)
    return conn.cursor(MySQLdb.cursors.DictCursor)

def getCatColors(userID):
    userID = 1 # currently hardcoded
    curs = cursor(DATABASE)
    curs.execute('select name, color from category where userID = %s;',(userID,))
    colorsDict = curs.fetchall()
    d = {}
    for obj in colorsDict:
        d[str(obj['name'])] = str(obj['color'])
    return d


def rightPanelTask(userID):
    getColors = getCatColors(1)
    userID = 1 # hardcoded right now
    curs = cursor(DATABASE)
    curs.execute('select distinct parentTaskID, subTaskID from taskList where userId = %s;',(userID,))
    buildAssociation = curs.fetchall()
    finalData = []
    taskDic = {}
    for object in buildAssociation:
        parentTask = str(object['parentTaskID'])
        print parentTask
        subTask = str(object['subTaskID'])
        if (parentTask in taskDic):
            taskDic[parentTask].append(subTask)
        else:
            taskDic[parentTask] = [subTask]
    for obj in taskDic.keys():
        taskHolder = []
        curs1 = cursor(DATABASE)
        curs1.execute('select isFinished, taskName, taskID, start, end, name from task where taskID = %s',(obj,))
        parent = curs1.fetchall()

        parentDic = {'name': str(parent[0]['taskName']),
                    'isFinished': parent[0]['isFinished'],
                    'taskID': str(parent[0]['taskID']),
                    'start': parent[0]['start'],
                    'end': parent[0]['end'],
                    'catColor': getColors[str(parent[0]['name'])],
                    'cat': str(parent[0]['name'])}

        subDics = []
        for subID in taskDic[obj]:
            curs2 = cursor(DATABASE)
            curs2.execute('select taskName, isFinished, taskID, end, name from task where taskID = %s;',(subID,))
            subTask = curs2.fetchall()

            if (curs2.rowcount == 0):
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
    clean1 = str(finalData).replace('datetime.date(','[')
    clean2 = str(clean1).replace(')',']')
    clean3 = str(clean2).replace('None','0')
    return clean3


def buildDropdown(timeSelection,dataSelection):
    data = [['value="day"','Day View'],['value="week"','Week View'],['value="month"','Month View']]
    return data


def getCats(userID):#check this part, need to check for none value
    curs = cursor(DATABASE)
    curs.execute('select * from category where userID = %s;',(userID,))
    allCats = curs.fetchall()
    if allCats!=None:

        return allCats
    else:
        return []

def addCat(name,color,userID):
    curs = cursor(DATABASE)
    try:
        curs.execute('insert into category(name, color,userID) values (%s,%s,%s);',(name, color,userID,))
        print "successful insert"
        flash("Inserted " + name + " successfully!")
    except:
        print "todo"
        print "did not work"


def addTask(isFinished,userID,taskName,start,end,cat):
    curs = cursor(DATABASE)
    try:
        curs.execute('select * from task where taskName = %s and start = %s and end = %s and userID = %s;',(taskName,start,end,userID,))
        row = curs.fetchone()
        if row == None:
            curs.execute('insert into task(isFinished,userID,taskName,start,end,name) values (%s,%s,%s,%s,%s,%s);',(isFinished,userID,taskName,start,end,cat,))
            print 'successfullt insert'
            flash ("Inserted "+taskName +" successfully!")
        else:
            flash ("task existed in the database")
    except:
        flash("check your input!")

def deleteSubtask(taskID):
    curs = cursor(DATABASE)
    curs.execute('select * from taskList where parentTaskID = %s;',(taskID,))
    rows = curs.fetchall()
    print rows
    print len(rows)
    if len(rows)!=0:
        for row in rows:
            subTaskID = row['subTaskID']
            print subTaskID
            deleteSubtask(subTaskID)
            curs.execute('delete from taskList where parentTaskID = %s and subTaskID = %s;',(taskID,subTaskID,))
        curs.execute('delete from task where taskID = %s;',(taskID,))
    else:
        curs.execute('delete from taskList where subTaskID = %s;',(taskID,))
        curs.execute('delete from task where taskID  = %s;',(taskID,))


def deleteTask(userID,taskName,start,end,cat):
    curs = cursor(DATABASE)
    taskID = checkTaskID(taskName,start,end)
    if taskID is not None:
        deleteSubtask(taskID['taskID'])
        flash('deleted')
    else:
        flash('Such task does not exist')

def checkTaskID(taskName,start,end):
    curs = cursor(DATABASE)
    try:
        #curs.execute('insert into task(isFinished,userID,taskName,start,end) values ("{0}","{1}","{2}","{3}","{4}");'.format(isFinished,userID,taskName,start,end))
        curs.execute('select * from task where taskName = %s and start = %s and end = %s;',(taskName,start,end,))
        row = curs.fetchone()
        return row
    except:
        flash('please check your input')
        print "to do: not working"

def tickBox(taskID):
    curs = cursor(DATABASE)
    curs.execute('select isFinished from task where taskID =' + taskID[4:])
    row = curs.fetchone()
    isFin = 1
    if (row['isFinished']):
        isFin = 0

    curs2 = cursor(DATABASE)
    print 'update task set isFinished=' + str(isFin) + ' where taskID = ' + taskID[4:] + ';'
    curs.execute('update task set isFinished=' + str(isFin) + ' where taskID = ' + taskID[4:] + ';')


def addSubtask(userID,parent,child):#this needs to be an id
    curs = cursor(DATABASE)
    curs.execute('insert into taskList (userID,parentTaskID,subTaskID) values (%s,%s,%s);',(userID,parent,child,))

def addSubtaskNull(userID,parent):#this needs to be an id
    curs = cursor(DATABASE)
    curs.execute('insert into taskList (userID,parentTaskID,subTaskID) values (%s,%s,NULL);',(userID,parent,))

def addLog(cat,hours,userID,taskDate):
    curs = cursor(DATABASE)
    curs.execute('select * from category where name = %s;',(cat,))
    row = curs.fetchone()
    if row != None:
        curs.execute('select * from logEntry where name = %s and taskDate = %s and userID = %s;',(cat,taskDate,userID,))
        row = curs.fetchone()
        if row == None:
            curs.execute('insert into logEntry values (%s,%s,%s,%s);',(cat,hours,userID,taskDate,))
            flash('log has been entered')
        else:
            #existingHour = row['hours']
            curs.execute('update logEntry set hours = hours + %s where name = %s and taskDate = %s and userID = %s;',(hours,cat,taskDate,userID,))
            flash('log has been updated ')
    else:
        flash('please input an existing category')

def checkLog(logType,userID):
    curs = cursor(DATABASE)
    if logType == 'day':
        curs.execute('select taskDate,sum(hours) as accum from logEntry where userID = %s group by taskDate;',(userID,))
    #if logType == 'day':#per week
    #    curs.execute('select taskDate, sum(hours) as accum from logEntry where taskDate between date_sub(now(),INTERVAL 1 WEEK) and now() group by taskDate;')
    if logType == 'week':
        curs.execute('select taskDate, sum(hours) as accum from logEntry where userID = %s group by YEARWEEK(taskDate);',(userID,))
    if logType == 'month':
        curs.execute('select taskDate, sum(hours) as accum from logEntry where userID = %s group by YEAR(taskDate), MONTH(taskDate);',(userID,))
    rows = curs.fetchall()
    if rows!=None:
        return rows
    else:
        flash('no log record')
        return [{'taskDate':'','accum':''}]

def addEvent(userID,eventName,eventDate,start,end):

    curs = cursor(DATABASE)
    curs.execute('select * from event where eventDate = %s and (%s between start and end or %s between start and end);',(eventDate,start,end,))
    row = curs.fetchone()
    if row == None:
        curs.execute('insert into event (userID,eventDate,start,end,name) values (%s,%s,%s,%s,%s);',(userID,eventDate,start,end,eventName,))
        print 'successfullt insert'
        flash ("Inserted "+eventName +" successfully!")
    else:
        flash('there seems to be a scheduling conflict')
    # try:
    #     #check if there exists any preexisting event
    #     curs.execute('select * from event where eventDate = %s where %s bewteen start and end or %s bewteen start and end;',(eventDate,start,end,))
    #     row = curs.fetchone()
    #     if row == None:
    #         curs.execute('insert into event (userID,eventDate,start,end,name) values (%s,%s,%s,%s);',(userID,eventDate,start,end,eventName,))
    #         print 'successfullt insert'
    #         flash ("Inserted "+eventName +" successfully!")
    #     else:
    #         flash ("task existed in the database")
    # except:
    #     flash("check your input!")
