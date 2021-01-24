import os
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
from cachetools import cached, TTLCache
import hashlib

app = Flask(__name__)
cache = TTLCache(maxsize=1024, ttl=600)
cors = CORS(app)
api = Api(app)

DATA_FILE = "data/GeoLite2-City-Blocks-IPv4.csv"
BIN_FILE = "data/ipCounts.bin"

fileHash = hashlib.md5()
fileHash.update(open(DATA_FILE, 'rb').read())
cachedIpCountsDict = {}

@cached(cache)
def read_data():
    global fileHash
    global cachedIpCountsDict

    newHash = hashlib.md5()
    newHash.update(open(DATA_FILE, 'rb').read())
    createNew = fileHash.digest() != newHash.digest()
    fileHash = newHash
    if not createNew and cachedIpCountsDict != {}:
        return cachedIpCountsDict

    ipCounts = ipv6_map_api.ipCount_pb2.IPCounts()
    if not createNew:
        try:
            f = open(BIN_FILE, "rb")
            ipCounts.ParseFromString(f.read())
            f.close()
            createNew |= False
        except IOError:
            print("Could not open " + BIN_FILE + ". Creating a new one.")
            createNew = True

    if createNew:
        print("Creating new protocol buffer")
        ipBlocks = []
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
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
        f = open(BIN_FILE, "wb")
        f.write(ipCounts.SerializeToString())
        f.close()
    
    cachedIpCountsDict = protobuf_to_dict.protobuf_to_dict(ipCounts, including_default_value_fields=True)['ipCounts']
    return cachedIpCountsDict

@app.route("/ipCounts")
@cross_origin()
def getIPCounts():
    ipCountsDict = read_data()
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