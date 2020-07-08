import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# set the database url inside the quotes using this command
# $ export DATABASE_URL=""
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

print("Creating tables")
# creating books table
db.execute(""" CREATE TABLE books ( 
    id SERIAL NOT NULL, 
    isbn varchar(100) NOT NULL, 
    title varchar (100) NOT NULL, 
    author varchar(100) NOT NULL, 
    year integer NOT NULL, 
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (isbn) )  """)

print('books table created')


# creating users table
db.execute(""" CREATE TABLE users (
    id SERIAL NOT NULL,
    name varchar(100) NOT NULL, 
    email varchar(100) NOT NULL,
    username varchar(100) NOT NULL,
    password varchar(100) NOT NULL,
    PRIMARY KEY (username));  """)

print('users table created')


# creating reviews table
db.execute(""" CREATE TABLE reviews (
    username varchar(100) NOT NULL, 
    rating integer NOT NULL, 
    comment varchar(1200) NOT NULL, 
    isbn varchar(100) NOT NULL, 
    date DATE NOT NULL DEFAULT CURRENT_DATE) ;  """)

print('reviews table created')


i = 1  # variable to count the number of book

f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    if title == "title":
        continue
    else:
        db.execute(" INSERT INTO books (isbn, title, author, year ) VALUES (:a, :b, :c, :d)", {
                   'a': isbn, 'b': title, 'c': author, 'd': year})
        print(f"{i} books added")
        i = i + 1

db.commit()
