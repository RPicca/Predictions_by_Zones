from shapely.geometry import Polygon
import numpy as np
from shapely.prepared import prep
import geopandas as gpd
import matplotlib.pyplot as plt

def read_geometry(geo_file):
    f=open(geo_file, "r")
    lines=f.readlines()
    f.close()
    poly=[]
    for pt in lines[2:]:
        a=pt.split("\t")
        poly.append((float(a[0]),float(a[1])))
    return Polygon(poly)

def grid_bounds(geom, delta, resolution):
    minx, miny, maxx, maxy = geom.bounds
    minx=minx//resolution*resolution
    maxx=np.ceil((maxx-minx)/delta)*delta+minx
    maxy=np.ceil(maxy/resolution)*resolution
    miny=maxy-np.ceil((maxy-miny)/delta)*delta
    nx = int((maxx - minx)/delta)+1
    ny = int((maxy - miny)/delta)+1
    gx, gy = np.linspace(minx,maxx,nx), np.linspace(miny,maxy,ny)
    grid = []
    for i in range(len(gx)-1):
        for j in range(len(gy)-1):
            poly_ij = Polygon([[gx[i],gy[j]],[gx[i],gy[j+1]],[gx[i+1],gy[j+1]],[gx[i+1],gy[j]]])
            grid.append( poly_ij )
    return grid

def partition(geom, delta, resolution):
    prepared_geom = prep(geom)
    grid = list(filter(prepared_geom.intersects, grid_bounds(geom, delta, resolution)))
    return grid


resolution=50
tile_size=1000
poly=read_geometry("D:\\Documents\\validation\\Addin\\Predictions by Zones\\tuiles\\geo.txt")
geom = poly
grid = partition(geom, tile_size, resolution)

fig, ax = plt.subplots(figsize=(15, 15))
gpd.GeoSeries(grid).boundary.plot(ax=ax)
gpd.GeoSeries([geom]).boundary.plot(ax=ax,color="red")
plt.show()