from flask import Flask, request
from flask_restful import Api
from flask_cors import CORS, cross_origin
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from decimal import Decimal
import csv
import pandas as pd
import json

app = Flask(__name__)
cors = CORS(app)
api = Api(app)

ipLocations = []
ipBlocks = []

with open('data/GeoLite2-City-Blocks-IPv4.csv', newline='', encoding='utf-8') as csvfile:
    next(csvfile)
    blocksReader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in blocksReader:
        ipBlocks.append({
            "latitude": row[7],
            "longitude": row[8],
        })

ipCountsDF = pd.DataFrame(ipBlocks).pivot_table(index=['latitude', 'longitude'], aggfunc='size')
ipCounts = []
for ipCount in ipCountsDF.items():
    if ipCount[0][0] != '' and ipCount[0][1] != '':
        ipCounts.append({
            "latitude": ipCount[0][0],
            "longitude": ipCount[0][1],
            "count": ipCount[1]
        })

@app.route("/ipCounts")
@cross_origin()
def getIPCounts():
    result = ipCounts
    if "bounds" in request.args:
        bounds = json.loads(request.args["bounds"])
        polygon = Polygon(bounds)
        boundedIpCounts = []
        for ipCount in ipCounts:
            if polygon.contains(Point(Decimal(ipCount['longitude']), Decimal(ipCount['latitude']))):
                print(ipCount)
                boundedIpCounts.append(ipCount)
        result = boundedIpCounts
    return {"result": result}, 200

app.run(debug=True)