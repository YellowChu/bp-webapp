import http.client
import json
import base64
import struct
from datetime import datetime, timedelta
import time
import ttn
import requests
import os

#######################################################################
# CURRENTLY SET FOR THE THINGS STACK V3, FOR V2 CHECK VERSION CONTROL #
#######################################################################

# schedules Downlink to TTN by creating post request
def scheduleDownlink(payload):
    # parameters for request
    url = os.environ.get("TTNV3_POST_URL")
    body = {"downlinks":[{"frm_payload":payload, "f_port":1, "confirmed": True}]}
    post_bearer = os.environ.get("TTNV3_POST_BEARER")

    requests.post(url, data=json.dumps(body), headers={"Authorization": post_bearer})

# gathers lastest 100 uplinks from Pipdedream (TTN sends all the data to pipedream using webhooks)
class Uplinks:
    def __init__(self):
        # request data from pipedream
        pd_bearer = os.environ.get("PD_BEARER")
        conn = http.client.HTTPSConnection('api.pipedream.com')
        conn.request("GET", '/v1/sources/dc_BVu2xEz/event_summaries?expand=event', '', {
          'Authorization': pd_bearer,
        })

        # parse response
        res = conn.getresponse()
        events = res.read()
        eventsStr = events.decode("utf-8")
        eventsParsed = json.loads(eventsStr)

        # initialize attributes lists
        self.ids = []
        self.altitudes = []
        self.pressures = []
        self.temperatures = []
        self.batteries = []
        self.dataRates = []
        self.timestamps = []

        # loops through gathered data
        for data in eventsParsed["data"]:
            # unpack the payload to hex
            payloadRaw = data["event"]["body"]["uplink_message"]["frm_payload"]
            lopyData = base64.b64decode(payloadRaw).hex()
            # extract values from payload (in hex)
            payloadId = lopyData[0:8]
            altitudeHex = lopyData[8:16]
            pressureHex = lopyData[16:24]
            temperatureHex = lopyData[24:32]
            batteryHex = lopyData[32:40]
            # append to list of values converted to float except from the id
            self.ids.append(payloadId)
            self.altitudes.append(struct.unpack('f', bytes.fromhex(altitudeHex))[0])
            self.pressures.append(struct.unpack('f', bytes.fromhex(pressureHex))[0])
            self.temperatures.append(struct.unpack('f', bytes.fromhex(temperatureHex))[0])
            self.batteries.append(struct.unpack('f', bytes.fromhex(batteryHex))[0])
            # get data rate/spreading factor/bandwith
            dataRate = data["event"]["body"]["uplink_message"]["settings"]["data_rate"]["lora"]["spreading_factor"]
            if dataRate == 7:
                dataRate = "SF7 (5min interval)"
            if dataRate == 8:
                dataRate = "SF8 (10min interval)"
            if dataRate == 9:
                dataRate = "SF9 (15min interval)"
            if dataRate == 10:
                dataRate = "SF10 (30min interval)"
            if dataRate == 11:
                dataRate = "SF11 (60min interval)"
            if dataRate == 12:
                dataRate = "SF12 (90min interval)"
            self.dataRates.append(dataRate)
            # get time value and convert it to timestamp
            timeInData = data["event"]["body"]["uplink_message"]["received_at"]
            dateTimeStr = timeInData[0:10] + " " + timeInData[11:19]
            dateTime = datetime.strptime(dateTimeStr, "%Y-%m-%d %H:%M:%S") + timedelta(hours=4)
            timestamp = datetime.timestamp(dateTime)
            self.timestamps.append(timestamp)
