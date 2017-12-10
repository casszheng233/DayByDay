drop table if exists event;
drop table if exists logEntry;
drop table if exists taskList;
drop table if exists task;
drop table if exists user;
drop table if exists category;

Create table user(
	userID int not null auto_increment,
	psswd varchar(50),
	Index (userID),
	Primary key(userID)
) ENGINE = InnoDB;


Create table category(
	name varchar(50) not null,
	color varchar(50),
	userID int,
	primary key(name),
	foreign key(userID) references user(userID)
) ENGINE = InnoDB;


Create table event(
	eventID int auto_increment,
	userID int,
	INDEX (eventID),
	eventDate date not null,
	start time not null,
	end time not null,
	name varchar(50) not null,
	primary key(eventID),
	foreign key(userID) references user(userID)
) ENGINE = InnoDB;

Create table logEntry(
	name varchar(50),
	hours int,
	userID int,
	taskDate date not null,
	Foreign key (name) references category(name)
) ENGINE = InnoDB;

create table task(
	isFinished boolean,
	userID int,
	taskName varchar(50),
	taskID int auto_increment,
	INDEX (taskID),
	start date not null,
	`end` date not null,
	name varchar(50),
	primary key(taskID),
	foreign key (name) references category(name),
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
