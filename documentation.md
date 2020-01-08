# Code reusability
The code was made in the mindset that it can be broken apart and reused as well as having lots of option to change the behaviour of the program with little to no change to the initial code. For that reason we made several config files to be altered to adjust the program.

## Database Config
In the json file with as name CSV.specification.json you can define the data stored in the database by naming and defining the data type of each column in the database. The types INT, FLOAT, or STRING may be chosen at this time.
Additionally the database may be indexed to increase efficiency of filter actions by specifying a set of columns to index by. Such as streetname and house number to index by address. It is important that this is configured before you upload the database as the filtering of the database without this option is much slower.

As of now the config also contains a separate entry to configure the tooltip so that different attributes are shown when you hover the mousecursor over the data points.

## tb\_name.txt and mapboxtoken.txt
The mapboxtoken.txt and tb\_name.txt contain information about the currently used mapbox, the map that is shown, and the table name used from the database. These files only consist of one line, but are used throughout the program. Without these files you would have to change several lines to change the name of the database and a long line for the mapboxtoken which looks ugly in the initial code.

## Example data
The program was made to function well with the example dataset:
https://surfdrive.surf.nl/files/index.php/s/8C7TsZmoTUCZqXN

# Programming language used
The programming language is most likely the most important choice because it is the core foundation of the program and converting code from one language to another can be time consuming.
The most important deciding factor was the performance of the language.
We limited the potential programming languages to Python and R because these two languages where strongly preferred.
## Used Python
Python is similar to R and is a very abstract language so programming in it is not that difficult. This choice was made because it is faster than most abstract languages and has a big variety in packages available to use.

## Considered R
R is considered but nobody in the group has experience in R and we discovered that in most cases R is slower than python. R is a statistical language made for processing data, but because of the higher difficulty and possible slow performance we did not choose R.

## Others
Most other languages have a bigger learning curve or nobody in the group has any experience in the language at all. As going to a language with an extremely high learning curve was not preferred, we did not consider other languages even if they would be potentially faster
# Packages used
These are the python packages used for the program with reasons for using them followed by rejected alternatives:

## Map generator
Used for communication between the user and the server. For example the filtermenu.

### Used Dash
Dash is an open source package with the focus on performance which is one of the main points of the program. Most of the main functionalities were also present in the package and the website itself provided several nice examples which made us make this choice.

#### Plotly
As a part of Dash, it renders the map and data points. This is one of the most important aspects of dash because this will be responsible for rendering the map and placing down the data points from the .csv files.

### Considered Folium
Because Folium has similar functionalities as Dash and is also open source this package was a valid alternative for Dash. After some research we discoverd that Folium has a focus on good-looking visualization but lacks in performance. Because we want to use lots of data and the visual advantage was not significant enough we chose for Dash rather than Folium.

### Considered Leaflet
Leaflet was recommended to us and for that reason we did some investigating in what it had to offer. After some searching it became clear this is an JavaScrip application instead of working together with python. Because JavaScript is more difficult than python and Dash and Folium were also working options we did not use Leaflet.

### Used MySQL-connector-python
We use the MySQL connector for python to connect to the MySQL database. This is one of few packages able to connect to a MySQL server and was for that reason used. More explaining about the choice for MySQL can be found under the header Database.

### Used Pandas
Used to execute MySQL queries and read the results. Also used to write CSV files for export. Again there are not many choices for this application so the decision was easy.

# Database
Because the data used is very large and loading all of it in makes the program really slow we decided to use a database to help with the storage of all the points as well as give a significant speedup for the filtering.
Again we list the reasoning behind choosing MySQL and the rejected alternatives:

## Used MySQL
MySQL is an application that can run a database for a server and is specialized in fast read instructions with simple conditions, so filtering for a specific city is really fast for MySQL with the correct configuration. It is also the most used database system currenctly so most questions about the database are already answered on internet.

## Considered PostgreSQL
PostgreSQL was also considered as it is the second most used database system. This database is fast for writes, in particular writes that from users which may or may not contain invalid data that should be handeled correctly. Because the database is not often updated and these optimizations slowed down the read operations the database was not used in the final project.

## Considered CockroachDB
CockroachDB was also an options since it is open source and also has an focus on MySQL. The database system is very reliable which was their most important attribute, but it is used less and the many copies of the database to ensure its reliability took a cut out of its performance which was our most important goal. For that reason this option was rejected.