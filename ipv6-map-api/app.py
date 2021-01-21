from flask import Flask
from flask_restful import Api, Resource, reqparse
import csv
import pandas as pd
import numpy as np

app = Flask(__name__)
api = Api(app)

ipLocations = []
ipBlocks = []

# with open('GeoLite2-City-Locations-en.csv', newline='', encoding='utf-8') as csvfile:
#     next(csvfile)
#     locationsReader = csv.reader(csvfile, delimiter=',', quotechar='"')
#     for row in locationsReader:
#         ipLocations.append({
#             "geoname_id": row[0],
#             "locale_code": row[1],
#             "continent_code": row[2],
#             "continent_name": row[3],
#             "country_iso_code": row[4],
#             "country_name": row[5],
#             "subdivision_1_iso_code": row[6],
#             "subdivision_1_name": row[7],
#             "subdivision_2_iso_code": row[8],
#             "subdivision_2_name": row[9],
#             "city_name": row[10],
#             "metro_code": row[11],
#             "time_zone": row[12],
#             "is_in_european_union": row[13]
#         })

with open('GeoLite2-City-Blocks-IPv6.csv', newline='', encoding='utf-8') as csvfile:
    next(csvfile)
    blocksReader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in blocksReader:
        ipBlocks.append({
            "network": row[0],
            "geoname_id": row[1],
            "registered_country_geoname_id": row[2],
            "represented_country_geoname_id": row[3],
            "is_anonymous_proxy": row[4],
            "is_satellite_provider": row[5],
            "postal_code": row[6],
            "latitude": row[7],
            "longitude": row[8],
            "accuracy_radius": row[9],
        })

ipCountsDF = pd.DataFrame(ipBlocks).pivot_table(index=['latitude', 'longitude'], aggfunc='size')
ipCounts = []
for ipCount in ipCountsDF.items():
    ipCounts.append({
        "latitude": ipCount[0][0],
        "longitude": ipCount[0][1],
        "count": ipCount[1]
    })

# ipGeos = pd.merge(pd.DataFrame(ipLocations), dfIPBlocks, on='geoname_id', how='outer')
# ipGeos = ipGeos.replace({np.nan: None})

@app.route("/ipCounts/")
def getIPCounts():
    return {"result": ipCounts}, 200

app.run(debug=True)