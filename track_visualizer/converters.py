import math

def convert_coords(integer):
    return integer  / (2**32 / 360)


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile, zoom


def deg2pixcoord(lat_deg, lon_deg, zoom, tilesize=1024):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = (lon_deg + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    rx = (x - int(x) +1)*tilesize
    ry = (y - int(y) +1)*tilesize
        
    return rx, ry


def degdiff2pixcoord(lat_deg, lon_deg, zoom, tilesize=1024):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = (lon_deg + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    
    rx = x*tilesize
    ry = y*tilesize
        
    return rx, ry




