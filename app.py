# CS304 Final Project
# Alpha Version
# app.py
# Rosie Pyktel and Cassandra Zheng
from flask import Flask, render_template, flash, request, redirect, url_for, session, jsonify
import os
import p3
import datetime as dt
import hashlib
from DSN import *

app = Flask(__name__)
app.secret_key = "whatever"
#DATABASE = 'czheng_db'

# html base template
@app.route('/')
def initialPage():
    return render_template('login.html')

@app.route('/login/',methods = ['GET','POST'])
def login():#login page
    conn = p3.getConnection()
    userID = request.form['userID']
    password = request.form['passwd']
    passwd = hashlib.sha256(password).hexdigest()#hashing password
    row = p3.checkUser(conn,userID,passwd)#check the account exist/password match with the account
    if row!=None:
        session['userID'] = row['userID']
        return redirect(url_for('dayByDay'))
    else:#wrong information
        flash('No record is matched. Try again or create a new account!')
        return render_template('login.html', database=DATABASE)

@app.route('/DayByDay/',methods = ['GET','POST'])
def dayByDay():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            data = p3.rightPanelTask(conn,userID)
            return render_template('base_task_day.html',allCats =  allCats, dataStruct = data, database = DATABASE)
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/createUser/',methods = ['POST'])
def createUser():#create a new user account
    conn = p3.getConnection()
    username = request.form['userID']#@TODO:RENAME THIS
    passwd = request.form['passwd']
    encryption = hashlib.sha256(passwd).hexdigest()

    #check if input is valid
    if username.split()!=[] and passwd.split()!=[] and p3.checkUsername(conn,username) :
        p3.createUser(conn,username,encryption)
        flash('User created! Please sign in.')
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

#create new category: catName, catColor
@app.route('/addCat/', methods = ['POST'])
def addCat():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']

            if (request.form['catName'] == "") or (request.form['catColor'] == ""):
                return jsonify({"error":"Empty inputs!"})

            name = request.form['catName']
            color = request.form['catColor']

            checkError = p3.addCat(conn,name,color,userID)
            if (checkError):
                return jsonify({"error":"Duplicate category!"})

            data = {"catName": name, "catColor": color}
            return jsonify(data)
        else:
            flash('not logged in!')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

#create a new task
@app.route('/addTask/', methods = ['POST'])
def addTask():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            isFinished = 0
            taskName = request.form['catName']
            start = request.form['startDate']
            end = request.form['endDate']
            cat = request.form['catOpt']

            try:
                if taskName.split()!=[] and legalDate(start) and legalDate(end):
                    checkError = p3.addTask(conn,isFinished,userID,taskName,start,end,cat)
                    if (checkError):
                        return jsonify({"error":"Duplicate task!"})

                    checkID = p3.checkTaskID(conn,taskName,start,end)
                    if checkID!=None:
                        parID = checkID['taskID']
                        numSubtask = int(request.form['num']) #check number of subtasks
                        print numSubtask
                        if (numSubtask == 0):
                            p3.addSubtaskNull(conn,userID,parID)

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

                                    p3.addTask(conn,isFinished,userID,sub,start,endFormat,cat)
                                    print "subtaskAdded"
                                    childID = p3.checkTaskID(conn,sub,start,endFormat)['taskID']
                                    p3.addSubtask(conn,userID,parID,childID)
                else:
                    return jsonify({"error":"Empty inputs!"})

                jsonData = p3.rightPanelTask(conn,userID)
                return jsonify(jsonData)

            except:
                flash('something is wrong: check your entries!')
                return render_template('base.html', allCats =  allCats, database = DATABASE)
        else:
            print "omg 2"
            return render_template('login.html')
    except:
        print "omg3"
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/deleteTask/', methods = ['POST'])
def deleteTask():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(userID)#need to take care of userID
            taskName = request.form['catName']#should we change the name of this varchar

            start = request.form['startDate']
            end = request.form['endDate']
            cat = request.form['catOpt']
            p3.deleteTask(userID,taskName,start,end,cat)
            return render_template('base.html', database=DATABASE,allCats = allCats)
        else:
            flash('not currently logged in')
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')


@app.route('/tickTask/', methods = ['GET','POST'])
def tickTask():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            if request.method == 'POST':
                value = request.form['taskCheck']
                redirectVal = request.form['timeSelector']
                p3.tickBox(conn,value)
                # print redirectVal
            # return redirect(url_for(redirectVal))
            return json.dumps({'status':'OK','user':value,'pass':redirectVal});
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/tickedCats/', methods = ['GET', 'POST'])
def tickedCats():
    conn = p3.getConnection()
    if 'userID' in session:
        userID = session['userID']
        if request.method == 'POST':
            # value = request.form['catHidden']
            dataSelection = request.form['catHiddenRedirect']

            if (dataSelection == "checklist"):
                dataStruct = p3.rightPanelTask(conn,userID)
                return jsonify(dataStruct)
            if (dataSelection == "events"):
                dataStruct = p3.rightPanelEvent(conn,userID)
                return jsonify(dataStruct)
            if (dataSelection == "log"):
                allCats = p3.getCats(conn,userID)
                dataStruct = p3.allLog(conn,userID,allCats)
                return jsonify(dataStruct)

    return jsonify({"error":"oh my god2"})



# @app.route('/tickedCats/', methods = ['GET', 'POST'])
# def tickedCats():
#     try:
#         conn = p3.getConnection()
#         if 'userID' in session:
#             print "userID is in session"
#             if request.method == 'POST':
#                 print "it's a post"
#                 print "big cocks"
#                 # value = request.form['catHidden']
#                 dataSelection = request.form['catHiddenRedirect']
#
#                 # print value
#                 print dataSelection
#
#                 if (dataSelection == "checklist"):
#                     dataStruct = p3.rightPanelTask(conn,userID)
#                     return jsonify(dataStruct)
#                 # if (dataSelection == "events"):
#                 #     dataStruct = p3.rightPanelEvent(conn,userID)
#                 #     return jsonify(dataStruct)
#                 # if (dataSelection == "log"):
#                 #     print "TODO"
#
#                 return jsonify({"error":"oh my god1"})
#
#                 # timeSelection = redir.split('-')[0]
#                 # dataSelection = redir.split('-')[1]
#
#                 # print timeSelection
#                 # print dataSelection
#
#                 # if (dataSelection == "checklist"):
#                 #     dataStruct = p3.rightPanelTask(conn,userID)
#                 #     return jsonify(dataStruct)
#                 # if (dataSelection == "events"):
#                 #     dataStruct = p3.rightPanelEvent(conn,userID)
#                 #     return jsonify(dataStruct)
#                 # if (dataSelection == "log"):
#                 #     print "TODO"
#
#             # redirDic = {"day-checklist":"day_checklist","week-checklist":"week_checklist","month-checklist":"month_checklist",
#             # "day-event":"day_event","week-event":"week_event","month-event":"month_event",
#             # "day-logview":"day_logview","week-logview":"week_logview","month-logview":"month_logview"}
#             # if request.method == 'POST':
#             #     value = request.form['catHidden']
#             #     redir = request.form['catHiddenRedirect']
#
#             # return redirect(url_for(redirDic[redir]))
#             return jsonify({"error":"oh my god2"})
#         else:
#             print "something happened1"
#             return render_template('login.html')
#     except:
#         flash('Error! Redirecting to login page')
#         print "something happened2"
#         return render_template('login.html')



#input a new log
@app.route('/addLog/',methods = ['POST'])
def addLog():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            cat = request.form['catName']
            hours = request.form['hour']
            taskDate = request.form['taskDate']
            try:
                if legalDate(taskDate) and int(hours)>0: #check if input is legal
                    p3.addLog(conn,cat,hours,userID,taskDate)
                else:
                    # print "check input!!!"
                    flash('check your input')
                    return jsonify({"error":"Empty inputs!"})
                # return redirect(url_for('day_logview'))
                #data = {"cat": cat,"hour":hours,"taskDate":taskDate}

                # logDictDay = {}
                # logDictDay['all'] = p3.checkLog(conn,'day',userID,'all')
                # for eachCat in allCats:
                #     cat = eachCat['name']
                #
                #     catInfo = p3.checkLog(conn,'day',userID,cat)#list of dictionary
                #     logDictDay[str(cat)] = p3.checkLog(conn,'day',userID,cat)
                #
                #
                # logDictWeek = {}
                # logDictWeek['all'] = p3.checkLog(conn,'week',userID,'all')
                # for eachCat in allCats:
                #     cat = eachCat['name']
                #
                #     catInfo = p3.checkLog(conn,'week',userID,cat)#list of dictionary
                #     logDictWeek[str(cat)] = p3.checkLog(conn,'week',userID,cat)
                #
                # logDictMonth = {}
                # logDictMonth['all'] = p3.checkLog(conn,'month',userID,'all')
                # for eachCat in allCats:
                #     cat = eachCat['name']
                #
                #     catInfo = p3.checkLog(conn,'month',userID,cat)#list of dictionary
                #     logDictMonth[str(cat)] = p3.checkLog(conn,'month',userID,cat)
                #
                # colorRows = p3.checkCatColor(conn,userID)
                # colorDict = {}
                # colorDict['all']='000000'
                # if colorRows != None:
                #     for eachRow in colorRows:
                #         colorDict[str(eachRow['name'])]=str(eachRow['color'])

                #dataDay = p3.checkLog(conn,'day','userID')
                dataStruct = p3.allLog(conn,userID,allCats)
                return jsonify(dataStruct)

                # return jsonify([logDictDay,logDictWeek, logDictMonth, colorDict])
            except:
                flash('check your input')
                # print("very wrong!!!!")
                # return redirect(url_for('login.html'))
                return jsonify({"error":"Not a valid number!"})
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')


@app.route('/changeView/', methods = ['POST'])
def changeView():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            timeSelection = request.form['time']
            dataSelection = request.form['views']

            if (dataSelection == "checklist"):
                dataStruct = p3.rightPanelTask(conn,userID)
                return jsonify(dataStruct)
            if (dataSelection == "events"):
                dataStruct = p3.rightPanelEvent(conn,userID)
                return jsonify(dataStruct)
            if (dataSelection == "log"):
                print "at dataselectionlog!"
                dataStruct = p3.allLog(conn,userID,allCats)
                print dataStruct
                return jsonify(dataStruct)





            #routing for log
            # if (timeSelection == "day" and dataSelection == "log"):
            #     print "day log"
            #     return redirect(url_for('day_logview'))
            # elif (timeSelection == "week" and dataSelection == "log"):
            #     print "week log"
            #     return redirect(url_for('week_logview'))
            # elif (timeSelection == "month" and dataSelection == "log"):
            #     print "month log"
            #     return redirect(url_for('month_logview'))
            #
            # # routing for checklist
            # if (timeSelection == "day" and dataSelection == "checklist"):
            #     return redirect(url_for('day_checklist'))
            # if (timeSelection == "week" and dataSelection == "checklist"):
            #     return redirect(url_for('week_checklist'))
            # if (timeSelection == "month" and dataSelection == "checklist"):
            #     return redirect(url_for('month_checklist'))
            #
            # #routing for events
            # if (timeSelection == "day" and dataSelection == "events"):
            #     return redirect(url_for('day_event'))
            # if (timeSelection == "week" and dataSelection == "events"):
            #     return redirect(url_for('week_event'))
            # if (timeSelection == "month" and dataSelection == "events"):
            #     return redirect(url_for('month_event'))
            # else:
            #     rightpanel = "View: " + str(timeSelection) + " " + str(dataSelection)
            #     dropdowns = p3.buildDropdown(timeSelection,dataSelection)
            #     return render_template('base.html', allCats =  allCats, timeSelect1 = dropdowns, rightPanel = rightpanel, database = DATABASE)
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/day-logview/', methods = ['GET','POST'])
def day_logview():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            dFormat = "MMM/DD/YYYY"
            intervalGap = 1
            intType = 'day'
            logDict = {}
            logDict['all'] = p3.checkLog(conn,'day',userID,'all')
            for eachCat in allCats:
                cat = eachCat['name']

                catInfo = p3.checkLog(conn,'day',userID,cat)#list of dictionary
                logDict[str(cat)] = p3.checkLog(conn,'day',userID,cat)
            colorRows = p3.checkCatColor(conn,userID)
            colorDict = {}
            colorDict['all']='000000'
            if colorRows != None:
                for eachRow in colorRows:
                    colorDict[str(eachRow['name'])]=str(eachRow['color'])

            return render_template('base_log_day.html',allCats = allCats, database = DATABASE,logs = logDict,dFormat = dFormat,intervalGap = intervalGap,colorDict = colorDict )

        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/week-logview/', methods = ['GET','POST'])
def week_logview():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            dFormat = "MMM/DD/YYYY"
            intervalGap = 7
            intType = 'day'
            logDict = {}
            logDict['all'] = p3.checkLog(conn,'week',userID,'all')
            for eachCat in allCats:
                cat = eachCat['name']

                catInfo = p3.checkLog(conn,'week',userID,cat)#list of dictionary
                logDict[str(cat)] = p3.checkLog(conn,'week',userID,cat)
            colorRows = p3.checkCatColor(conn,userID)
            colorDict = {}
            colorDict['all']='black'
            if colorRows != None:
                for eachRow in colorRows:
                    colorDict[str(eachRow['name'])]=str(eachRow['color'])
            return render_template('base_log_week.html',allCats = allCats, database = DATABASE,logs = logDict,dFormat = dFormat,intervalGap = intervalGap, colorDict=colorDict )
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')


@app.route('/month-logview/', methods = ['GET','POST'])
def month_logview():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            dFormat = "MMM/YYYY"
            intervalGap = 1
            intType = 'month'

            logDict = {}
            logDict['all'] = p3.checkLog(conn,'month',userID,'all')
            for eachCat in allCats:
                cat = eachCat['name']

                catInfo = p3.checkLog(conn,'month',userID,cat)#list of dictionary
                logDict[str(cat)] = p3.checkLog(conn,'month',userID,cat)
            colorRows = p3.checkCatColor(conn,userID)
            colorDict = {}
            colorDict['all']='black'
            if colorRows != None:
                for eachRow in colorRows:
                    colorDict[str(eachRow['name'])]=str(eachRow['color'])
            return render_template('base_log_month.html',allCats = allCats, database = DATABASE,logs = logDict,dFormat = dFormat,intervalGap = intervalGap, colorDict=colorDict )
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')



@app.route('/day-checklist/', methods = ['GET','POST'])
def day_checklist():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            data = p3.rightPanelTask(conn,userID)
            return render_template('base_task_day.html',allCats =  allCats, dataStruct = data, database = DATABASE)
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/week-checklist/', methods = ['GET','POST'])
def week_checklist():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            data = p3.rightPanelTask(conn,userID)
            return render_template('base_task_week.html', allCats =  allCats, dataStruct = data, database = DATABASE)
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/month-checklist/', methods = ['GET','POST'])
def month_checklist():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            data = p3.rightPanelTask(conn,userID)
            return render_template('base_task_month.html', allCats =  allCats, dataStruct = data, database = DATABASE)
        else:
            flash('you are not currently logged in')
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/addEvent/',methods = ['POST'])
def addEvent():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)

            if (request.form['eventName'] == "") or (request.form['eventDate'] == "") or (request.form['eventName'] == "") or (request.form['eventName'] == ""):
                return jsonify({"error":"Empty inputs!"})

            startCheck = request.form['startTime'].split(':')
            startCheckFormat = int(startCheck[0] + startCheck[1])
            endCheck = request.form['endTime'].split(':')
            endCheckFormat = int(endCheck[0] + endCheck[1])
            if (endCheckFormat < startCheckFormat):
                return jsonify({"error":"Time continuum violation!"})

            eventName = request.form['eventName'] # we should change the name of this varchar
            eventDate = request.form['eventDate']
            start = request.form['startTime'] + ':00'
            end = request.form['endTime'] + ':00'

            if eventName.split()!=[] and legalDate(eventDate):
                checkError = p3.addEvent(conn,userID,eventName,eventDate,start,end)
                print checkError
                if (checkError):
                    return jsonify({"error": "Scheduling conflict!"})


            dataStruct = p3.rightPanelEvent(conn,userID)
            return jsonify(dataStruct)
        else:
            print "break1"
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        print "break2"
        return render_template('login.html')

@app.route('/day-event/', methods = ['GET','POST'])
def day_event():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            data = p3.rightPanelEvent(conn,userID)
            return render_template('base_event_day.html',allCats =  allCats, dataStruct = data, database = DATABASE)
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/week-event/', methods = ['GET','POST'])
def week_event():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID)
            data = p3.rightPanelEvent(conn,userID)
            return render_template('base_event_week.html', allCats =  allCats, dataStruct = data, database = DATABASE)
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')

@app.route('/month-event/', methods = ['GET','POST'])
def month_event():
    try:
        conn = p3.getConnection()
        if 'userID' in session:
            userID = session['userID']
            allCats = p3.getCats(conn,userID) #need to take care of userID
            data = p3.rightPanelEvent(conn,userID)
            return render_template('base_event_month.html', allCats =  allCats, dataStruct = data, database = DATABASE)
        else:
            return render_template('login.html')
    except:
        flash('Error! Redirecting to login page')
        return render_template('login.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()=='csv'
@app.route('/upload/', methods=["POST"])
def csvUpload():

    if 'userID' in session:
        userID = session['userID']
        conn = p3.getConnection()
        allCats = p3.getCats(conn,userID)
        f = request.files['file']
        if not f:
            flash('No file is selected')
            #return render_template('base.html',allCats=allCats)
        if allowed_file(f.filename):
            csv_input = pandas.read_csv(f,header=None)
            data = csv_input.values

            for eachRow in data:
                try:
                    if eachRow[0]=='log':
                        cat = eachRow[1]
                        hours = int(eachRow[3])
                        rawDate= eachRow[2].split('/')
                        logDate = rawDate[2]+'-'+rawDate[0]+'-'+rawDate[1]
                        p3.addLog(conn,cat,hours,userID,logDate)
                    elif eachRow[0] == 'event':
                        eventName = eachRow[1]
                        rawDate= eachRow[2].split('/')
                        eventDate = rawDate[2]+'-'+rawDate[0]+'-'+rawDate[1]
                        start = eachRow[3]+':00'
                        end = eachRow[4]+':00'
                        p3.addEvent(conn,userID,eventName,eventDate,start,end)
                    elif eachRow[0]=='task':
                        cat = eachRow[1]
                        isFinished = int(eachRow[2])
                        taskName = eachRow[3]
                        rawStart= eachRow[4].split('/')
                        start = rawStart[2]+'-'+rawStart[0]+'-'+rawStart[1]
                        rawEnd= eachRow[5].split('/')
                        end = rawEnd[2]+'-'+rawEnd[0]+'-'+rawEnd[1]
                        if taskName.split()!=[] and legalDate(start) and legalDate(end):
                            p3.addTask(conn,isFinished,userID,taskName,start,end,cat)
                            checkID = p3.checkTaskID(conn,taskName,start,end)
                            if checkID!=None:
                                parID = checkID['taskID']
                                numSubtask = len(eachRow)-6 #check number of subtasks
                                print numSubtask
                                if (numSubtask == 0):
                                    p3.addSubtaskNull(conn,userID,parID)
                                elif (numSubtask>0):
                                    for i in range(6,len(eachRow)):
                                        sub = eachRow[i]
                                        if sub.split()!=[]:
                                            startDT = dt.datetime.strptime(start,'%Y-%m-%d')
                                            print startDT
                                            endDT = dt.datetime.strptime(end,'%Y-%m-%d')
                                            numDays = endDT - startDT
                                            length = numDays/numSubtask
                                            daysFromStart = (length*(i-5)).days
                                            endFormatted = startDT + dt.timedelta(days = daysFromStart)
                                            endFormat = str(endFormatted)[:-9]
                                            p3.addTask(conn,isFinished,userID,sub,start,endFormat,cat)
                                            print "subtaskAdded"
                                            childID = p3.checkTaskID(conn,sub,start,endFormat)['taskID']
                                            p3.addSubtask(conn,userID,parID,childID)
                except:
                    flash("invalid input")

        return render_template('base.html',allCats = allCats)
    else:
        return render_template('login.html')


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
