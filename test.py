import fiona
import shapely
from shapely.geometry import asPolygon, asShape, Point
from pyproj import Transformer, Proj, transform

lat=42.257564
lon=-83.728200

transformer = Transformer.from_crs("epsg:4326", "epsg:2253", always_xy=True)
out1, out2 = transformer.transform(lon, lat)

with fiona.open("AA_Wards_and_Precincts/AA_Wards_and_Precincts.shp") as fiona_collection:
    for record in fiona_collection:
        shape = asShape(record['geometry'])
        point = Point(out1, out2)
        if shape.contains(point):
            precinct = record['properties']['WRDPCT']
            print(f"Precinct {precinct}")

