# Introduction

Facebook now allows you to download a copy of your Facebook information. Included in this is all of the messages you've sent through Facebook and Messenger.  This project will allow you to take the messages you download from Facebook, and put them in a MySQL database that you can run queries on.

# Requirements

* Python 3.6
* [mysql-connector](https://www.mysql.com/products/connector/) - I think you can get this through a stand-alone download or through pip.
* An empty MySQL database.

# Setting Up

1. First step is to get a copy of your Facebook messages.  

    `Facebook.com -> Settings -> Your Facebook Information -> Download Your Information`

	Make sure to download as JSON

2. Next, set up your database that the messenging data will go into.  I'm leaving it up to you to set up the server and DB accounts that you will use.  Once you have a blank database set up, you can run the `CreateDB.sql` script which will creat all the tables, columns, and starting data that you will need.

	You can also open `FB2SQL.xml` in [draw.io](https://www.draw.io/) to get a diagram of the database.

	NOTE: The MediaTypes table is the only table that needs to be prepopulated (this is in the createDB script):
	```
	INSERT INTO `MediaType` (`ID`, `Type`) VALUES
	(1, 'photos'),
	(2, 'gifs'),
	(3, 'videos'),
	(4, 'thumbnail'),
	(5, 'audio_files'),
	(6, 'sticker'),
	(7, 'files');
	```

# Running The Script