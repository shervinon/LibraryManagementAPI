create database library;
use library;
create table users
(
	id int auto_increment primary key,
    name varchar(255) not null
);
create table books 
(
	id int auto_increment primary key,
    title varchar(255) not null,
    author varchar(255) not null,
    is_borrowed boolean default false,
    borrowed_by int default null,
    borrowed_start_date DATE NULL,
    borrowed_end_date DATE NULL,
    foreign key (borrowed_by) references users(id)
);
create table categories 
(
    id int auto_increment primary key,
    name varchar(255) not null unique
);
create table book_categories 
(
    book_id int,
    category_id int,
    primary key (book_id, category_id),
    foreign key (book_id) references books(id) on delete cascade,
    foreign key (category_id) references categories(id) on delete cascade
);
