
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
    dropCats = p3.getCats()
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    return render_template('base_personalized.html', allCats =  allCats, add_dropdown = dropCats , database = DATABASE)

# routing for adding a category
#todo: add error handling for if catName not unique, add a better way to select a color
@app.route('/addCat/', methods = ['POST'])
def addCat():
    name = request.form['catName']
    color = request.form['catColor']
    p3.addCat(name,color)
    allCats = p3.getCats()
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    return render_template('base_personalized.html', allCats =  allCats, database = DATABASE)

@app.route('/addTask/', methods = ['POST'])
def addTask():
    allCats = p3.checkcat()#p3.getCats()
    isFinished = 0#default:not finished
    taskName = request.form['catName']#should we change the name of this varchar
    userID = 1#currently hard coded, need to change once we have the login page
    start = request.form['startDate']
    end = request.form['endDate']
    p3.addTask(isFinished,userID,taskName,start,end)
    parID = p3.checkTaskID(taskName,start,end)['taskID']
    numSubtask = int(request.form['num'])
    for i in range(1,numSubtask+1):
            sub = request.form['subtask'+str(i)]
            if sub.split()!=[]:
                print 'subTask'+str(i)
                p3.addTask(isFinished,userID,sub,start,end)
                childID = p3.checkTaskID(sub,start,end)['taskID']
                p3.addSubtask(userID,parID,childID)
    # dropdowns = p3.buildDropdown(request.form['time'],request.form['views'])
    return render_template('base_personalized.html', allCats =  allCats, database = DATABASE)

@app.route('/changeView/', methods = ['POST'])
def changeView():
    allCats = p3.getCats()
    timeSelection = request.form['time']
    dataSelection = request.form['views']
    rightpanel = "View: " + str(timeSelection) + " " + str(dataSelection)
    dropdowns = p3.buildDropdown(timeSelection,dataSelection)
    print("got here")
    return render_template('base_personalized.html', allCats =  allCats, timeSelect1 = dropdowns, rightPanel = rightpanel, database = DATABASE)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
