import os
import datetime as datm
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

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


def time_to_number(time, to_format=float):
    hour = time.hour
    minute = time.minute
    second = time.second

    return to_format(hour * 3600 + minute * 60 + second)


def number_to_time(secs):
    microseconds = int(secs % 1 *10e5)
    seconds = int(secs % 60)
    minutes = int(secs %3600 / 60)
    hours = int(secs / 3600)
    return datm.time(hour=hours, minute=minutes, second=seconds, microsecond=microseconds)


def get_crop_coords(rx, ry, scale=1):
    width = 1024 / 2 * scale
    xrange = (rx - width, rx + width)
    yrange = (ry - width, ry + width)
    
    return (xrange[0], yrange[0], xrange[1], yrange[1])


def format_line_id(id):
    out = int(id*10)
    return out


def strip_nans_from_tail(*lists, tail=200):
    out = []
    out.append(lists[0][~np.isnan(lists[0])])
    
    if len(lists) > 1:
        for ls in lists[1:]:
            _out = np.array(ls)[~(np.isnan(lists[0]) & (np.arange(len(lists[0])) > len(lists[0])-tail))]
            out.append(list(_out))
    return out

def get_timestamp_frame(time, font_size=110, font_path="C:/Users/micha/Documents/Software/fonts/DigitalDismay.ttf", figsize=(510,100), color='white'):
    textimg = Image.new('RGBA', figsize, (10,10,10,0))
    draw  = ImageDraw.Draw(textimg)
    font = ImageFont.truetype(font_path, font_size)
    text = time
    draw.text((1,1), text, fill=color, font=font, align='left')
    
    return textimg


def get_range_suggestions(reader, smoothing=400, threshold=0.95, smoothening_threshold=0.4, minimum_length=500):
    fig, ax = plt.subplots(3,1, dpi=250, figsize=(7,5), sharex=True)
    all_id = np.array([line['id'] for line in reader.data if line['distance'] is not None])

    id_density = int(np.round(1.0 / np.mean(all_id[1:] - all_id[:-1]), 0))
    
    try:
        all_dist = np.array([line['distance'] for line in reader.data if line['distance'] is not None])
    except:
        Exception('Not supported for GPX files - distance log is missing.')

    dist_diff = (all_dist[2:] - all_dist[:-2]) / (all_id[2] - all_id[0])
    
    ax[0].plot(all_id[1:-1], dist_diff)
    
    dist_diff = np.abs(dist_diff)
    dist_diff[dist_diff < threshold] = 0
    dist_diff[dist_diff > threshold] = 1
    
    new = np.zeros_like(dist_diff)
    sm = smoothing * id_density
    
    for i in range(len(dist_diff)):
        if np.mean(dist_diff[i-sm:i+sm]) > smoothening_threshold:
            new[i] = 1
            
    print(max(new))
    dist_diff2 = (new[1:] - new[:-1])
    dist_diff2 /= max(dist_diff2)
    plus = np.array(all_id)[np.argwhere(dist_diff2 > 0.9)]
    minus = np.array(all_id)[np.argwhere(dist_diff2 < -0.9)]
    gaps_pairs = [p.flatten() for p in np.array(list(zip(minus[:-1], plus[1:]))) if np.diff(p, axis=0) > minimum_length]
    drives_pairs = [p.flatten() for p in np.array(list(zip(plus, minus))) if np.diff(p, axis=0) > minimum_length]
    
    ax[1].plot(all_id[1:-1], dist_diff)
    ax[2].plot(all_id[1:-2], dist_diff2)
    
    return {'breaks':gaps_pairs, 'drives':drives_pairs}


def plot_interval_preview(reader, low, high, width=500):
    fig, ax = plt.subplots(1, 2, figsize=(6,3), dpi=300)

    pos_data = np.array([line['position'] for line in reader.data])[low:high]
    pos_data_low = pos_data[:width].T
    pos_data_high = pos_data[-width:].T
    
    ax[0].scatter(pos_data_low[1], pos_data_low[0], s=2)
    ax[0].set_aspect('equal')
    ax[1].scatter(pos_data_high[1], pos_data_high[0], s=2)
    ax[1].set_aspect('equal')


def save_points_as_svg(points, save_path):
    fig, ax  = plt.subplots(figsize=(6,6), dpi=300)
    pos = np.array(points)
    ax.plot(pos[:,1], pos[:,0])
    ax.set_axis_off()
    ax.set_aspect('equal')
    plt.savefig(save_path)
