
from flask import Flask, render_template, flash, request, redirect, url_for
import os
import p3

app = Flask(__name__)
app.secret_key = "whatever"

# DATABASE = 'czheng_db'
DATABASE = 'rpyktel_db'

# html base template, never seen
@app.route('/base/')
def landingPage():
    return render_template('base.html', database=DATABASE)

# version with categories filled out
@app.route('/')
def fillCats():
    allCats = p3.getCats(1)
    dropCats = p3.getCats(1)
    # p3.rightPanelTask('hardcoded in function') # delete this line later Rosie
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    return render_template('base_personalized.html', allCats =  allCats, add_dropdown = dropCats , database = DATABASE)

# routing for adding a category
#todo: add error handling for if catName not unique, add a better way to select a color
@app.route('/addCat/', methods = ['POST'])
def addCat():
    name = request.form['catName']
    color = request.form['catColor']
    p3.addCat(name,color,1)#last one is userID
    allCats = p3.getCats(1)
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    return render_template('base_personalized.html', allCats =  allCats, database = DATABASE)

@app.route('/addTask/', methods = ['POST'])
def addTask():
    allCats = p3.getCats(1)#need to take care of userID
    isFinished = 0#default:not finished
    taskName = request.form['catName']#should we change the name of this varchar
    userID = 1#currently hard coded, need to change once we have the login page
    start = request.form['startDate']
    end = request.form['endDate']
    cat = request.form['catOpt']
    p3.addTask(isFinished,userID,taskName,start,end,cat)
    parID = p3.checkTaskID(taskName,start,end)['taskID']
    numSubtask = int(request.form['num'])
    for i in range(1,numSubtask+1):
            sub = request.form['subtask'+str(i)]
            if sub.split()!=[]:
                print 'subTask'+str(i)
                p3.addTask(isFinished,userID,sub,start,end,cat)
                childID = p3.checkTaskID(sub,start,end)['taskID']
                p3.addSubtask(userID,parID,childID)
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    return render_template('base_personalized.html', allCats =  allCats, database = DATABASE)

# TODO
@app.route('/deleteTask/', methods = ['GET'])
def deleteTask():
    return render_template('base.html', database=DATABASE)

@app.route('/addLog/',methods = ['POST'])
def addLog():
    allCats = p3.getCats(1)
    cat = request.form['catName']
    hours = request.form['hour']
    taskDate = request.form['taskDate']
    userID = 1 #hard coded, need to be changed
    p3.addLog(cat,hours,userID,taskDate)
    return render_template('base_personalized.html',allCats = allCats, database = DATABASE)

@app.route('/changeView/', methods = ['POST'])
def changeView():
    allCats = p3.getCats(1)
    timeSelection = request.form['time']
    dataSelection = request.form['views']

    #routing for all of log
    if (dataSelection == "log"):
        if timeSelection == 'day':
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
        log = p3.checkLog(timeSelection)
        logRecord = []
        for rec in log:
            recDate = rec['taskDate']
            if recDate!=None:
                cleanRec = [recDate.year,recDate.month,recDate.day]
                cleanRec.append(int(rec['accum']))
                logRecord.append(cleanRec)
        return render_template('base_log.html',allCats = allCats, database = DATABASE,logs = logRecord,dFormat = dFormat,intervalGap = intervalGap )

    # routing for day and checklist
    if (timeSelection == "day" and dataSelection == "checklist"):
        return redirect(url_for('day_checklist'))

    else:
        rightpanel = "View: " + str(timeSelection) + " " + str(dataSelection)
        dropdowns = p3.buildDropdown(timeSelection,dataSelection)
        print("got here")
        return render_template('base_personalized.html', allCats =  allCats, timeSelect1 = dropdowns, rightPanel = rightpanel, database = DATABASE)

@app.route('/day-checklist/', methods = ['GET','POST'])
def day_checklist():
    allCats = p3.getCats()

    # timeSelection = request.form['time']
    # dataSelection = request.form['views']
    # dropdowns = p3.buildDropdown(timeSelection,dataSelection)
    # rightpanel = "View: " + str(timeSelection) + " " + str(dataSelection)
    print "ha!"
    data = p3.rightPanelTask("hardcoded")

    return render_template('base_taskView.html', allCats =  allCats, dataStruct = data, database = DATABASE)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
