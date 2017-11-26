
from flask import Flask, render_template, flash, request, redirect, url_for
import os
import p3

app = Flask(__name__)
app.secret_key = "whatever"

DATABASE = 'rpyktel_db'

# html base template, never seen
@app.route('/base/')
def landingPage():
    return render_template('base.html', database=DATABASE)

# version with categories filled out
@app.route('/')
def fillCats():
    allCats = p3.getCats()
    return render_template('base_personalized.html', allCats =  allCats, database = DATABASE)

# routing for adding a category
#todo: add error handling for if catName not unique, add a better way to select a color
@app.route('/addCat/', methods = ['POST'])
def addCat():
    name = request.form['catName']
    color = request.form['catColor']
    p3.addCat(name,color)
    allCats = p3.getCats()
    return render_template('base_personalized.html', allCats =  allCats, database = DATABASE)

@app.route('/addTask/', methods = ['POST'])
def addTask():
    allCats = p3.getCats()
    isFinished = 0#default:not finished
    taskName = request.form['catName']#should we change the name of this varchar
    userID = 1#currently hard coded, need to change once we have the login page
    start = request.form['startDate']
    end = request.form['endDate']
    p3.addTask(isFinished,userID,taskName,start,end)
    parID = p3.checkTaskID(taskName,start,end)['taskID']
    subTask1 = request.form['subtask1']
    print subTask1
    subTask2 = request.form['subtask2']
    if subTask1.split()!=[]:
        print 'here'
        p3.addTask(isFinished,userID,subTask1,start,end)
        childID = p3.checkTaskID(subTask1,start,end)['taskID']
        p3.addSubtask(userID,parID,childID)
    return render_template('base_personalized.html', allCats =  allCats, database = DATABASE)

@app.route('/changeView/', methods = ['POST'])
def changeView():
    allCats = p3.getCats()
    timeSelection = request.form['time']
    dataSelection = request.form['views']
    rightpanel = "View: " + str(timeSelection) + " " + str(dataSelection)
    print("got here")
    return render_template('base_personalized.html', allCats =  allCats, rightPanel = rightpanel, database = DATABASE)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
