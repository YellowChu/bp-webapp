from pymongo import MongoClient
import time
import csv
import os
from datetime import datetime, timedelta

# stores data if it is unique
def storeData(data):
    # connects to database
    cluster = MongoClient(os.environ.get("MONGODB_CLIENT"))
    db = cluster[os.environ.get("MONGODB_DATABASE")]
    collection = db[os.environ.get("MONGODB_COLLECTION")]

    # id in mongo_db is uplink_id + its timestamp
    pysense_id = data.ids[0] + str(data.timestamps[0])
    # looks for duplicates
    duplicates = collection.find({"_id": pysense_id})
    # you have to loop through results to find duplicates
    for duplicate in duplicates:
        uselesscode = ""

    # if the id is unique, data is saved to database
    if duplicates.retrieved == 0:
        post = {
            "_id": pysense_id,
            "time": data.timestamps[0],
            "temperature": data.temperatures[0],
            "pressure": data.pressures[0],
        }

        collection.insert_one(post)

# creates csv file with data between the entered interval
def getData(from_timestamp, to_timestamp):
    # connects to database
    cluster = MongoClient(os.environ.get("MONGODB_CLIENT"))
    db = cluster[os.environ.get("MONGODB_DATABASE")]
    collection = db[os.environ.get("MONGODB_COLLECTION")]

    # finds data between the interval
    results = collection.find({'time': {'$gte': from_timestamp, '$lte': to_timestamp+60}}).sort([('time', -1)])

    # creates csv file with num. of data, datetime, temp., pressure as parameters
    i = 0
    with open("data.csv", "w", newline='') as csvfile:
        field_names = ["i", "Date Time", "Temperature [°C]", "Pressure [Pa]"]

        theWriter = csv.DictWriter(csvfile, fieldnames=field_names)
        theWriter.writeheader()

        for result in results:
            i += 1
            dt = datetime.fromtimestamp(result["time"]) - timedelta(hours=2)
            theWriter.writerow({"i":i, "Date Time":dt, "Temperature [°C]":result["temperature"], "Pressure [Pa]":result["pressure"]})
