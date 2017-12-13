#CS304 Phase3 draft
#app.py
#Rosie Pyktel and Cassandra Zheng
from flask import Flask, render_template, flash, request, redirect, url_for, session
import os
import p3
import datetime as dt
import hashlib

app = Flask(__name__)
app.secret_key = "whatever"

# DATABASE = 'czheng_db'
DATABASE = 'rpyktel_db'

# html base template, never seen
@app.route('/')
def initialPage():
    return render_template('login.html')

@app.route('/login/',methods = ['GET','POST'])
def login():
    userID = request.form['userID']
    password = request.form['passwd']
    passwd = hashlib.sha256(password).hexdigest()

    row = p3.checkUser(userID,passwd)

    if row!=None:
        session['userID'] = row['userID']
        print row['userID']
        print session['userID']
        return redirect(url_for('day_checklist'))
    else:
        flash('Check your input!')
        return render_template('login.html', database=DATABASE)

@app.route('/createUser/',methods = ['POST'])
def createUser():
    username = request.form['userID']#@TODO:RENAME THIS
    passwd = request.form['passwd']
    encryption = hashlib.sha256(passwd).hexdigest()
    print encryption
    if username.split()!=[] and passwd.split()!=[] and p3.checkUsername(username) :
        p3.createUser(username,encryption)
        flash('successfully create username')
    else:
        flash('you may want to think of another name')
    return render_template('login.html', database=DATABASE)


@app.route('/logout/',methods = ['POST'])
def logout():
    session.pop('userID',None)
    return redirect(url_for('initialPage'))

# helper : check if the input date is legal or not
def legalDate(inputDate):
    s = inputDate.split('-')
    try:
        if len(s)==3:
            yr = int(s[0])
            month = int(s[1])
            day = int(s[2])
            return (0<month and month<13 and 0<day and day<32)
        else:
            return False
    except:
        return False


# version with categories filled out
# @app.route('/')
# def fillCats():
#     allCats = p3.getCats(1)
#     dropCats = p3.getCats(1)
#     return redirect(url_for('day_checklist'))

# routing for adding a category
#todo: add error handling for if catName not unique, add a better way to select a color
@app.route('/addCat/', methods = ['POST'])
def addCat():
    userID = session['userID']
    name = request.form['catName']
    color = request.form['catColor']
    if name.split()!=[]:
        p3.addCat(name,color,userID)#last one is userID

    else:
        flash('please enter all required information')
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    allCats = p3.getCats(userID)
    return render_template('base.html', allCats =  allCats, database = DATABASE)

# todo: move some of this logic to p3.py
@app.route('/addTask/', methods = ['POST'])
def addTask():
    userID = session['userID']
    # print "adding tasks"
    allCats = p3.getCats(userID) #need to take care of userID
    isFinished = 0 #default:not finished
    taskName = request.form['catName'] #should we change the name of this varchar
    # userID = userID #currently hard coded, need to change once we have the login page
    start = request.form['startDate']
    end = request.form['endDate']
    cat = request.form['catOpt']
    try:
        if taskName.split()!=[] and legalDate(start) and legalDate(end):
            p3.addTask(isFinished,userID,taskName,start,end,cat)
            checkID = p3.checkTaskID(taskName,start,end)
            if checkID!=None:
                parID = checkID['taskID']
                numSubtask = int(request.form['num']) #check number of subtasks
                print numSubtask
                if (numSubtask == 0):
                    p3.addSubtaskNull(userID,parID)

                for i in range(1,numSubtask+1):
                        sub = request.form['subtask'+str(i)]
                        print sub
                        if sub.split()!=[]:
                            startDT = dt.datetime.strptime(start,'%Y-%m-%d')
                            endDT = dt.datetime.strptime(end,'%Y-%m-%d')
                            numDays = endDT - startDT
                            length = numDays/numSubtask
                            daysFromStart = (length*i).days

                            endFormatted = startDT + dt.timedelta(days = daysFromStart)
                            endFormat = str(endFormatted)[:-9]

                            # print 'subTask'+str(i)
                            # print " "
                            p3.addTask(isFinished,userID,sub,start,endFormat,cat)
                            print "subtaskAdded"
                            childID = p3.checkTaskID(sub,start,endFormat)['taskID']
                            p3.addSubtask(userID,parID,childID)
        else:
            flash('please check your entries!')
        # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
        return render_template('base.html', allCats =  allCats, database = DATABASE)

    except:
        flash('something is wrong: check your entries!')
        return render_template('base.html', allCats =  allCats, database = DATABASE)

@app.route('/deleteTask/', methods = ['POST'])
def deleteTask():
    userID = session['userID']
    allCats = p3.getCats(userID)#need to take care of userID
    taskName = request.form['catName']#should we change the name of this varchar

    start = request.form['startDate']
    end = request.form['endDate']
    cat = request.form['catOpt']
    p3.deleteTask(userID,taskName,start,end,cat)
    return render_template('base.html', database=DATABASE,allCats = allCats)


# TODO
@app.route('/tickTask/', methods = ['GET','POST'])
def tickTask():
    if request.method == 'POST':
        value = request.form['taskCheck']
        redirectVal = request.form['timeSelector']
        p3.tickBox(value)
        # print value
    return redirect(url_for(redirectVal))

@app.route('/tickedCats/', methods = ['GET', 'POST'])
def tickedCats():
    redirDic = {"day-checklist":"day_checklist","week-checklist":"week_checklist","month-checklist":"month_checklist",
    "day-event":"day_event","week-event":"week_event","month-event":"month_event",
    "day-logview":"day_logview","week-logview":"week_logview","month-logview":"month_logview"}
    if request.method == 'POST':
        value = request.form['catHidden']
        redir = request.form['catHiddenRedirect']

        # print redir

    return redirect(url_for(redirDic[redir])) #todo: go to wherever they were


@app.route('/addLog/',methods = ['POST'])
def addLog():
    userID = session['userID']
    allCats = p3.getCats(userID)
    cat = request.form['catName']
    hours = request.form['hour']
    taskDate = request.form['taskDate']
    # userID = 1 #hard coded, need to be changed
    try:
        if legalDate(taskDate) and int(hours)>0: #check if input is legal
            p3.addLog(cat,hours,userID,taskDate)
        else:
            flash('check your input')
        return render_template('base.html',allCats = allCats, database = DATABASE)
    except:
        flash('check your input')
        return render_template('base.html',allCats = allCats, database = DATABASE)


@app.route('/changeView/', methods = ['POST'])
def changeView():
    userID = session['userID']
    allCats = p3.getCats(userID)
    timeSelection = request.form['time']
    dataSelection = request.form['views']

    #routing for log
    if (timeSelection == "day" and dataSelection == "log"):
        print "day log"
        return redirect(url_for('day_logview'))
    elif (timeSelection == "week" and dataSelection == "log"):
        print "week log"
        return redirect(url_for('week_logview'))
    elif (timeSelection == "month" and dataSelection == "log"):
        print "month log"
        return redirect(url_for('month_logview'))

    # routing for checklist
    if (timeSelection == "day" and dataSelection == "checklist"):
        return redirect(url_for('day_checklist'))
    if (timeSelection == "week" and dataSelection == "checklist"):
        return redirect(url_for('week_checklist'))
    if (timeSelection == "month" and dataSelection == "checklist"):
        return redirect(url_for('month_checklist'))

    #routing for events
    if (timeSelection == "day" and dataSelection == "events"):
        return redirect(url_for('day_event'))
    if (timeSelection == "week" and dataSelection == "events"):
        return redirect(url_for('week_event'))
    if (timeSelection == "month" and dataSelection == "events"):
        return redirect(url_for('month_event'))
    else:
        rightpanel = "View: " + str(timeSelection) + " " + str(dataSelection)
        dropdowns = p3.buildDropdown(timeSelection,dataSelection)
        return render_template('base.html', allCats =  allCats, timeSelect1 = dropdowns, rightPanel = rightpanel, database = DATABASE)

@app.route('/day-logview/', methods = ['GET','POST'])
def day_logview():
    userID = session['userID']
    allCats = p3.getCats(userID) #need to take care of userID
    dFormat = "MMM/DD/YYYY"
    intervalGap = 1
    intType = 'day'
    logDict = {}
    logDict['all'] = p3.checkLog('day',userID,'all')
    for eachCat in allCats:
        cat = eachCat['name']

        catInfo = p3.checkLog('day',userID,cat)#list of dictionary
        logDict[str(cat)] = p3.checkLog('day',userID,cat)
    colorRows = p3.checkCatColor(userID)
    colorDict = {}
    colorDict['all']='black'
    if colorRows != None:
        for eachRow in colorRows:
            colorDict[str(eachRow['name'])]=str(eachRow['color'])

    return render_template('base_log_day.html',allCats = allCats, database = DATABASE,logs = logDict,dFormat = dFormat,intervalGap = intervalGap,colorDict = colorDict )



@app.route('/week-logview/', methods = ['GET','POST'])
def week_logview():
    userID = session['userID']
    allCats = p3.getCats(userID) #need to take care of userID
    dFormat = "MMM/DD/YYYY"
    intervalGap = 7
    intType = 'day'
    logDict = {}
    logDict['all'] = p3.checkLog('week',userID,'all')
    for eachCat in allCats:
        cat = eachCat['name']

        catInfo = p3.checkLog('week',userID,cat)#list of dictionary
        logDict[str(cat)] = p3.checkLog('week',userID,cat)
    colorRows = p3.checkCatColor(userID)
    colorDict = {}
    colorDict['all']='black'
    if colorRows != None:
        for eachRow in colorRows:
            colorDict[str(eachRow['name'])]=str(eachRow['color'])
    return render_template('base_log_week.html',allCats = allCats, database = DATABASE,logs = logDict,dFormat = dFormat,intervalGap = intervalGap, colorDict=colorDict )

    # else:
    #     flash('something is wrong')
    #     return render_template('base.html',allCats = allCats,database = DATABASE)

@app.route('/month-logview/', methods = ['GET','POST'])
def month_logview():
    userID = session['userID']
    allCats = p3.getCats(userID) #need to take care of userID
    dFormat = "MMM/YYYY"
    intervalGap = 1
    intType = 'month'

    logDict = {}
    logDict['all'] = p3.checkLog('month',userID,'all')
    for eachCat in allCats:
        cat = eachCat['name']

        catInfo = p3.checkLog('month',userID,cat)#list of dictionary
        logDict[str(cat)] = p3.checkLog('month',userID,cat)
    colorRows = p3.checkCatColor(userID)
    colorDict = {}
    colorDict['all']='black'
    if colorRows != None:
        for eachRow in colorRows:
            colorDict[str(eachRow['name'])]=str(eachRow['color'])
    return render_template('base_log_month.html',allCats = allCats, database = DATABASE,logs = logDict,dFormat = dFormat,intervalGap = intervalGap, colorDict=colorDict )




@app.route('/day-checklist/', methods = ['GET','POST'])
def day_checklist():
    userID = session['userID']
    allCats = p3.getCats(userID)
    data = p3.rightPanelTask(userID)
    return render_template('base_task_day.html',allCats =  allCats, dataStruct = data, database = DATABASE)

@app.route('/week-checklist/', methods = ['GET','POST'])
def week_checklist():
    userID = session['userID']
    allCats = p3.getCats(userID)
    data = p3.rightPanelTask(userID)
    return render_template('base_task_week.html', allCats =  allCats, dataStruct = data, database = DATABASE)

# rosie: please make inheretence for the week task views...
@app.route('/month-checklist/', methods = ['GET','POST'])
def month_checklist():
    userID = session['userID']
    allCats = p3.getCats(userID)
    data = p3.rightPanelTask(userID)
    return render_template('base_task_month.html', allCats =  allCats, dataStruct = data, database = DATABASE)

@app.route('/addEvent/',methods = ['POST'])
def addEvent():
    userID = session['userID']
    allCats = p3.getCats(userID) #need to take care of userID
    eventName = request.form['eventName'] #should we change the name of this varchar

    eventDate = request.form['eventDate']
    start = request.form['startTime'] + ':00'
    end = request.form['endTime'] + ':00'

    if eventName.split()!=[] and legalDate(eventDate):
        p3.addEvent(userID,eventName,eventDate,start,end)
    return render_template('base.html', allCats =  allCats, database = DATABASE)

@app.route('/day-event/', methods = ['GET','POST'])
def day_event():
    userID = session['userID']
    allCats = p3.getCats(userID) #need to take care of userID
    data = p3.rightPanelEvent(userID)
    return render_template('base_event_day.html',allCats =  allCats, dataStruct = data, database = DATABASE)

@app.route('/week-event/', methods = ['GET','POST'])
def week_event():
    userID = session['userID']
    allCats = p3.getCats(userID) #need to take care of userID
    data = p3.rightPanelEvent(userID)
    return render_template('base_event_week.html', allCats =  allCats, dataStruct = data, database = DATABASE)

@app.route('/month-event/', methods = ['GET','POST'])
def month_event():
    userID = session['userID']
    allCats = p3.getCats(userID) #need to take care of userID
    data = p3.rightPanelEvent(userID)
    return render_template('base_event_month.html', allCats =  allCats, dataStruct = data, database = DATABASE)



if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
