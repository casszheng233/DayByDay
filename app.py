#CS304 Phase3 draft
#app.py
#Rosie Pyktel and Cassandra Zheng
from flask import Flask, render_template, flash, request, redirect, url_for
import os
import p3
import datetime as dt

app = Flask(__name__)
app.secret_key = "whatever"

# DATABASE = 'czheng_db'
DATABASE = 'rpyktel_db'

# html base template, never seen
@app.route('/base/')
def landingPage():
    return render_template('base.html', database=DATABASE)

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
@app.route('/')
def fillCats():
    allCats = p3.getCats(1)
    dropCats = p3.getCats(1)
    return redirect(url_for('day_checklist'))

# routing for adding a category
#todo: add error handling for if catName not unique, add a better way to select a color
@app.route('/addCat/', methods = ['POST'])
def addCat():
    name = request.form['catName']
    color = request.form['catColor']
    if name.split()!=[]:
        p3.addCat(name,color,1)#last one is userID

    else:
        flash('please enter all required information')
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    allCats = p3.getCats(1)
    return render_template('base.html', allCats =  allCats, database = DATABASE)

# todo: move some of this logic to p3.py
@app.route('/addTask/', methods = ['POST'])
def addTask():

    allCats = p3.getCats(1) #need to take care of userID
    isFinished = 0 #default:not finished
    taskName = request.form['catName'] #should we change the name of this varchar
    userID = 1 #currently hard coded, need to change once we have the login page
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
                if (numSubtask == 0):
                    p3.addSubtaskNull(userID,parID)

                for i in range(1,numSubtask+1):
                        sub = request.form['subtask'+str(i)]
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
    allCats = p3.getCats(1)#need to take care of userID
    taskName = request.form['catName']#should we change the name of this varchar
    userID = 1#currently hard coded, need to change once we have the login page
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
    redirDic = {"day-checklist":"day_checklist","week-checklist":"week_checklist","month-checklist":"month_checklist"}
    if request.method == 'POST':
        value = request.form['catHidden']
        redir = request.form['catHiddenRedirect']

        print redir

    return redirect(url_for(redirDic[redir])) #todo: go to wherever they were


@app.route('/addLog/',methods = ['POST'])
def addLog():
    allCats = p3.getCats(1)
    cat = request.form['catName']
    hours = request.form['hour']
    taskDate = request.form['taskDate']
    userID = 1 #hard coded, need to be changed
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
    allCats = p3.getCats(1)
    timeSelection = request.form['time']
    dataSelection = request.form['views']

    #routing for log
    if (dataSelection == "log"):
        return redirect(url_for('logview',timeSelection=timeSelection))

    # routing for day and checklist
    if (timeSelection == "day" and dataSelection == "checklist"):
        return redirect(url_for('day_checklist'))
    if (timeSelection == "week" and dataSelection == "checklist"):
        return redirect(url_for('week_checklist'))
    if (timeSelection == "month" and dataSelection == "checklist"):
        return redirect(url_for('month_checklist'))

    else:
        rightpanel = "View: " + str(timeSelection) + " " + str(dataSelection)
        dropdowns = p3.buildDropdown(timeSelection,dataSelection)
        return render_template('base.html', allCats =  allCats, timeSelect1 = dropdowns, rightPanel = rightpanel, database = DATABASE)

@app.route('/logview/<timeSelection>/', methods = ['GET','POST'])
def logview(timeSelection):
    allCats = p3.getCats(1)
    dFormat = "MMM/DD/YYYY"
    if timeSelection=='day':
        dFormat = "MMM/DD/YYYY"
        intervalGap = 1
        intType = 'day'
    elif timeSelection == 'week':
        dFormat = "MMM/DD/YYYY"
        intervalGap = 7
        intType = 'day'
    elif timeSelection == 'month':
        dFormat = "MMM/YYYY"
        intervalGap = 1
        intType = 'month'
    log = p3.checkLog(timeSelection,1)#TODO:userID is hard coded
    logRecord = []
    for rec in log:
        recDate = rec['taskDate']
        if recDate!=None:
            cleanRec = [recDate.year,recDate.month,recDate.day]
            cleanRec.append(int(rec['accum']))
            logRecord.append(cleanRec)
    return render_template('base_log.html',allCats = allCats, database = DATABASE,logs = logRecord,dFormat = dFormat,intervalGap = intervalGap )


@app.route('/day-checklist/', methods = ['GET','POST'])
def day_checklist():
    allCats = p3.getCats(1)
    data = p3.rightPanelTask("hardcoded")
    return render_template('base_task_day.html',allCats =  allCats, dataStruct = data, database = DATABASE)

@app.route('/week-checklist/', methods = ['GET','POST'])
def week_checklist():
    allCats = p3.getCats(1)
    data = p3.rightPanelTask("user id currently hardcoded")
    return render_template('base_task_week.html', allCats =  allCats, dataStruct = data, database = DATABASE)

# rosie: please make inheretence for the week task views...
@app.route('/month-checklist/', methods = ['GET','POST'])
def month_checklist():
    allCats = p3.getCats(1)
    data = p3.rightPanelTask("user id currently hardcoded")
    return render_template('base_task_month.html', allCats =  allCats, dataStruct = data, database = DATABASE)

@app.route('/addEvent/',methods = ['POST'])
def addEvent():
    allCats = p3.getCats(1) #need to take care of userID
    eventName = request.form['eventName'] #should we change the name of this varchar
    userID = 1 #currently hard coded, need to change once we have the login page
    eventDate = request.form['eventDate']
    start = request.form['startTime']
    end = request.form['endTime']

    if eventName.split()!=[] and legalDate(eventDate):
        p3.addEvent(userID,eventName,eventDate,start,end)
    return render_template('base.html', allCats =  allCats, database = DATABASE)



    # try:
    #     if eventName.split()!=[] and legalDate(eventDate):
    #         p3.addEvent(userID,eventName,eventDate,start,end)
    #
    #
    #     else:
    #         flash('please check your entries!')
    #     # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    #     return render_template('base.html', allCats =  allCats, database = DATABASE)
    #
    # except:
    #     flash('something is wrong: check your entries!')
    #     return render_template('base.html', allCats =  allCats, database = DATABASE)
    #
    #



if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
