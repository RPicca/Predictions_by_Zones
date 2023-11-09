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
    nbr_regions=int(lines[0].split(" ")[1])
    for i in range(nbr_regions):
        is_hole=False
        pol=[]
        for pt in range(int(lines[l])): #Nombre de points indiqué dans le fichier
            l+=1
            a=lines[l].split("\t")
            pol.append((float(a[0]),float(a[1])))
        l+=1
        # Le trou peut être dans n'importe quel polygone. On parcours toute la liste pour chercher si on intersecte
        for p in polys:
            if Polygon(pol).intersects(Polygon(p[0])):
                p[1].append(pol)
                is_hole=True
        if not is_hole:
            polys.append([pol, []])
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

def partition(geom, delta, resolution, all_tiles=False):
    prepared_geom = prep(geom)
    if not all_tiles:
        grid = list(filter(prepared_geom.intersects, grid_bounds(geom, delta, resolution)))
    else:
        grid=grid_bounds(geom, delta, resolution)
    return grid
def tiles_geo(grid, file_name):
    f=open(file_name, "w")
    nbr_tiles=len(grid)
    f.write("REGION "+str(nbr_tiles)+"\n")
    for g in range(len(grid)):
        f.write("5\n")
        for coord in range(5):
            f.write(str(grid[g].exterior.coords.xy[0][coord])+"\t"+str(grid[g].exterior.coords.xy[1][coord])+"\n")
    f.close()


resolution=50
tile_size=10000
polys=read_geometry(".\\geo.txt").geoms
all_tiles=True
cnt=0
for poly in polys:
    geom = poly
    grid = partition(geom, tile_size, resolution, all_tiles)
    print("nombre de tuiles : ", len(grid))
    tiles_geo(grid, ".\\tiles"+str(cnt)+".txt")
    fig, ax = plt.subplots(figsize=(15, 15))
    gpd.GeoSeries(grid).boundary.plot(ax=ax)
    gpd.GeoSeries([geom]).boundary.plot(ax=ax,color="red")
    cnt+=1
plt.show()
