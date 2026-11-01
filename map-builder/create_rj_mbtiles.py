#!/usr/bin/env python3
"""Render a compact Rio de Janeiro raster MBTiles from LEGALLY downloaded OSM PBF.
This script never requests tiles from tile.openstreetmap.org.
Simplified offline road basemap for AD Car Aura (not a full cartographic rendering).
Copyright OSM contributors; ODbL attribution displayed by the app.
Usage: python tools/create_rj_mbtiles.py rio-highways.osm.pbf /path/RJ-ADCar.mbtiles
"""
import argparse
import array
import io
import math
import os
import sqlite3
import sys
import time
import zlib
from pathlib import Path

import osmium
from PIL import Image, ImageDraw, ImageFont

# BBox fully encloses the State of Rio de Janeiro, with a small buffer for roads.
WEST, SOUTH, EAST, NORTH = -45.33, -23.50, -40.60, -20.62
MIN_ZOOM, MAX_ZOOM = 7, 13
BACK = "#131c28"
HIGHWAYS = {
    "motorway": 1,"motorway_link":1,"trunk":1,"trunk_link":1,
    "primary":2,"primary_link":2,"secondary":3,"secondary_link":3,
    "tertiary":4,"tertiary_link":4,"residential":5,"living_street":5,
    "unclassified":5,"service":6,"road":5,"track":7,
    "pedestrian":7
}
COLORS = {1:"#e3ac7e",2:"#d6b48e",3:"#d3cebc",4:"#acaeb1",5:"#75869a",6:"#55677b",7:"#475464",8:"#477b91"}
# Non-OSM place labels are not fabricated; labels below come from place=* OSM nodes.

def norm(lon,lat):
    lat=max(-85.0511,min(85.0511,lat))
    x=(lon+180.0)/360.0
    y=(1.0-math.asinh(math.tan(math.radians(lat)))/math.pi)/2.0
    return x,y

BBOX=(norm(WEST,NORTH)[0],norm(EAST,SOUTH)[0],norm(EAST,SOUTH)[1],norm(WEST,NORTH)[1])
# sqlite RTree uses xMin,xMax,yMin,yMax with y increasing southward.
XMIN,XMAX,YMAX,YMIN=BBOX

def inside_bbox(xmin,xmax,ymin,ymax):
    return xmin<=XMAX and xmax>=XMIN and ymin<=YMAX and ymax>=YMIN

def category(way):
    highway=way.tags.get("highway")
    if highway in HIGHWAYS:
        return HIGHWAYS[highway]
    water=way.tags.get("waterway")
    if water in ("river","stream","canal","ditch"):
        return 8
    return None

class RoadCollector(osmium.SimpleHandler):
    def __init__(self,db):
        super().__init__();self.db=db;self.count=0;self.place_count=0
        self.batch=[];self.batch_index=[];self.place_batch=[]
    def flush(self):
        if self.batch:
            self.db.executemany("INSERT INTO roads(id,kind,name,geom) VALUES (?,?,?,?)",self.batch)
            self.db.executemany("INSERT INTO roads_index(id,minx,maxx,miny,maxy) VALUES(?,?,?,?,?)",self.batch_index)
            self.batch.clear();self.batch_index.clear()
        if self.place_batch:
            self.db.executemany("INSERT INTO places(name,kind,x,y) VALUES(?,?,?,?)",self.place_batch)
            self.place_batch.clear()
        self.db.commit()
    def node(self,n):
        p=n.tags.get("place")
        if p not in ("city","town","village","suburb","hamlet"):return
        if not n.location.valid():return
        name=n.tags.get("name");lon=n.location.lon;lat=n.location.lat
        if not name or not (WEST<=lon<=EAST and SOUTH<=lat<=NORTH):return
        x,y=norm(lon,lat)
        self.place_batch.append((name,{"city":1,"town":2,"village":3,"suburb":4,"hamlet":5}[p],x,y))
        self.place_count+=1
    def way(self,w):
        kind=category(w)
        if kind is None:return
        coords=array.array("f")
        try:
            for node in w.nodes:
                if node.location.valid():
                    x,y=norm(node.location.lon,node.location.lat)
                    coords.extend((x,y))
        except Exception:return
        if len(coords)<4:return
        xs=coords[0::2];ys=coords[1::2]
        xmin,xmax,ymin,ymax=min(xs),max(xs),min(ys),max(ys)
        if not inside_bbox(xmin,xmax,ymin,ymax):return
        name=w.tags.get("name","")[:100]
        self.count+=1
        blob=zlib.compress(coords.tobytes(),level=1)
        self.batch.append((self.count,kind,name,blob))
        self.batch_index.append((self.count,xmin,xmax,ymin,ymax))
        if len(self.batch)>=4000:
            self.flush()
            if self.count%40000<4000: print(f"Read {self.count:,} highway/waterway ways",flush=True)

def label_font(size):
    paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for p in paths:
        try:return ImageFont.truetype(p,size)
        except Exception:pass
    return ImageFont.load_default()

def render(db,z,tx,ty,font,font_city):
    N=1<<z
    box=(tx/N,(tx+1)/N,ty/N,(ty+1)/N)
    xmin,xmax,ymin,ymax=box
    im=Image.new("RGB",(256,256),BACK)
    d=ImageDraw.Draw(im)
    query="""SELECT r.kind,r.name,r.geom FROM roads_index idx
             JOIN roads r ON r.id=idx.id
             WHERE idx.minx<=? AND idx.maxx>=? AND idx.miny<=? AND idx.maxy>=?
             ORDER BY r.kind DESC"""
    rows=db.execute(query,(xmax,xmin,ymax,ymin)).fetchall()
    labels=[];has_road=False
    for typ,name,blob in rows:
        if typ>=7 and z<11:continue
        if typ>=5 and z<10:continue
        if typ>=4 and z<9:continue
        if typ>=3 and z<8:continue
        pos=array.array("f");pos.frombytes(zlib.decompress(blob))
        pts=[((pos[i]*N-tx)*256,(pos[i+1]*N-ty)*256) for i in range(0,len(pos),2)]
        if len(pts)<2:continue
        width=max(1,{1:4,2:3,3:2,4:2,5:1,6:1,7:1,8:1}[typ]+max(-2,z-12))
        if typ==8:
            d.line(pts,fill=COLORS[typ],width=max(1,width))
        else:
            if typ<=3 and z>=10:d.line(pts,fill="#293442",width=width+2,joint="curve")
            d.line(pts,fill=COLORS[typ],width=width,joint="curve")
            has_road=True
        if z>=11 and name and typ<=4 and len(pts)>=2:
            mid=pts[len(pts)//2]
            if 15<mid[0]<235 and 16<mid[1]<236:
                labels.append((typ,name,mid))
    # Major roads first, only a few street names per tile, avoid overlap.
    if z>=11 and has_road:
        occupied=[]
        for typ,name,(x,y) in sorted(labels,key=lambda q:q[0]):
            if len(occupied)>=8:break
            text=name if len(name)<25 else name[:22]+"…"
            size=d.textbbox((0,0),text,font=font)
            tw=size[2]-size[0]
            if not (10<x<245-tw):continue
            if any(abs(x-x0)<min(tw+10,110) and abs(y-y0)<16 for x0,y0 in occupied):continue
            d.text((x,y),text,font=font,fill="#eef3f6",stroke_width=2,stroke_fill="#182331")
            occupied.append((x,y))
    if z>=8:
        places=db.execute("""SELECT name,kind,x,y FROM places
             WHERE x>=? AND x<=? AND y>=? AND y<=? ORDER BY kind LIMIT 45""",
             (xmin,xmax,ymin,ymax)).fetchall()
        previous=[]
        for name,kind,x,y in places:
            if z<=9 and kind>2:continue
            if z<=11 and kind>3:continue
            px=(x*N-tx)*256;py=(y*N-ty)*256
            if any(abs(px-a)<90 and abs(py-b)<20 for a,b in previous):continue
            label=name if len(name)<28 else name[:26]
            d.text((px+4,py-12),label,font=font_city,fill="#f5f7f8",stroke_width=3,stroke_fill="#111b28")
            d.ellipse((px-2,py-2,px+2,py+2),fill="#f5e3b3")
            previous.append((px,py))
    # Render blank background tiles too: no gaps in rural/offshore regions.
    b=io.BytesIO();im.save(b,format="PNG",compress_level=6,optimize=False)
    return b.getvalue()

def create(source,destination):
    work=Path(str(destination)+".work.sqlite")
    if work.exists():work.unlink()
    db=sqlite3.connect(str(work))
    db.execute("PRAGMA journal_mode=OFF");db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE roads(id INTEGER PRIMARY KEY,kind INTEGER,name TEXT,geom BLOB)")
    db.execute("CREATE VIRTUAL TABLE roads_index USING rtree(id,minx,maxx,miny,maxy)")
    db.execute("CREATE TABLE places(name TEXT,kind INTEGER,x REAL,y REAL)")
    handler=RoadCollector(db);start=time.monotonic()
    print("Reading OSM road network:",source,flush=True)
    handler.apply_file(str(source),locations=True,idx="sparse_mmap_array")
    handler.flush()
    print(f"Stored {handler.count:,} ways and {handler.place_count:,} places after {time.monotonic()-start:.1f}s",flush=True)
    out=Path(destination);out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():out.unlink()
    mb=sqlite3.connect(str(out))
    mb.execute("PRAGMA journal_mode=OFF");mb.execute("PRAGMA synchronous=OFF")
    mb.execute("CREATE TABLE metadata(name TEXT,value TEXT)")
    mb.execute("CREATE TABLE tiles(zoom_level INTEGER,tile_column INTEGER,tile_row INTEGER,tile_data BLOB)")
    mb.execute("CREATE UNIQUE INDEX tile_unique ON tiles(zoom_level,tile_column,tile_row)")
    info={
        "name":"AD Car Aura · Rio de Janeiro (OSM offline raster)",
        "description":"Simplified drivable offline road basemap from OpenStreetMap PBF; limited raster zoom 7-13; NOT turn-by-turn routing.",
        "type":"baselayer","version":"2026-10-31","format":"png",
        "bounds":f"{WEST},{SOUTH},{EAST},{NORTH}",
        "center":"-43.2,-22.8,10","minzoom":str(MIN_ZOOM),"maxzoom":str(MAX_ZOOM),
        "attribution":"© OpenStreetMap contributors (ODbL) · Geofabrik extract · rendered for AD Car"
    }
    mb.executemany("INSERT INTO metadata(name,value) VALUES (?,?)",info.items())
    font=label_font(11);font_city=label_font(12)
    tile_count=0
    for z in range(MIN_ZOOM,MAX_ZOOM+1):
        x0=int(norm(WEST,NORTH)[0]*(1<<z));x1=int(norm(EAST,SOUTH)[0]*(1<<z))
        y0=int(norm(WEST,NORTH)[1]*(1<<z));y1=int(norm(EAST,SOUTH)[1]*(1<<z))
        count=0
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                content=render(db,z,x,y,font,font_city)
                if content is None:continue
                mb.execute("INSERT INTO tiles VALUES (?,?,?,?)",(z,x,(1<<z)-1-y,sqlite3.Binary(content)))
                count+=1
            if x%6==0:mb.commit()
        mb.commit();tile_count+=count
        print(f"zoom {z} -> {count:,} raster tiles, total {tile_count:,} ({out.stat().st_size/1024/1024:.1f} MB)",flush=True)
    result=mb.execute("PRAGMA integrity_check").fetchone()[0]
    print("SQLite integrity:",result,flush=True)
    if result!="ok" or tile_count<100:raise RuntimeError("MBTiles invalid or unexpectedly small")
    mb.close();db.close();work.unlink(missing_ok=True)
    print(f"DONE {out} {out.stat().st_size/1048576:.1f} MiB · {tile_count:,} tiles",flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("pbf")
    parser.add_argument("output")
    args=parser.parse_args()
    create(Path(args.pbf),Path(args.output))
