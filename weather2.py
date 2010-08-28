#!/usr/local/bin/python
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Author Daniel Guerrero (chancleta at gmail dot com)
#    Usage: python weather2.py
#
#    Source code from meteo project can be found at:
#    http://github.com/daniguerrero/meteo

import urllib
from datetime import datetime, date, time
import time as _time

#list of strings of cities: Lyon, Alicante, Sunne, Madrid, London so far
city_list=['20068133','12695279','906783','766273','44418']

def string_to_stamp(chain):
   #yahoo gives us the date like: "Sun, 15 Aug 2010 10:50 am BST"
   #striping time zone as we want to compare at same hour
   dt = datetime.strptime(chain, "%a, %d %b %Y %I:%M %p")
   tt = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0, -1)
   stamp = _time.mktime(tt)
   return stamp

def putinline(url):
   opener = urllib.FancyURLopener({})
   f = opener.open(url)
   #doing a kind of bash grep separating fields with ";"
   for line in f:
       if 'yweather:wind' in line: 
           words = line.split('"')
           result.write(words[1]+';'+words[3]+';'+words[5]) 
       elif 'yweather:atmosphere' in line:
           words = line.split('"')
           result.write(';'+words[1]+';'+words[3]+';'+words[5])
       elif 'yweather:astronomy' in line:
           words = line.split('"')
           result.write(';'+words[1]+';'+words[3])
       elif 'yweather:condition' in line:
           words = line.split('"')
           result.write(';'+words[1]+';'+words[3]+';'+words[5]+';')
           stringdate = words[7].split(' ')
           #getting rid off time zone
           stringnotz = stringdate[0]+" "+stringdate[1]+" "+stringdate[2]+" "+stringdate[3]+" "+stringdate[4]+" "+stringdate[5]
           #realtime converstion to timestamp
           result.write(str(string_to_stamp(stringnotz)))
   result.close
   f.close 

#column meas, stands for specific meassurement: temp, humidity, preassure...
#column stamp is the timestamp
def gen_stamp_data (city,column_meas,column_stamp):
    dbfile = open('weather_db2.txt','r')
    chain_stamp_data = "" 
    first_round = True
    for line in dbfile:
        city_split = line.split('|')
        city_string = city_split[city]
        single_data = city_string.split(';')
        if first_round == True:
           chain_stamp_data = '['+str(single_data[column_stamp])+','+str(single_data[column_meas])+']'
        else:
           chain_stamp_data = '['+str(single_data[column_stamp])+','+str(single_data[column_meas])+']'+','+chain_stamp_data 
        first_round = False 
    dbfile.close
    return chain_stamp_data


def main():
    for x in city_list[:]:
       putinline('http://weather.yahooapis.com/forecastrss?w='+x+'&u=c')
       #separate cities with symbol "|"
       result.write('|')
    #separate samples 
    result.write('\n')
    
    #Didn't spent too much time here probably can be improved
    #once we have all data on the text file, lets generate the json data
    jsonfile = open('/var/www/meteo/weather_json.js','w')
    #adding json data to file
    #temperature
    gen_stamp_data (0,10,11)
    temp_lyon=gen_stamp_data (0,10,11)
    temp_alicante=gen_stamp_data (1,10,11)
    temp_sunne=gen_stamp_data (2,10,11)
    temp_madrid=gen_stamp_data (3,10,11)
    temp_london=gen_stamp_data (4,10,11)
    #humdity
    humi_lyon=gen_stamp_data (0,3,11)
    humi_alicante=gen_stamp_data (1,3,11)
    humi_sunne=gen_stamp_data (2,3,11)
    humi_madrid=gen_stamp_data (3,3,11)
    humi_london=gen_stamp_data (4,3,11)


    jsonfile.write('var temperature={ "Lyon": { "data":['+temp_lyon+'], "x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "Alicante": { "data":['+temp_alicante+'], "x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "Sunne": { "data":['+temp_sunne+'],"x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "Madrid": { "data":['+temp_madrid+'],"x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "London": { "data":['+temp_london+'],"x_field_name": "timestamp", "y_field_name": "Temperatura" } };\
var humidity={ "Lyon": { "data":['+humi_lyon+'], "x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "Alicante": { "data":['+humi_alicante+'], "x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "Sunne": { "data":['+humi_sunne+'],"x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "Madrid": { "data":['+humi_madrid+'],"x_field_name": "timestamp", "y_field_name": "Temperatura" },\
 "London": { "data":['+humi_london+'],"x_field_name": "timestamp", "y_field_name": "Temperatura" } }; var cities=["Lyon", "Alicante", "Sunne", "Madrid", "London"];')
    jsonfile.close


if __name__ == "__main__":
    result = open('weather_db2.txt','a')
    main()
    result.close
