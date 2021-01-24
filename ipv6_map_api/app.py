from flask import Flask, request
from flask_restful import Api
from flask_cors import CORS, cross_origin
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import csv
import pandas as pd
import json
import sys
sys.path.append("..")
import ipv6_map_api.ipCount_pb2
import protobuf_to_dict
app = Flask(__name__)
cors = CORS(app)
api = Api(app)

ipLocations = []
ipBlocks = []

ipCounts = ipv6_map_api.ipCount_pb2.IPCounts()
try:
    f = open("ipCounts.bin", "rb")
    ipCounts.ParseFromString(f.read())
    f.close()
    createNew = False
except IOError:
    print("Could not open ipCounts.bin. Creating a new one.")
    createNew = True

if createNew:
    with open('data/GeoLite2-City-Blocks-IPv4.csv', newline='', encoding='utf-8') as csvfile:
        next(csvfile)
        blocksReader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in blocksReader:
            ipBlocks.append({
                "latitude": row[7],
                "longitude": row[8],
            })

    ipCountsDF = pd.DataFrame(ipBlocks).pivot_table(index=['latitude', 'longitude'], aggfunc='size')
    for ipCount in ipCountsDF.items():
        if ipCount[0][0] != '' and ipCount[0][1] != '':
            newCount = ipCounts.ipCounts.add()
            newCount.latitude = float(ipCount[0][0])
            newCount.longitude = float(ipCount[0][1])
            newCount.count = ipCount[1]
    f = open("ipCounts.bin", "wb")
    f.write(ipCounts.SerializeToString())
    f.close()

    

@app.route("/ipCounts")
@cross_origin()
def getIPCounts():
    ipCountsDict = protobuf_to_dict.protobuf_to_dict(ipCounts, including_default_value_fields=True)['ipCounts']
    result = ipCountsDict
    if "bounds" in request.args:
        bounds = json.loads(request.args["bounds"])
        polygon = Polygon(bounds)
        boundedIpCounts = []
        for ipCount in ipCountsDict:
            if polygon.contains(Point(float(ipCount['latitude']), float(ipCount['longitude']))):
                boundedIpCounts.append(ipCount)
        result = boundedIpCounts
    return {"result": result}, 200

app.run(debug=True)