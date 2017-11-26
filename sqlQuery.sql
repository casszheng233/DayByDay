drop table if exists category;
drop table if exists event;
drop table if exists logEntry;
drop table if exists task;
drop table if exists taskList;
drop table if exists user;

Create table user(
	userID int not null auto_increment,
	psswd varchar(50),
	Index (userID),
	Primary key(userID)
) ENGINE = InnoDB;


Create table category(
	name varchar(50) not null,
	color varchar(50),
	primary key(name)
) ENGINE = InnoDB;


Create table event(
	eventID int auto_increment,
	userID int,
	INDEX (eventID),
	start date,
	end date,
	name varchar(50),
	primary key(eventID),
	foreign key(userID) references user(userID)
) ENGINE = InnoDB;

Create table logEntry(
	taskID int,
	hours int,
	userID int,
	taskDate date,
	Foreign key (userID) references user(userID)
) ENGINE = InnoDB;

create table task(
	isFinished boolean,
	userID int,
	taskName varchar(50),
	taskID int auto_increment,
	INDEX (taskID),
	start date,
	`end` date,
	primary key(taskID),
	foreign key (userID) references user(userID)
)ENGINE = InnoDB;


create table taskList(
	userID int,
	parentTaskID int,
	subTaskID int,
	foreign key(userID) references user(userID),
	foreign key(parentTaskID) references task(taskID),
	foreign key(subTaskID) references task(taskID)
)ENGINE = InnoDB;
