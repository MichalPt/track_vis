import os
from PIL import Image, ImageDraw, ImageFont
from track_visualizer import converters, tools
from tqdm import tqdm
import numpy as np

class Visualizer():
    time_frame_filename = "time_{:06d}.png"
    tile_frame_filename = "tile_{:06d}.png"
    
    def __init__(self, mapshandler, reader, path_output, \
                 font_path="C:\Windows\Fonts\Consolas/consolab.ttf", dot_color=(255, 23, 16), \
                 dot_size=19, dot_size_min=5, dot_size_step=1):
                     
        self.mapshandler = mapshandler
        self.reader = reader
        self.path_output = path_output
        self.font_path = font_path
                     
        self.dot_color = dot_color
                     
        self.dot_size = dot_size
        self.dot_size_min = dot_size_min
        self.dot_size_step = dot_size_step

        
    def get_timestamp_frame(self, time, fontsize=110, figsize=(510,100)):
        textimg = Image.new('RGBA', figsize, (10,10,10,0))
        draw  = ImageDraw.Draw(textimg)
        font = ImageFont.truetype(self.font_path, fontsize)
        text = time
        draw.text((1,1), text, fill='black', font=font, align='left')
        
        return textimg

    
    def draw_circle(self, image, size=20, color=(232, 23, 16), loc=(512,512)):
        cx, cy = loc
        cy -= 1
        
        draw = ImageDraw.Draw(image)
        d = size / 2
        draw.ellipse((cx-d, cy-d, cx+d, cy+d), fill=color)

    
    def render(self, zoom, range=None, save_times=True, save_maps=True, for_davinci_resolve=True):
        all_pdxpdy = None
        last_coords = None
        
        #save_path = "C:/Users/micha/Pictures/5RiversClassic_2023/frames-16_10"
        save_path = tools.anti_overwrite_check(self.path_output)

        if save_path != self.path_output:
            print("Output directory already exists! The output will be forwarded to a new directory '{}' instead.".format(save_path))
        
        self.path_output = save_path
        
        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        data = self.reader.data
        length = len(data)

        if range is None:
            range = (0, length)

        i = 1
        
        for line in tqdm(data[range[0]:range[1]]):
            id = line[0]
            coords = line[2]
            
            time = str(tools.add_to_time(line[1], hours=2))
            time_img = self.get_timestamp_frame(time)
        
            super_tile1 = self.mapshandler.save_9tiles(*coords, zoom)
        
            rx, ry = converters.deg2pixcoord(*coords, zoom)
            im1 = super_tile1.crop(tools.get_crop_coords(rx, ry))
            
            if all_pdxpdy is None:
                all_pdxpdy = np.array([0,0], dtype=float)
            else:
                dxdy = coords - last_coords
                dxdy_rel = np.array(converters.degdiff2pixcoord(*coords, zoom)) - np.array(converters.degdiff2pixcoord(*last_coords, zoom))
                all_pdxpdy = np.vstack((all_pdxpdy, [0,0])) + dxdy_rel
        
                xys = np.array([512, 512]) - all_pdxpdy
        
                csize = self.dot_size
                ccol = np.array(self.dot_color)
                
                for xy in xys[::-1]:    
                    self.draw_circle(im1, loc=xy, size=csize, color=tuple(ccol))
                    if csize >= self.dot_size_min:
                        csize -= self.dot_size_step 
                    if ccol[2] <= 80:
                        ccol += np.array([0,2,2]) 
            
            last_coords = coords
            self.draw_circle(im1)

            if for_davinci_resolve:
                suffix = i
            else:
                suffix = tools.format_line_id(id)
        
            if save_maps:
                im1.save(os.path.join(save_path, self.tile_frame_filename.format(suffix)))
            if save_times:
                time_img.save(os.path.join(save_path, self.time_frame_filename.format(suffix)))
            
            i += 1

        print('Done!')
        im1.show()