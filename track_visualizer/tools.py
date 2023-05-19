import os
import datetime as datm

def anti_overwrite_check(path):
    while os.path.exists(path):
        lastdir = os.path.basename(path)
        split = lastdir.split('_v')
        
        if len(split) > 1:
            try:
                suffix = int(split[-1])
                new_suffix = '_v{}'.format(suffix + 1)
                new_lastdir = split[-2] + new_suffix
            except:
                new_suffix = '_v2'
                new_lastdir = lastdir + new_suffix
        else:
            new_lastdir = lastdir + '_v2'
            
        new_path = path.replace(lastdir, new_lastdir)
        path = new_path
    
    return path

def add_to_time(t, hours=0, minutes=0, seconds=0):
    newdate = datm.datetime.combine(datm.date(1,1,1), t) + datm.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    
    return newdate.time()

def get_crop_coords(rx, ry, scale=1):
    width = 1024 / 2 * scale
    xrange = (rx - width, rx + width)
    yrange = (ry - width, ry + width)
    
    return (xrange[0], yrange[0], xrange[1], yrange[1])

def format_line_id(id):
    out = int(id*10)
    return out