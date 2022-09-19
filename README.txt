The csv data export files provided by the Albertan govenment on their covid website (https://www.alberta.ca/stats/covid-19-alberta-statistics.htm#data-export) was a fraction of the data provided in the tables of the rest of the website. So I decided to instead manually scrap all the data embedded in the widgets across the website.

There are 2 ways the data is organized (exluding the csv exports): Html tables and html widgets.

This program downloads the html of https://www.alberta.ca/stats/covid-19-alberta-statistics.htm and seperates it into html widgets and html tables.

Currently, the tables are not yet handled.

The widgets are placed into a raw, unorganized and minimally structured dataframe called "silver", and then the date-driven data is properly organized into a hierarchical dataframe called "gold".

An end user cmd application has been started (Grapher.py) to allow ease of selecting, manipulating, and displaying this data, but I'm not so motivated by front-end programming as of 2022-02-16
