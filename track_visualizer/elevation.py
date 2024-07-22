import numpy as np
from PIL import Image, ImageDraw, ImageFont
from track_visualizer import tools

def get_elevation_frame(index, all_indices, all_dist, all_elevation, \
                        figsize=(1600,600), xaxis_step=50000, yaxis_step=200, color='white', \
                        breaks=[], tests={}):
    width, height = figsize
    
    all_dist, all_indices, all_elevation = tools.strip_nans_from_tail(all_dist, all_indices, all_elevation)
    
    img = Image.new('RGBA', figsize, (0,0,0,0))
    draw  = ImageDraw.Draw(img)
    font = ImageFont.truetype("C:/Users/micha/Documents/Software/fonts/DigitalDismay.ttf", 250)
    font_labels = ImageFont.truetype("C:/Users/micha/Documents/Software/fonts/DigitalDismay.ttf", 60)
    
    ele_label_size = (750, 250)
    img2 = Image.new('RGBA', ele_label_size, (0,0,0,0))
    draw2  = ImageDraw.Draw(img2)
    elevation = all_elevation[all_indices.index(index)]
    text = "{:.0f}  M".format(elevation)
    draw2.text((ele_label_size[0], 0), text, fill=color, font=font, anchor='rt')
    
    left_gap = 100
    right_gap = 180
    top_gap = 10
    bottom_gap = 80
    bottom_axis_gap = 0.2 * (height - bottom_gap - top_gap)

    xaxis = [(left_gap, height-bottom_gap), (width-right_gap, height-bottom_gap)]
    yaxis = [(left_gap, top_gap), (left_gap, height-bottom_gap)]
    
    xdata = np.array(all_dist) / max(all_dist) * (width - left_gap - right_gap) + left_gap
    ydata = height - (np.array(all_elevation) - min(all_elevation)) / max(all_elevation - min(all_elevation)) * (height - top_gap - bottom_gap - bottom_axis_gap) \
            - bottom_gap - bottom_axis_gap
    xydata = list(zip(xdata, ydata))

    polygon_upper = xydata[:all_indices.index(index)]
    polygon_lower = [(xydata[all_indices.index(index)][0], height-bottom_gap), (left_gap, height-bottom_gap)]
    polygon_points = polygon_upper + polygon_lower
    #draw.polygon(polygon_points, fill=(21, 119, 179,80))
    draw.polygon(polygon_points, fill=(255, 255, 255, 90))
    
    if len(polygon_upper) > 0:
        # draw.line(xydata, fill=(0,0,0,20), width=7, joint='curve')
        # draw.line(polygon_upper, fill=(21, 119, 179), width=9, joint='curve' )
        draw.line(xydata, fill=(255,255,255,120), width=7, joint='curve')
        draw.line(polygon_upper, fill=color, width=9, joint='curve' )

    axis_color = (255,255,255,255)
    axis_width = 6
    for axis in [xaxis, yaxis]:
        draw.line(axis, fill=axis_color, width=axis_width) 
    
    ## axis markers
    marker_length = 12
    
    # xaxis markers
    convert_to_x = lambda i: i / max(all_dist) * (width - left_gap - right_gap) + left_gap
    for i in np.arange(0, max(all_dist), xaxis_step):
        marker_x =  convert_to_x(i)
        marker_y = height - bottom_gap
        draw.line([(marker_x, marker_y), (marker_x, marker_y + marker_length)], fill=axis_color, width=axis_width)
        draw.text((marker_x, marker_y + marker_length*1.5), '{:.0f}'.format(i/1000), fill=axis_color, font=font_labels, anchor='mt')

    # yxis markers
    _y = np.arange(0, max(all_elevation), yaxis_step)
    
    convert_to_y = lambda i:height - (i - min(all_elevation)) / max(all_elevation - min(all_elevation)) * (height - top_gap - bottom_gap - bottom_axis_gap) \
                            - bottom_gap - bottom_axis_gap
    convert_from_y = lambda y: - (y - height + bottom_gap + bottom_axis_gap) * (max(all_elevation - min(all_elevation))) / (height - top_gap - bottom_gap - bottom_axis_gap)\
                            + min(all_elevation)
    
    min_y_w_gap = convert_from_y(height - bottom_gap)
    
    for i in _y[_y > min_y_w_gap]:
        marker_x =  left_gap
        marker_y = convert_to_y(i)
        draw.line([(marker_x, marker_y), (marker_x - marker_length, marker_y)], fill=axis_color, width=axis_width)
        draw.text((marker_x - marker_length*1.5, marker_y ), '{:.0f}'.format(i), fill=axis_color, font=font_labels, anchor='rm')

    draw.text((left_gap + marker_length, top_gap), 'M', font=font_labels, fill=axis_color, anchor='lt')
    draw.text((width-right_gap + marker_length, height - bottom_gap + marker_length*1.5), 'kM', font=font_labels, fill=axis_color, anchor='lt')
        
    gap_line_label = 8
    
    if index >= all_indices[np.argwhere(ydata == min(ydata)).flatten()[0]]:
        draw.line([(xdata[ydata == min(ydata)], min(ydata)), (width, min(ydata))], fill=(255,255,255,130), width=2)
        draw.text((width, min(ydata) + gap_line_label), '{:.0f}  M'.format(max(all_elevation)), fill=color, font=font_labels, anchor='rt')

    if index >= all_indices[np.argwhere(ydata == max(ydata)).flatten()[0]]:
        draw.line([(xdata[ydata == max(ydata)], max(ydata)), (width, max(ydata))], fill=(255,255,255,130), width=2)
        draw.text((width, max(ydata) - gap_line_label), '{:.0f}  M'.format(min(all_elevation)), fill=color, font=font_labels, anchor='rb')

    for br in breaks:
        center_pos = np.array((convert_to_x(br), height-bottom_gap))
        rectangle_size = 15
        rectangle_points = [tuple(center_pos + rectangle_size * i * np.array((1, 1))) for i in [-1,1]]
        draw.rectangle(rectangle_points, fill=color)
        restaurant = Image.open("./track_visualizer/restaurant-{}.png".format(color))
        icon_size = 2 * rectangle_size
        new_size = (icon_size, icon_size)
        restaurant = restaurant.resize(new_size)
        img.paste(restaurant, [int(convert_to_x(br) - icon_size/2), int(height - bottom_gap - rectangle_size - icon_size - 5)], restaurant.convert('RGBA'))

    for rt_label, rt in tests.items():
        center_pos = np.array((convert_to_x(rt), height-bottom_gap))
        ellipse_size = 15
        ellipse_points = [tuple(center_pos + ellipse_size * i * np.array((1, 1))) for i in [-1,1]]
        #draw.ellipse(ellipse_points, fill='red')
        draw_asterisk(draw, center_pos, ellipse_size, width=4, fill='red')
    
    return img, img2


def draw_asterisk(draw_object, center, radius, **kwargs):
    for i in (0, np.sqrt(2)/2, 1, -np.sqrt(2)/2):
        line_points = [tuple(np.array(center) + radius * j * np.array((-i, np.sqrt(1-i**2)))) for j in [1, -1]]
        draw_object.line(line_points, **kwargs)
        