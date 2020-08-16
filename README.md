# Reader's Cabin

## Visit the website : https://readerscabin.herokuapp.com/

Reader's Cabin is a book review website in which users will be able to search for books, leave reviews for individual books and see ratings of books from a broader audience. but first user must register and login in order to access the library.
For developers, reader's cabin has a feature to let users query for book details and book reviews programmatically via my website's API.

:arrow_forward: &nbsp; **View Live Demo [here](https://www.youtube.com/watch?v=LCDnNLaenv0)**

## How to use this app 

1. Clone this repositiory or Download Source files

2. Run the command in your terminal/CMD window to make sure that all of the necessary Python packages (Flask and SQLAlchemy, for instance) are installed.

    ```bash
    pip install -r requirements.txt
    ```

3. Set an environmental variable to connect with database.
Varialbe name must be: "DATABASE_URL"
Varialbe value will be: "...your database uri ...", example: postgres://username:password@hostname/database

    ```bash
    export DATABASE_URL=""
    ```

4. Run python imports.py to create user,books and reveiws table in database and to insert 5000 books data from books.csv

    ```bash
    python3 imports.py
    ```

5. Run python application.py to run the app.

    ```bash
    python3 application.py
    ```

## Files

#### app.py

This file contains the backend of the website.

#### send_mail.py
This file is used to connect to mailtrap.io for the contact information.

#### import.py

This file contains the code to insert the books from the CSV file to the database.

#### requirements.txt

This file contains all the packages necessary to run this project.

#### Templates Folder

This folder contains all the HTML files.

#### Static Folder

This folder contains the css and img folders.

## Technologies used

* HTML
* CSS
* Sass
* Bootstrap
* Git
* Flask
* SQLAlchemy
* Postgresql

## API

Goodreads api is used in this website to access the review data for individual books.

<br>

### Contribute

Contributions are always welcome! Please create a PR to contribute.

### :pencil: License

This project is licensed under [MIT](https://opensource.org/licenses/MIT) license.

### :man_astronaut: Show your support

Give a ⭐️ if this project helped you!
