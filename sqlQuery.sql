drop table if exists category;
drop table if exists event;
drop table if exists logEntry;
drop table if exists taskList;
drop table if exists user;

Create table user(
	userID int auto_increment,
	psswd varchar(50),
	Index (userID),
	Primary key(userID)
) ENGINE = InnoDB;


Create table category(
	name varchar(50),
	catID int,
	INDEX(catID),
	color varchar(50)
) ENGINE = InnoDB;


Create table event(
	eventID int,
	userID int,
	Index (eventID),
	start date,
	end date,
	name varchar(50),
	foreign key (userID) references user(userID)
) ENGINE = InnoDB;

Create table logEntry(
	taskID int,
	hours int,
	userID int,
	taskDate date,
	Foreign key (userID) references user(userID)
) ENGINE = InnoDB;

Create table taskList(
	isFinished boolean,
	userID int,
parentTaskID int,
	subTaskID int,
	Start date,
	End date,
	Foreign key (userID) references user(userID)
)ENGINE = InnoDB;
