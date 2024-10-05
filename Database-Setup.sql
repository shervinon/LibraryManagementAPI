create database library;
use library;
create table books 
(
	id int auto_increment primary key,
    title varchar(255) not null,
    author varchar(255) not null,
    is_borrowed boolean default false,
    borrowed_by int default null
);
create table users
(
	id int auto_increment primary key,
    name varchar(255) not null
);