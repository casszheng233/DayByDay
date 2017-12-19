//Ajax Calls (and pulseMessage) -----------------------------------------------------------------------------------------------------

//displays message in sidebar showing confirmation of success (in blue)
//or alerting users to errors (in red)
function pulseMessage(text, color){
  $('#pulseMessages').css({'color': color, 'border-color': color});
  $("#pulseMessages").text(text);
  $('#pulseMessages').finish().show().delay(2000).fadeOut("slow");
}

//ajax call for selecting a new view in the two dropdowns
function changeView(){
  $.ajax({
			url: '/changeView/',
			data: $("#changeViewForm").serialize(),
			type: 'POST',
			success: function(data){
        timeChoice = Cookies.get('timeChoice');
        dataChoice = Cookies.get('dataChoice');

        //create views for checklist, if user is at a checklist-view
        if (dataChoice == "checklist"){
          dataStruct = JSON.parse(data.replace(/'/g,'"'));
          if (timeChoice == "day"){
            packagedTaskDay(dataStruct);
          } else if (timeChoice == "week"){
            packagedTaskWeek(dataStruct);
          } else if (timeChoice == "month"){
            packagedTaskMonth(dataStruct);
          }
        }

        //create views for events, if user is at a event-view
        if (dataChoice == "events"){
          dataStruct = JSON.parse(data.replace(/'/g,'"'));
          if (timeChoice == "day"){
            packagedEventDay(dataStruct);
          } else if (timeChoice == "week"){
            packagedEventWeek(dataStruct);
          } else if (timeChoice == "month"){
            packagedEventMonth(dataStruct);
          }
        }

        //create views for log, if user is at a log-view
        if (dataChoice == "log"){
          dataStruct = data;
          if (timeChoice == "day"){
            packagedLogDay(dataStruct[0],dataStruct[3]);
          } else if (timeChoice == "week"){
            packagedLogDay(dataStruct[1],dataStruct[3]);
          } else if (timeChoice == "month"){
            packagedLogDay(dataStruct[2],dataStruct[3]);
          }
        }
				pulseMessage("Swish, changed!","#418ACA");
			},
			error: function(error){
				console.log(error);
			}
		});
}

//ajax call for ticking a category box in sidebar. Similar to the above changeView() function
function catTick(){
  $.ajax({
			url: '/tickedCats/',
			data: $("#catTickForm").serialize(),
			type: 'POST',
			success: function(data){

        if (data.error){
          pulseMessage(data.error,'#D9534E');
          return;
        }

        timeChoice = Cookies.get('timeChoice');
        dataChoice = Cookies.get('dataChoice');

        if (dataChoice == "checklist"){
          dataStruct = JSON.parse(data.replace(/'/g,'"'));
          if (timeChoice == "day"){
            packagedTaskDay(dataStruct);
          } else if (timeChoice == "week"){
            packagedTaskWeek(dataStruct);
          } else if (timeChoice == "month"){
            packagedTaskMonth(dataStruct);
          }
        }

        if (dataChoice == "events"){
          dataStruct = JSON.parse(data.replace(/'/g,'"'));
          if (timeChoice == "day"){
            packagedEventDay(dataStruct);
          } else if (timeChoice == "week"){
            packagedEventWeek(dataStruct);
          } else if (timeChoice == "month"){
            packagedEventMonth(dataStruct);
          }
        }

        if (dataChoice == "log"){
          dataStruct = data;
          if (timeChoice == "day"){
            packagedLogDay(dataStruct[0],dataStruct[3]);
          } else if (timeChoice == "week"){
            packagedLogDay(dataStruct[1],dataStruct[3]);
          } else if (timeChoice == "month"){
            packagedLogDay(dataStruct[2],dataStruct[3]);
          }
        }

				pulseMessage("Bam, changed!","#418ACA");
			},
			error: function(error){
				console.log(error);
			}
		});
}

//ajax call for checking a task checkbox
function tickTaskCall(taskID){
  $.ajax({
			url: '/tickTask/',
			data: $("#taskForm" + taskID).serialize(),
			type: 'POST',
			success: function(response){
				pulseMessage("Success","#418ACA");
			},
			error: function(error){
				console.log(error);
			}
		});
}

//ajax call for submitting new category
$(function(){
  $('#addCategorySubmit').click(function(){
    $.ajax({
      url: '/addCat/',
      data: $("#addCategory").serialize(),
      type: 'POST',
      success: function(data){

        //reset accordion
        $('#collapseOne').collapse('hide');
        $('#addCategory')[0].reset();
        $(".selectpicker").selectpicker("refresh");

        //check for errors, and pulse them if they exist
        if (data.error){
          pulseMessage(data.error,'#D9534E');
          return;
        }
        pulseMessage("Category Added","#418ACA");

        //update other form dropdowns
        $('.canUpdateCat').append('<option value="'+data.catName+'">'+data.catName+'</option>');

        //add new category + checkbox
        var line1 = '<div class="pretty p-default p-curve">';
        var line2 = '<input type="checkbox" class = "cat" name="cat" id = "cat'+data.catName+'" onchange="checkCat(this,true); this.form.submit();" value="'+data.catName+'" />';
        var line3 = '<div class="state '+data.catColor+' generatedCat">';
        var line4 = '<label><font color=" '+data.catColor+'  "> '+data.catName+'  </font></label>';
        var line5 = '</div></div><br>';
        $('#catTickForm').append(line1 + line2 + line3 + line4 + line5);

      },
      error: function(error){
        console.log(error);
      }
    });
  });
});

//ajax call for submitting new task
$(function(){
  $('#addTaskSubmit').click(function(){
    $.ajax({
      url: '/addTask/',
      data: $("#addTask").serialize(),
      type: 'POST',
      success: function(data){

        //reset accordion
        $('#collapseTwo').collapse('hide');
        $('#addTask')[0].reset();
        $('#datetimepicker6').data().DateTimePicker.date(null);
        $('#datetimepicker7').data().DateTimePicker.date(null);
        $(".selectpicker").selectpicker("refresh");
        $('#subtasks').empty();

        //error checking and pulsing
        if (data.error){
          pulseMessage(data.error,'#D9534E');
          return;
        }
        pulseMessage("Task Added","#418ACA");

        timeChoice = Cookies.get('timeChoice');
        dataChoice = Cookies.get('dataChoice');

        //get JSON from backend
        dataStruct = JSON.parse(data.replace(/'/g,'"'));

        //update tasks in the view
        if (dataChoice == "checklist"){
          if (timeChoice == "day"){
            packagedTaskDay(dataStruct);
          } else if (timeChoice == "week"){
            packagedTaskWeek(dataStruct);
          } else if (timeChoice == "month"){
            packagedTaskMonth(dataStruct);
          }
        }
      },
      error: function(error){
        console.log(error);
      }
    });
  });
});


//ajax call for submitting new log entry
$(function(){
  $('#addLogSubmit').click(function(){
    $.ajax({
      url: '/addLog/',
      data: $("#addLog").serialize(),
      type: 'POST',
      success: function(data){

        //reset accordion
        $('#collapseThree').collapse('hide');
        $('#addLog')[0].reset();
        $('#datetimepicker1').data().DateTimePicker.date(null);
        $(".selectpicker").selectpicker("refresh");
        $('#hours').empty();

        //error checking/pulsing
        if (data.error){
          pulseMessage(data.error,'#D9534E');
          return;
        }
        pulseMessage("Entry Added","#418ACA");

        timeChoice = Cookies.get('timeChoice');
        dataChoice = Cookies.get('dataChoice');

        var logDicDay = data[0];
        var logDicWeek = data[1];
        var logDicMonth = data[2];
        var colorDic = data[3];

        //update tasks in the view
        if (dataChoice == "log"){
          if (timeChoice == "day"){
            packagedLogDay(logDicDay,colorDic);
          } else if (timeChoice == "week"){
            packagedLogWeek(logDicWeek,colorDic);
          } else if (timeChoice == "month"){
            packagedLogMonth(logDicMonth,colorDic);
          }
        }
      },
      error: function(error){
        console.log(error);
      }
    });
  });
});


//ajax call for submitting new event
$(function(){
  $('#addEventSubmit').click(function(){
    $.ajax({
      url: '/addEvent/',
      data: $("#addEvent").serialize(),
      type: 'POST',
      success: function(data){

        //reset accordion
        $('#collapseFour').collapse('hide');
        $('#addEvent')[0].reset();

        //error checking and pulsing
        if (data.error){
          pulseMessage(data.error,'#D9534E');
          return;
        }
        pulseMessage("Event Added","#418ACA");

        timeChoice = Cookies.get('timeChoice');
        dataChoice = Cookies.get('dataChoice');

        dataStruct = JSON.parse(data.replace(/'/g,'"'));

        //update tasks in the view
        if (dataChoice == "events"){
          if (timeChoice == "day"){
            packagedEventDay(dataStruct);
          } else if (timeChoice == "week"){
            packagedEventWeek(dataStruct);
          } else if (timeChoice == "month"){
            packagedEventMonth(dataStruct);
          }
        }
      },
      error: function(error){
        console.log(error);
      }
    });
  });
});



//Helper Functions for Ajax calls -----------------------------------------------------------------------------------------------------

//Log-related helpers----------------------------------------------------------

//helps clean data for graph
function translatePoints(raw){
  var result = [];
  for (i = 0; i < raw.length; i++){
    rec = raw[i];
    result.push({ x: new Date(rec[0],rec[1]-1,rec[2]), y: rec[3] });
  }
  return result;
}

//pushes the dataPoints of a new category to the existing data
function makeData(dataList,catName,dataPoints,color){
  var eachData = {
        type: "line",
        showInLegend: true,
        lineThickness: 2,
        name: catName,
        markerType: "square",
        color: '#'+color,
        dataPoints : dataPoints
      };
  dataList.push(eachData);
}

function packagedLogDay(allLogRec,colorDic){
  $('#container2').empty();
  $("#container2").append('<div id="chartContainer" style="height: 80%; width: 90%;"></div>');
  var catChoiceDic = catCookies();
  var catList = []; //catList is a list of selected categories
  for (k in catChoiceDic){
    if (catChoiceDic[k]==true){
      catList.push(k);
    }
  }
  dataRec = [];
  intervalGap = 1;
  intType = 'day';
  dateFormat = "MMM/DD/YYYY"

  for (var j = 0 ; j <catList.length; j++){ //construct data for each category
    var actualCat = catList[j].substring(3); //the previous form is 'catXXX', and we are only interested in XXX
    if (actualCat in allLogRec){
      var dataPoints = translatePoints(allLogRec[actualCat]); //prepare data
      makeData(dataRec,actualCat,dataPoints,colorDic[actualCat]); //append it to our current data list
    }
  }
	var data = dataRec;
	var gap = intervalGap;
	var viewFormat = dateFormat;

		var chart = new CanvasJS.Chart("chartContainer", {
			title: {
				text: "Log View",
				fontSize: 30
			},
			animationEnabled: true,
			axisX: {
				gridColor: "Silver",
				tickColor: "silver",
				interval:gap,
				intervalType: intType,
				valueFormatString: viewFormat//"DD/MMM/YYYY"
			},
			toolTip: {
				shared: true
			},
			theme: "theme2",
			axisY: {
				gridColor: "Silver",
				tickColor: "silver"
			},
			legend: {
				verticalAlign: "center",
				horizontalAlign: "right"
			},
			data:data,//data is prepared by the helper function
			legend: {
				cursor: "pointer",
				itemclick: function (e) {
					if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
						e.dataSeries.visible = false;
					}
					else {
						e.dataSeries.visible = true;
					}
					chart.render();
				}
			}
		});

		chart.render();
}

function packagedLogWeek(allLogRec,colorDic){
  $('#container2').empty();
  $("#container2").append('<div id="chartContainer" style="height: 300px; width: 100%;"></div>');

  var catChoiceDic = catCookies();
  var catList = [];//catList is a list of selected categories
  for (k in catChoiceDic){
    if (catChoiceDic[k]==true){
      catList.push(k);
    }
  }
  dataRec = [];
  intervalGap = 7;
  intType = 'day';
  dateFormat = "MMM/DD/YYYY"

  for (var j = 0 ; j <catList.length; j++){//construct data for each category
    var actualCat = catList[j].substring(3);//the previous form is 'catXXX', and we are only interested in XXX
    if (actualCat in allLogRec){
      var dataPoints = translatePoints(allLogRec[actualCat]);//prepare data
      makeData(dataRec,actualCat,dataPoints,colorDic[actualCat]);//append it to our current data list
    }

  }
	var data = dataRec;
	var gap = intervalGap;
	var viewFormat = dateFormat;

		var chart = new CanvasJS.Chart("chartContainer", {
			title: {
				text: "Log View",
				fontSize: 30
			},
			animationEnabled: true,
			axisX: {
				gridColor: "Silver",
				tickColor: "silver",
				interval:gap,
				intervalType: intType,
				valueFormatString: viewFormat//"DD/MMM/YYYY"
			},
			toolTip: {
				shared: true
			},
			theme: "theme2",
			axisY: {
				gridColor: "Silver",
				tickColor: "silver"
			},
			legend: {
				verticalAlign: "center",
				horizontalAlign: "right"
			},
			data:data,//data is prepared by the helper function
			legend: {
				cursor: "pointer",
				itemclick: function (e) {
					if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
						e.dataSeries.visible = false;
					}
					else {
						e.dataSeries.visible = true;
					}
					chart.render();
				}
			}
		});
		chart.render();
}


function packagedLogMonth(allLogRec,colorDic){
  $('#container2').empty();
  $("#container2").append('<div id="chartContainer" style="height: 300px; width: 100%;"></div>');

  var catChoiceDic = catCookies();
  var catList = [];//catList is a list of selected categories
  for (k in catChoiceDic){
    if (catChoiceDic[k]==true){
      catList.push(k);
    }
  }
  dataRec = [];
  intervalGap = 1;
  intType = 'month';
  dateFormat = "MMM/YYYY"

  for (var j = 0 ; j <catList.length; j++){//construct data for each category
    var actualCat = catList[j].substring(3);//the previous form is 'catXXX', and we are only interested in XXX
    if (actualCat in allLogRec){
      var dataPoints = translatePoints(allLogRec[actualCat]);//prepare data
      makeData(dataRec,actualCat,dataPoints,colorDic[actualCat]);//append it to our current data list
    }

  }
	var data = dataRec;
	var gap = intervalGap;
	var viewFormat = dateFormat;

		var chart = new CanvasJS.Chart("chartContainer", {
			title: {
				text: "Log View",
				fontSize: 30
			},
			animationEnabled: true,
			axisX: {
				gridColor: "Silver",
				tickColor: "silver",
				interval:gap,
				intervalType: intType,
				valueFormatString: viewFormat//"DD/MMM/YYYY"
			},
			toolTip: {
				shared: true
			},
			theme: "theme2",
			axisY: {
				gridColor: "Silver",
				tickColor: "silver"
			},
			legend: {
				verticalAlign: "center",
				horizontalAlign: "right"
			},
			data:data,//data is prepared by the helper function
			legend: {
				cursor: "pointer",
				itemclick: function (e) {
					if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
						e.dataSeries.visible = false;
					}
					else {
						e.dataSeries.visible = true;
					}
					chart.render();
				}
			}
		});
		chart.render();
}

//Task-related helpers----------------------------------------------------------

function getMyDate(){
  var today = new Date(),
      d = today.getDate(),
      m = today.getMonth()+1,
      y = today.getFullYear();
  var date = y + "," + m + "," + d;
  return date;
}

//set container2 to have the most recent task-day data
function packagedTaskDay(dataStruct){
  var date = getMyDate();
  $('#container2').empty();

  var catChoiceDic = catCookies();

  function placeSubtasksHelper(taskDic, isParent){
    if (taskDic["end"].toString() == date){
      buildTask(taskDic["taskID"], taskDic["catColor"], taskDic["cat"], taskDic["name"], taskDic["isFinished"].toString(), isParent, "container2", "day");
    }
  }

  //process data structure of all tasks to find which dates to display
  function placeSubtasks(dataStruct){
    //Extract parent task from data structure for processing
    for (j=0; j < dataStruct.length; j++ ){
      taskDic = dataStruct[j][0];
      placeSubtasksHelper(taskDic, true);

      //Extract child subTasks from data structure for processing
      for (i=0; i < dataStruct[j][1].length; i++){
          taskDic = dataStruct[j][1][i];
          if (Object.keys(taskDic).length != 0){
            placeSubtasksHelper(taskDic, false);
        }
      }
    }
  }
  placeSubtasks(dataStruct);
}

//set container2 to have the most recent task-week data
function packagedTaskWeek(dataStruct){
  var date = getMyDate();
  $('#container2').empty();
  var catChoiceDic = catCookies();

    initializeWeekTable("Tasks");

    //for one task from the data structure, if the date on task matches a date to be displayed,
    //create the task in the corresponding slot of the week table
    function placeSubtasksHelper (j, dataStruct, date, selector){

      //makes sure task's due date is the same as the relevant date
      function placer(taskDic, isParent, selector){
        if (taskDic["end"].toString() == date){
          buildTask(taskDic["taskID"], taskDic["catColor"], taskDic["cat"], taskDic["name"], taskDic["isFinished"].toString(), isParent, selector, "week");
        }
      }

      //executes placing for both parent tasks and subtasks
      taskDic = dataStruct[j][0];
      placer(taskDic, true, selector);
      for (i=0; i < dataStruct[j][1].length; i++){
          taskDic = dataStruct[j][1][i];
          if (Object.keys(taskDic).length != 0){
            placer(taskDic,false, selector);
          }
      }
    }

    //iterate through all tasks and place them in the relevant week
    function placeSubtasks(dataStruct){
      var week = defineWeek(new Date());

      //iterate through all tasks
      for (j=0; j < dataStruct.length; j++ ){

        placeSubtasksHelper(j, dataStruct, week[0], week[0].split(',')[2]);
        placeSubtasksHelper(j, dataStruct, week[1], week[1].split(',')[2]);
        placeSubtasksHelper(j, dataStruct, week[2], week[2].split(',')[2]);
        placeSubtasksHelper(j, dataStruct, week[3], week[3].split(',')[2]);
        placeSubtasksHelper(j, dataStruct, week[4], week[4].split(',')[2]);
        placeSubtasksHelper(j, dataStruct, week[5], week[5].split(',')[2]);
        placeSubtasksHelper(j, dataStruct, week[6], week[6].split(',')[2]);

        //why is this not working?
        // for (i=0; i < 7; i++){
        //   //for each task, check whether it falls into any day of the week we're displaying
        //   placeSubtasksHelper(j, dataStruct, week[i], week[i].split(',')[2]);
        // }

      }
    }
    placeSubtasks(dataStruct);
}

//set container2 to have the most recent task-month data
function packagedTaskMonth(dataStruct){

  var date = getMyDate();
  $('#container2').empty();
  var catChoiceDic = catCookies();

  initializeMonthTable("Tasks");

  //for one task from the data structure, if the date on task matches a date to be displayed,
  //create the task in the corresponding slot of the week table
  function placerHelper (j, dataStruct, date, selector){

    //makes sure task's due date is the same as the relevant date, and builds task
    function placer(taskDic, isParent, selector){
      if (taskDic["end"].toString() == date){
        var hi = 0;
        buildTask(taskDic["taskID"], taskDic["catColor"], taskDic["cat"], taskDic["name"], taskDic["isFinished"].toString(), isParent, selector, "month");
      }
    }

    //executes placing for both parent tasks and subtasks
    taskDic = dataStruct[j][0];
    placer(taskDic, true, selector);
    for (i=0; i < dataStruct[j][1].length; i++){
        taskDic = dataStruct[j][1][i];
        if (Object.keys(taskDic).length != 0){
          placer(taskDic,false, selector);
        }
    }
  }

  // create the weeks of the month
  var aWeek = defineMonth();
  oneWeek(aWeek[0], "Tasks", dataStruct, placerHelper);
  oneWeek(aWeek[1], "Tasks", dataStruct, placerHelper);
  oneWeek(aWeek[2], "Tasks", dataStruct, placerHelper);
  oneWeek(aWeek[3], "Tasks", dataStruct, placerHelper);
  oneWeek(aWeek[4], "Tasks", dataStruct, placerHelper);
  oneWeek(aWeek[5], "Tasks", dataStruct, placerHelper);
}

//Event-related helpers----------------------------------------------------------

//set container2 to have the most recent event-day data
function packagedEventDay(dataStruct){
  var date = getMyDate();
  $('#container2').empty();

  //process data structure of all tasks to find which dates to display
  function placeEvent(dataStruct){
    //Extract parent task from data structure for processing
    for (j=0; j < dataStruct.length; j++ ){
      eventDic = dataStruct[j]
      if (eventDic["eventDate"].toString() == date){
        s=''+date[0]+'/'+date[1]+'/'+date[2]
        buildEvent(eventDic["eventID"], eventDic["eventName"], s,eventDic["startTime"], eventDic["endTime"], "container2", "day");
      }
    }
  }
  placeEvent(dataStruct);
}

//set container2 to have the most recent event-week data
function packagedEventWeek(dataStruct){
    var date = getMyDate();
    $('#container2').empty();

    initializeWeekTable("Events");

    //for one event from the data structure, if the date on event matches a date to be displayed,
    //create the event in the corresponding slot of the week table
    function placeDayJ (j, dataStruct, date, selector){
      eventDic = dataStruct[j]
      if (eventDic["eventDate"].toString() == date){
        buildEvent(eventDic["eventID"], eventDic["eventName"], eventDic["eventDate"], eventDic["startTime"], eventDic["endTime"],  selector, "week");
      }
    }

    //iterate through all events and place them in the relevant week
    function placeEvents(dataStruct){
      var week = defineWeek(new Date());

      //iterate through all events
      //put in for loop later
      for (j=0; j < dataStruct.length; j++ ){
        placeDayJ(j, dataStruct, week[0], week[0].split(',')[2]);
        placeDayJ(j, dataStruct, week[1], week[1].split(',')[2]);
        placeDayJ(j, dataStruct, week[2], week[2].split(',')[2]);
        placeDayJ(j, dataStruct, week[3], week[3].split(',')[2]);
        placeDayJ(j, dataStruct, week[4], week[4].split(',')[2]);
        placeDayJ(j, dataStruct, week[5], week[5].split(',')[2]);
        placeDayJ(j, dataStruct, week[6], week[6].split(',')[2]);
      }
    }
    placeEvents(dataStruct);
}

//set container2 to have the most recent event-month data
function packagedEventMonth(dataStruct){
  var date = getMyDate();
  $('#container2').empty();

  initializeMonthTable("Events");

  // if date on event matches given date, build the event
  function placerHelper (j, dataStruct, date, selector){
    eventDic = dataStruct[j]
    if (eventDic["eventDate"].toString() == date){
      buildEvent(eventDic["eventID"], eventDic["eventName"], eventDic["eventDate"], eventDic["startTime"], eventDic["endTime"],  selector, "month");
    }
  }

  // create the weeks of the month
  var thing = defineMonth();
  oneWeek(thing[0], "Events", dataStruct, placerHelper);
  oneWeek(thing[1], "Events", dataStruct, placerHelper);
  oneWeek(thing[2], "Events", dataStruct, placerHelper);
  oneWeek(thing[3], "Events", dataStruct, placerHelper);
  oneWeek(thing[4], "Events", dataStruct, placerHelper);
  oneWeek(thing[5], "Events", dataStruct, placerHelper);
}

// Task and Event Functions (mostly related to date handling) ----------------------------------------------------------------------------------------

//find today
function findToday(){
  var today = new Date(),
      d = today.getDate(),
      m = today.getMonth()+1,
      y = today.getFullYear();
  var date = y + "," + m + "," + d;

  var month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

  $('#headerright').append("Today is: " + month_names[m-1] + " " + d + ", " + y);
  return date;
}

//given a date, returns array of current week's dates in format YYYY,MM,DD for comparison to SQL values
//Defines a week as last Sunday to Saturday.
function defineWeek(date){
  var sunday = date;
  sunday.setDate(sunday.getDate() - sunday.getDay());

  //add Sunday
  dStr = sunday.toLocaleDateString().split('/');
  week = [dStr[2] + ',' + dStr[0] + ',' + dStr[1]];

  //add rest of week
  for (i = 1; i < 7; i++){
    d = new Date(sunday.getTime() + 86400000*i); //robust against end-of-month changes
    dStr = d.toLocaleDateString().split('/');
    week.push(dStr[2] + ',' + dStr[0] + ',' + dStr[1] );
  }
  return week;
}


//formats week names for display in header
function formatWeekNames(){
  var week = defineWeek(new Date());
  var weeknames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]; //TODO: consider making current day name bold
  var displaynames = [];
  for (i = 0; i < 7; i++){
    var date = week[i].split(',');
    displaynames.push(weeknames[i] + " " + date[1] + "/" + date[2]);
  }
  return displaynames
}


// returns an array of date objects of the 1st of the month, the 8th of the month, etc, adding 7 days
// each time until reaching end of month
function defineMonth(){
  var date = new Date();
  var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
  var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);

  var weeks = [firstDay];
  for (i = 1; i < 6; i++){
    d = new Date(firstDay.getTime() + 7*86400000*i); //robust against end-of-month changes. TODO: daylights savings
    weeks.push(d);
  }
  return weeks;
}


//formats week names for display in header
function formatMonthWeekNames(date){
  var week = defineWeek(date);
  var displaynames = [];

  for (i = 0; i < 7; i++){
    var date = week[i].split(',');
    displaynames.push(date[1] + "/" + date[2]);
  }
  return displaynames
}


//Takes in "Tasks" or "Events" to create the appropriate week-table
function initializeWeekTable(viewSelection){
  //create table to seperate days of week into columns, and contain tasks
  $("#container2").append('<table style="width:100%;" id = "week'+ viewSelection +'" ></table>');
  $("#week"+ viewSelection +"").append('<tr id = "headers">  </tr>');

  //put days of week into header row
  displaynames = formatWeekNames();
  for (i = 0; i < 7; i++){
    var header = '<th class="text-center">' + displaynames[i] + '</th>';
    $("#headers").append(header);
  }

  //creates the row of table into which tasks or events will be placed
  var week = defineWeek(new Date());
  $("#week"+ viewSelection +"").append('<tr><td id = ' + week[0].split(',')[2] + ' style="vertical-align:top"> </td>' + //format with loop
                              '<td id = ' + week[1].split(',')[2] + ' style="vertical-align:top"> </td>' +
                              '<td id = ' + week[2].split(',')[2] + ' style="vertical-align:top"> </td>' +
                              '<td id = ' + week[3].split(',')[2] + ' style="vertical-align:top"> </td>' +
                              '<td id = ' + week[4].split(',')[2] + ' style="vertical-align:top"> </td>' +
                              '<td id = ' + week[5].split(',')[2] + ' style="vertical-align:top"> </td>' +
                              '<td id = ' + week[6].split(',')[2] + ' style="vertical-align:top"> </td>' +  '</tr>');
}


//Takes in "Tasks" or "Events" to create the appropriate month-table
function initializeMonthTable(viewSelection){
  //create table to seperate days of week into columns, and contain tasks
  $("#container2").append('<table style="width:100%; table-layout:fixed; border-collapse: collapse;" id = "week'+ viewSelection +'" ></table>')

  //put names of weekdays into header row
  $("#week"+ viewSelection + "").append('<tr id = headers>   </tr>');
  var weeknames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  for (i = 0; i < 7; i++){
    var header = '<th class = "text-center" style = "width: 10%;" >' + weeknames[i] + '</th>';
    $("#headers").append(header);
  }
}


// Takes in "Tasks" or "Events" to create one week, as a row, of a month table
// note that 'placerHelper' defines different methods in base_event_month and base_task_month
function oneWeek (date, viewSelection, dataStruct, placerHelper){
  var displayNames = formatMonthWeekNames(date);
  var current = new Date();
  var month = current.getMonth() + 1;
  var onlyCurrentMonth = displayNames.map((date) => { if (date.split('/')[0] != month){ return ' '; } else { return ('id = ' + date); }});
  displayNames = onlyCurrentMonth;

  // console.log(displayNames[0]); //really jank
  $("#week"+ viewSelection +"").append('<tr style ="height:130px;">' +
                              '<td class="text-center" ' + displayNames[0].replace("/","_") + ' style="vertical-align:top; border: 1px solid #F5F5F5; text-overflow: ellipsis;"> ' + displayNames[0].slice(-5) + ' </td>' +
                              '<td class="text-center" ' + displayNames[1].replace("/","_") + ' style="vertical-align:top; border: 1px solid #F5F5F5; text-overflow: ellipsis;"> ' + displayNames[1].slice(-5) + ' </td>' +
                              '<td class="text-center" ' + displayNames[2].replace("/","_") + ' style="vertical-align:top; border: 1px solid #F5F5F5; text-overflow: ellipsis;"> ' + displayNames[2].slice(-5) + ' </td>' +
                              '<td class="text-center" ' + displayNames[3].replace("/","_") + ' style="vertical-align:top; border: 1px solid #F5F5F5; text-overflow: ellipsis;"> ' + displayNames[3].slice(-5) + ' </td>' +
                              '<td class="text-center" ' + displayNames[4].replace("/","_") + ' style="vertical-align:top; border: 1px solid #F5F5F5; text-overflow: ellipsis;"> ' + displayNames[4].slice(-5) + ' </td>' +
                              '<td class="text-center" ' + displayNames[5].replace("/","_") + ' style="vertical-align:top; border: 1px solid #F5F5F5; text-overflow: ellipsis;"> ' + displayNames[5].slice(-5) + ' </td>' +
                              '<td class="text-center" ' + displayNames[6].replace("/","_") + ' style="vertical-align:top; border: 1px solid #F5F5F5; text-overflow: ellipsis;"> ' + displayNames[6].slice(-5) + ' </td>' +  '</tr>');

  var week = defineWeek(date);
  for (j=0; j < dataStruct.length; j++ ){
    for (w = 0; w < 7; w++){
      placerHelper(j, dataStruct, week[w], week[w].split(',')[1] + "_" + week[w].split(',')[2]);
    }
  }
}

// Task Functions -----------------------------------------------------------------------------------------------------

// get which categories user has checked in order to select
// certain categories of task for display
function catCookies(){
  catChoice = (Cookies.get('catChoice'));
  var catChoiceObj = "";
  if (catChoice){
    catChoiceObj = JSON.parse(catChoice);
  }
  catChoiceDic = {};
  for (i = 0; i < catChoiceObj.length; i ++){
    catChoiceDic[catChoiceObj[i][0].toString()] = catChoiceObj[i][1];
  }
  return catChoiceDic;
}

// TODO: toggling on completely done tasks
// IN PROGRESS: determining if all of a task's subtasks have been ticked
function areChildrenDone(){
  for (i = 0; i < dataStruct.length; i++){
      var subtasks = dataStruct[i][1];
      if (Object.keys(subtasks[0]).length != 0){
      let allDone = subtasks.reduce((result,taskDic) =>
          {return (taskDic['isFinished'] && (result))  }, true);
    }
  }
}

// build html for, and place into 'selector' one task
function buildTask(taskID, catColor, category, name, isFin, isParent, selector, timeChoice){
  // unless 'catall' has been ticked,
  if (!catChoiceDic["catall"]){
    // halt processing a task if that task's category was not ticked
    if (!catChoiceDic["cat" + category]){
     return;
    }
  }

  //determines whether checkbox should be rendered pre-checked
  finBool = "";
  if (parseInt(isFin)){
    finBool = " checked ";
  }

  //determines whether name of task should be rendered bold, indicating it is a parent
  nameParent = name;
  if (isParent){
    nameParent = "<b>" + name + "</b>";
  }
  nameParent = "<font color=" + catColor +  ">" + nameParent + "</font>";

  // building each form.
  // note: using the flask template double curly braces and url_for in the action causes errors
  $('#' + selector).append('<form id="taskForm'+taskID+'"  role="form">  <div class=task id=task' + taskID + ' >   </div></form>');

  // styling of panel
  var line0 =      '<div class="panel panel-default" style="width:95%; margin: 10px 2% 0 1%; border-width: 1px !important; border-style: solid !important; border-color:#'+ catColor +' !important;" > <div class="panel-body"><div class="pretty p-svg p-curve">';
  var line0month = '<div class="panel panel-default" style="width:95%; margin: 10px 2% 0 2%; border-width: 1px !important; border-style: solid !important; border-color:#'+ catColor +' !important;" > <div class="panel-body" style = "padding: 2px 0 !important"><div class="pretty p-svg p-curve">';

  //form items: hidden form values for backend processing, and the checkbox
  var line1 = "<input type='hidden' value='"+ timeChoice +"_checklist' name='timeSelector'>";
  var line2 = "<input type='hidden' value='task"+ taskID +"' name='taskCheck'>";
  // var line3 = "<input type='checkbox'"+ finBool +" onchange='this.form.submit();' name='taskCheck' value='task"+ taskID +"'/> ";
  var line3 = "<input class = 'taskTickbox' type='checkbox'"+ finBool +"onchange='tickTaskCall(" + taskID + ");' name='taskCheck' value='task"+ taskID +"'/> ";

  //styling of checkbox icon
  var colorDict = {'418ACA':'p-primary', '5DB85B':'p-success', 'F0AD4E':'p-warning', '5BC0DE':'p-info', 'D9534E':'p-danger'}
  var line4 = '<div class="state '+ colorDict[catColor] +'"><svg class="svg svg-icon" viewBox="0 0 20 20"><path d="M7.629,14.566c0.125,0.125,0.291,0.188,0.456,0.188c0.164,0,0.329-0.062,0.456-0.188l8.219-8.221c0.252-0.252,0.252-0.659,0-0.911c-0.252-0.252-0.659-0.252-0.911,0l-7.764,7.763L4.152,9.267c-0.252-0.251-0.66-0.251-0.911,0c-0.252,0.252-0.252,0.66,0,0.911L7.629,14.566z" style="stroke: white;fill:white;"></path></svg>';

  //passing of nameParent label and closing of all divs
  var line5 = '<label>'+ nameParent +'</label>';
  var line6 = '</div></div></div></div>';

  if (timeChoice == "month"){
    $("#task" + taskID.toString()).append(line0month + line1 + line2 + line3 + line4 + line5 + line6);
  } else {
    $("#task" + taskID.toString()).append(line0 + line1 + line2 + line3 + line4 + line5 + line6);
  }
}

//Event Function -----------------------------------------------------------------------------------------------------

// build html for, and place into 'selector' one event
function buildEvent(eventID, eventName, eventDate, startTime,endTime,selector, timeChoice){
  $('#' + selector).append('<div class=event id=event' + eventID + '> </div>');
  var line0 = '<div class="panel panel-default text-center" style="width:95%; margin: 10px 0 0 1%; border-width: 1px !important; border-style: solid !important; border-color:#418ACA !important;" > <div class="panel-body"><div class="pretty p-svg p-curve">';
  var line0month = '<div class="panel panel-default text-center" style="width:95%; margin: 10px 0 0 2%; border-width: 1px !important; border-style: solid !important; border-color:#418ACA !important;" > <div class="panel-body" style = "padding: 2px 0 !important"><div class="pretty p-svg p-curve">';

  var line1 = "<b>" + eventName + "</b> <br> " + startTime.slice(0,-3) + " to " + endTime.slice(0,-3);
  var line10 = '</div></div></div></div>';

  // note that month is formatted slightly differently
  if (timeChoice=='month'){
    line1 = "<b>" + eventName + "</b>";
    line0 = line0month;
  }

$("#event" + eventID.toString()).append( line0 + line1 + line10);
}
