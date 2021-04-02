from pymongo import MongoClient
import time
import csv
import os

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

# creates csv file with n-number of data
def getData(n):
    # connects to database
    cluster = MongoClient(os.environ.get("MONGODB_CLIENT"))
    db = cluster[os.environ.get("MONGODB_DATABASE")]
    collection = db[os.environ.get("MONGODB_COLLECTION")]

    # finds n-number of data sorted from newest to oldest
    results = collection.find().sort([('time', -1)]).limit(n)

    # creates csv file with num. of data, timestamp, temp., pressure as parameters
    i = 0
    with open("data.csv", "w", newline='') as csvfile:
        field_names = ["i", "timestamp", "temperature", "pressure"]

        theWriter = csv.DictWriter(csvfile, fieldnames=field_names)
        theWriter.writeheader()

        for result in results:
            i += 1
            theWriter.writerow({"i":i, "timestamp":result["time"], "temperature":result["temperature"], "pressure":result["pressure"]})
