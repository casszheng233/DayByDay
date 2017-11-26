
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




if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',os.getuid())
