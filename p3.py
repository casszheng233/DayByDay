import dbconn2
import MySQLdb
import os
from flask import (Flask, render_template, url_for, request, flash)

DSN  = { 'host': 'localhost',
                   'user' :  'czheng',
                   'passwd' :'MkC8oFMvMUTXc9O',
                   'db': 'czheng_db'}
DATABASE = 'czheng_db'

# DSN  = { 'host': 'localhost',
#                    'user' :  'rpyktel',
#                    'passwd' :'G2O2HUprzpi6xUl',
#                    'db': 'rpyktel_db'}
# DATABASE = 'rpyktel_db'

def cursor(database=DATABASE):
    DSN['db'] = database
    conn = dbconn2.connect(DSN)
    return conn.cursor(MySQLdb.cursors.DictCursor)

def rightPanelTask(userID):
    userID = 1 # hardcoded right now
    curs = cursor(DATABASE)
    curs.execute('select distinct parentTaskID, subTaskID from taskList where userId = {0};'.format(userID))
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
        curs1 = cursor(DATABASE)
        curs1.execute('select isFinished, taskName, taskID, start, end, name from task where taskID = {0}'.format(obj))
        parent = curs1.fetchall()
        parentDic = {'name': str(parent[0]['taskName']), 'isFinished': parent[0]['isFinished'], 'taskID': str(parent[0]['taskID']), "start": parent[0]['start'], "end": parent[0]['end'], "cat": str(parent[0]['name'])}
        subDics = []
        for subID in taskDic[obj]:
            curs2 = cursor(DATABASE)
            curs2.execute('select taskName, isFinished, taskID, end from task where taskID = {0};'.format(subID))
            subTask = curs2.fetchall()
            subDic = {'name': str(subTask[0]['taskName']), 'isFinished': subTask[0]['isFinished'], 'taskID': str(subTask[0]['taskID']), "end": subTask[0]['end']}
            subDics.append(subDic)
        taskHolder = [parentDic,subDics]
        finalData.append(taskHolder)
    clean1 = str(finalData).replace('datetime.date(','[')
    clean2 = str(clean1).replace(')',']')
    clean3 = str(clean2).replace('None','0')
    return clean3

    #form of final data: [   ({dictionary of parentTask}, [ {subTask}, {subTask}, ... ]  ) ,   ...     ]
    # [({'end': datetime.date(1111, 11, 12), 'name': u'psetCS', 'isFinished': 0, 'cat': u'cs', 'start': datetime.date(1111, 11, 11), 'taskID': '1'},
    #  [{'isFinished': 0, 'end': datetime.date(1111, 11, 12), 'name': u'a', 'taskID': '2'},
    #   {'isFinished': 0, 'end': datetime.date(1111, 11, 12), 'name': u'b', 'taskID': '3'},
    #   {'isFinished': 0, 'end': datetime.date(1111, 11, 12), 'name': u'c', 'taskID': '4'}]),
    #
    #   ({'end': None, 'name': u'psetmath', 'isFinished': 0, 'cat': u'math', 'start': None, 'taskID': '6'},
    #   [{'isFinished': 0, 'end': None, 'name': u'one', 'taskID': '7'},
    #   {'isFinished': 0, 'end': None, 'name': u'two', 'taskID': '8'},
    #   {'isFinished': 0, 'end': None, 'name': u'three', 'taskID': '9'}])]


    # {'end': datetime.date(1111, 11, 12), 'name': u'psetCS', 'isFinished': 0, 'cat': u'cs', 'start': datetime.date(1111, 11, 11), 'taskID': '1'}



def buildDropdown(timeSelection,dataSelection):
    data = [['value="day"','Day View'],['value="week"','Week View'],['value="month"','Month View']]
    # if timeSelection == "week":
    #     data[1][0] = 'value="shit"'
    #     print data
    return data


def getCats(userID):#check this part, need to check for none value
    curs = cursor(DATABASE)
    curs.execute('select * from category where userID = "{0}";'.format(userID))
    allCats = curs.fetchall()
    if allCats!=None:

        return allCats
    else:
        return []

def addCat(name,color,userID):
    curs = cursor(DATABASE)
    try:
        curs.execute('insert into category(name, color,userID) values ("{0}","{1}","{2}");'.format(name, color,userID))
        print "successful insert"
        flash("Inserted " + name + " successfully!")
    except:
        print "todo"
        print "did not work"


def addTask(isFinished,userID,taskName,start,end,cat):
    curs = cursor(DATABASE)
    try:
        curs.execute('select * from task where taskName = "{0}" and start = "{1}" and end = "{2}" and userID = "{3}";'.format(taskName,start,end,userID))
        row = curs.fetchone()
        if row == None:
            curs.execute('insert into task(isFinished,userID,taskName,start,end,name) values ("{0}","{1}","{2}","{3}","{4}","{5}");'.format(isFinished,userID,taskName,start,end,cat))
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

def addLog(cat,hours,userID,taskDate):
    curs = cursor(DATABASE)
    curs.execute('select * from logEntry where name = "{0}" and taskDate = "{1}" and userID = "{2}";'.format(cat,taskDate,userID))
    row = curs.fetchone()
    if row == None:
        curs.execute('insert into logEntry values ("{0}","{1}","{2}","{3}");'.format(cat,hours,userID,taskDate))
        flash('log has been entered')
    else:
        #existingHour = row['hours']
        curs.execute('update logEntry set hours = hours + "{0}" where name = "{1}" and taskDate = "{2}" and userID = "{3}";'.format(hours,cat,taskDate,userID))
        flash('log has been updated ')


def checkLog(logType):
    curs = cursor(DATABASE)
    if logType == 'day':
        curs.execute('select taskDate,sum(hours) as accum from logEntry group by taskDate;')
    #if logType == 'day':#per week
    #    curs.execute('select taskDate, sum(hours) as accum from logEntry where taskDate between date_sub(now(),INTERVAL 1 WEEK) and now() group by taskDate;')
    if logType == 'week':
        curs.execute('select taskDate, sum(hours) as accum from logEntry group by YEARWEEK(taskDate);')
    if logType == 'month':
        curs.execute('select taskDate, sum(hours) as accum from logEntry group by YEAR(taskDate), MONTH(taskDate);')
    rows = curs.fetchall()
    if rows!=None:
        return rows
    else:
        flash('no log record')
        return [{'taskDate':'','accum':''}]
