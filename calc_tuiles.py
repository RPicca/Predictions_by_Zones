from shapely.geometry import Polygon, MultiPolygon
import numpy as np
from shapely.prepared import prep
import geopandas as gpd
import matplotlib.pyplot as plt

def read_geometry(geo_file):
    f=open(geo_file, "r")
    lines=f.readlines()
    f.close()
    l=1 #numéro de ligne
    polys=[]
    pol_and_holes=[]
    nbr_regions=int(lines[0].split(" ")[1])
    for i in range(nbr_regions):
        pol=[]
        for pt in range(int(lines[l])): #Nombre de points indiqué dans le fichier
            l+=1
            a=lines[l].split("\t")
            pol.append((float(a[0]),float(a[1])))
        l+=1
        # Si pol_and_holes vide alors on ajoute juste un polygone
        if pol_and_holes == []:
            pol_and_holes=[pol,[]]
        # S'il ne l'est pas : deux choix : 
        else:
            # Soit le polygone à ajouter est un trou (i.e il intersecte le polygone précédent)
            if Polygon(pol).intersects(Polygon(pol_and_holes[0])):
                pol_and_holes[1].append(pol)
                if i==nbr_regions-1:
                    polys.append(pol_and_holes)
            # Soit ça n'est pas le cas, dans ce cas c'est un nouveau polygone et on peut stocker le précédent
            else:
                polys.append(pol_and_holes)
                pol_and_holes=[pol, []]
                if i==nbr_regions-1:
                    polys.append(pol_and_holes)
    return MultiPolygon(polys)

def grid_bounds(geom, delta, resolution):
    minx, miny, maxx, maxy = geom.bounds
    #wedging
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
polys=read_geometry(".\\geo.txt").geoms
for poly in polys:
    geom = poly
    grid = partition(geom, tile_size, resolution)
    fig, ax = plt.subplots(figsize=(15, 15))
    gpd.GeoSeries(grid).boundary.plot(ax=ax)
    gpd.GeoSeries([geom]).boundary.plot(ax=ax,color="red")
plt.show()