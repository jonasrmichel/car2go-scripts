'''
A simple script to poll car2go's public web API and save the raw data (XML, KML, JSON) to file.

@author: Jonas Michel
'''
import urllib2
import json
import datetime
import os
import unicodedata

''' Settings (configure these) '''
save_directory = "/save/raw/data/to/this/path"
consumer_key = "your-car2go-consumer-key"
'''       (that's all!)        '''

car2go_url = "http://www.car2go.com/api/v2.1"
car2go_data_types = ["parkingspots", "operationareas", "gasstations", "vehicles"]

json_format = "json"
xml_format = "xml"
kml_format = "kml"

translator = {
          0xe4: u'ae',
          0xf6: u'oe',
          0xfc: u'ue',
          0xdf: u'ss',
        }

def getLocations(formats):  # xml or json
    json_data = ""
    for fmt in formats:
        url = car2go_url + "/locations" + "?oauth_consumer_key=" + consumer_key
        if fmt == json_format:
            url += "&format=" + json_format
    
        data = urllib2.urlopen(url).read()
        save(data, "locations", fmt)
        
        if fmt == json_format:
            json_data = data
    
    decoded_json = json.loads(json_data)
    location_names = []
    for location in decoded_json["location"]:
        location_name = location["locationName"]
        location_names.append(format_string(location_name))
    
    return location_names

def format_string(s):
    return unicodedata.normalize('NFKD', s.translate(translator)).encode('ascii', 'ignore').replace(" " , "")

def getLocationData(location, data_type, formats):  # kml or json
    for fmt in formats:
        url = car2go_url + "/" + data_type + "?loc=" + location + "&oauth_consumer_key=" + consumer_key
        if fmt == json_format:
            url += "&format=" + json_format
    
        data = urllib2.urlopen(url).read()
        save(data, os.path.join(location, data_type), fmt)

def save(data, directory, fmt):
    save_path = os.path.join(save_directory, directory)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    now = datetime.datetime.now()
    save_file = os.path.join(save_path, now.strftime("%m-%d-%Y %H:%M:%S") + "." + fmt)
    
    f = open(save_file, "w")
    f.write(data)
    f.close()

if __name__ == '__main__':
    # retrieve the car2go locations (cities)
    locations = getLocations([xml_format, json_format])
    
    # save data for each car2go location
    for location in locations:
        for data_type in car2go_data_types:
            getLocationData(location, data_type, [kml_format, json_format])
