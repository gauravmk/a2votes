from flask import Flask, request, render_template
from pyproj import Transformer
from shapely.geometry import asShape, Point
from dotenv import load_dotenv
import os
import fiona
import googlemaps
import json

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_PLACES_API_KEY"))

app = Flask(__name__)

transformer = Transformer.from_crs("epsg:4326", "epsg:2253", always_xy=True)

f = open("polling_locations.json")
polling_locations = json.load(f)


precincts = []
with fiona.open(
    "AA_Wards_and_Precincts/AA_Wards_and_Precincts.shp"
) as fiona_collection:
    for record in fiona_collection:
        shape = asShape(record["geometry"])
        precincts.append({"shape": shape, "label": record["properties"]["WRDPCT"]})


def getPrecinct(lat, lng):
    out1, out2 = transformer.transform(lng, lat)
    point = Point(out1, out2)
    for precinct in precincts:
        if precinct["shape"].contains(point):
            return precinct["label"]


@app.route("/health")
def health():
    return {"ok": True}


@app.route("/ward_info")
def ward_info():
    geocode_result = gmaps.geocode(
        request.args["addr"],
        bounds={
            "southwest": (42.209925, -83.827531),
            "northeast": (42.343793, -83.642950),
        },
    )
    location = geocode_result[0]["geometry"]["location"]
    precinct = getPrecinct(location["lat"], location["lng"])
    polling_place = polling_locations[precinct]
    return {
        "result": {
            "location": location,
            "precinct": precinct,
            "polling_place": polling_place,
        }
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results")
def results():
    if "addr" not in request.args:
        return render_template("results.html")

    geocode_result = gmaps.geocode(
        request.args["addr"],
        bounds={
            "southwest": (42.209925, -83.827531),
            "northeast": (42.343793, -83.642950),
        },
    )
    if len(geocode_result) == 0:
        return render_template("results.html")

    location = geocode_result[0]["geometry"]["location"]
    precinct = getPrecinct(location["lat"], location["lng"])
    polling_place = polling_locations[precinct]
    polling_place["addr"] += ", Ann Arbor MI"

    return render_template(
        "results.html",
        addr=request.args["addr"],
        location=location,
        precinct=precinct,
        polling_place=polling_place,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
