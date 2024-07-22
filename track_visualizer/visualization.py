import os
from PIL import Image, ImageDraw, ImageFont
from track_visualizer import converters, tools, ranging, elevation, track
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

class Visualizer():
    time_frame_filename = "time_{:06d}.png"
    tile_frame_filename = "tile_{:06d}.png"
    alti_frame_filename = "alti_{:06d}.png"
    dist_frame_filename = "dist_{:06d}.png"
    
    def __init__(self, mapshandler, reader, path_output, \
                 font_path="C:/Users/micha/Documents/Software/fonts/DigitalDismay.ttf", \
                 #font_path="C:\Windows\Fonts\Consolas/consolab.ttf", \
                 dot_color=(255, 23, 16, 255), \
                 dot_size=19, dot_size_min=6, dot_size_step=4):
                     
        self.mapshandler = mapshandler
        self.reader = reader
        self.path_output = path_output
        self.font_path = font_path
                     
        self.dot_color = dot_color
                     
        self.dot_size = dot_size
        self.dot_size_min = dot_size_min

        self.index_density = reader.density
        self.dot_size_step = dot_size_step / (self.index_density + 1)

        self.dot_alpha_step = 10

        self.all_id_data = [line['id'] for line in reader.data]

        
    # def get_timestamp_frame(self, time, fontsize=110, figsize=(510,100)):
    #     textimg = Image.new('RGBA', figsize, (10,10,10,0))
    #     draw  = ImageDraw.Draw(textimg)
    #     font = ImageFont.truetype(self.font_path, fontsize)
    #     text = time
    #     draw.text((1,1), text, fill='black', font=font, align='left')
        
    #     return textimg

    def get_elevation_frame(self, elevation, fontsize=110, figsize=(900,700), color='white'):
        img = Image.new('RGBA', figsize, (10,10,10,0))
        draw  = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_path, fontsize)
        text = "{} m".format(time)
        draw.text((1,1), text, fill=color, font=font, align='center')
        
        return img

    
    #def draw_circle(self, image, size=20, color=(232, 23, 16), loc=(512,512)):
    def draw_circle(self, image, size=20, color=(232, 23, 16, 255), loc=(512,512)):
        cx, cy = loc
        cy -= 1
        
        #draw = ImageDraw.Draw(image)
        draw = ImageDraw.Draw(image, mode='RGBA')
        d = size / 2
        draw.ellipse((cx-d, cy-d, cx+d, cy+d), fill=color)
        

    def draw_lines(self, image, size=9, color=(232, 23, 16), locs=[(512,512),(511,511)]):        
        draw = ImageDraw.Draw(image, mode='RGBA')
        draw.line(locs, fill=color, width=int(size), joint='curve')
    
    def draw_lines_v2(self, image, size=9, color=(232, 23, 16), locs=[(512,512),(511,511)]):
        col_layer = Image.new('RGB', (1024, 1024), color[:3])
        mask = Image.new('L', (1024, 1024), 255)
        
        draw = ImageDraw.Draw(mask)
        #draw = ImageDraw.Draw(image, mode='RGBA')
        alpha = color[3] if len(color) == 4 else 165
            
        draw.line(locs, fill=alpha, width=int(size), joint='curve')

        image.paste(Image.composite(image, col_layer, mask))
        #image.paste(col_layer, (100,100))
        
    def render(self, zoom, ranges=(None,None), save_maps=True, for_davinci_resolve=True,\
               save_times=True, time_offset=[2,0,0], color='white', \
               save_video=True, video_settings={'codec':'hevc', 'bitrate':'8M', 'fps':20},\
               save_ids=True, save_elevation=True,\
               breaks=[], tests={}, underlay=[],\
               ):

        ranges = ranging.Range(*ranges)
        ranges * (self.index_density + 1)

        if issubclass(type(underlay), track.Track):
            underlay_data = [line['position'] for line in underlay.data]
        elif type(underlay) is list:
            underlay_data = underlay
        else:
            underlay_data = []

        fps = video_settings['fps'] * (self.index_density + 1)
        
        all_pdxpdy = None
        last_coords = None

        self.dot_size_min = self.dot_size_min + zoom - 13
        self.dot_size = 3 * self.dot_size_min
        
        if save_elevation:
            all_elevation_data = [line['altitude'] for line in self.reader.data]
            all_distance_data = np.array([line['distance'] for line in self.reader.data])
        
        save_path = tools.anti_overwrite_check(self.path_output)

        if save_path != self.path_output:
            print("Output directory already exists! The output will be forwarded to a new directory '{}' instead.".format(save_path))

        self.path_output = save_path
        
        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        data = self.reader.data
        #ranges = np.array(ranges)

        i = 1
        
        for line in tqdm(data[ranges[0]:ranges[1]]):
            id = line['id']
            coords = line['position']

            assert len(time_offset) == 3 and type(time_offset) == list
            off_hours, off_minutes, off_seconds = time_offset
            time = str(tools.add_to_time(line['timestamp'], hours=off_hours, minutes=off_minutes, seconds=off_seconds))
            time_img = tools.get_timestamp_frame(time, font_path=self.font_path, color=color)

            if save_maps:
                super_tile1 = self.mapshandler.save_9tiles(*coords, zoom)
            
                rx, ry = converters.deg2pixcoord(*coords, zoom)
                im1 = super_tile1.crop(tools.get_crop_coords(rx, ry))
                
                if len(underlay_data) > 0:
                    under_locs = np.array([np.array(converters.degdiff2pixcoord(*ulocs, zoom)) for ulocs in underlay_data])
                    
                    under_locs_rel = np.array([512, 512]) - np.array(converters.degdiff2pixcoord(*coords, zoom)) + under_locs
                    u_locs = [tuple(xy) for xy in under_locs_rel]
                    self.draw_lines_v2(im1, locs=u_locs, color=(3, 252, 237, 70), size=32)
                    
                
                if save_maps is False:
                    pass
                elif all_pdxpdy is None:
                    all_pdxpdy = np.array([0,0], dtype=float)
                else:
                    #dxdy = coords - last_coords
                    dxdy_rel = converters.degdiff2pixcoord(*coords, zoom) - np.array(converters.degdiff2pixcoord(*last_coords, zoom))
                    all_pdxpdy = np.vstack((all_pdxpdy, [0,0])) + dxdy_rel
            
                    xys = np.array([512, 512]) - all_pdxpdy
            
                    csize = self.dot_size
                    ccol = np.array(self.dot_color)
                    
                    off_screen = False
                    
                    for xy in xys[::-1]:  
                        if (np.array(xy) > 512*2).any() or (np.array(xy) < 0).any():
                            off_screen = True
                            continue
                            
                        if not off_screen:
                            self.draw_circle(im1, loc=xy, size=csize, color=tuple(ccol))
    
                        if csize >= self.dot_size_min:
                            csize -= self.dot_size_step 
                        if ccol[2] <= 80:
                            ccol += np.array([0,2,2,0])
                        if ccol[3] > self.dot_alpha_step:
                            ccol -= np.array([0,0,0,self.dot_alpha_step])
                        else:
                            ccol[3] = 0 
    
                        last_xy = xy
    
                    locs = [tuple(x) for x in xys]
                    locs.append((512,512))
                    #self.draw_lines(im1, locs=locs, color=(232, 23, 16, 90), size=self.dot_size_min+2)
                    self.draw_lines_v2(im1, locs=locs, color=(232, 23, 16), size=self.dot_size_min+2)

            if save_maps:
                last_coords = coords
                self.draw_circle(im1, size=self.dot_size)

            if for_davinci_resolve:
                suffix = i
            else:
                suffix = tools.format_line_id(id)

            if save_maps:
                im1.save(os.path.join(save_path, self.tile_frame_filename.format(suffix)))
            if save_times:
                time_img.save(os.path.join(save_path, self.time_frame_filename.format(suffix)))
            if save_ids:
                with open(os.path.join(save_path, "indexes.txt"), 'a') as textfile:
                    textfile.write("ID {}   {}\n".format(id, self.tile_frame_filename.format(suffix)))
            if save_elevation:
                elevation_frames = elevation.get_elevation_frame(id, self.all_id_data, all_distance_data, all_elevation_data,\
                                                                 figsize=(1700,600), color=color,\
                                                                 xaxis_step=50000, yaxis_step=200,\
                                                                 breaks=breaks, tests=tests)
                elevation_frames[0].save(os.path.join(save_path, self.dist_frame_filename.format(suffix)))
                elevation_frames[1].save(os.path.join(save_path, self.alti_frame_filename.format(suffix)))
            
            i += 1
            
        if save_video:
            basename = os.path.basename(save_path)
            
            try:
                if save_maps:
                    print('Rendering video - maps ...')
                    comm = "ffmpeg -r {fps} -i {tile_names} -b:v {bitrate} -c:v {codec} -vf format=yuv420p10le -y {output_file}".format(\
                        fps=fps, \
                        bitrate=video_settings['bitrate'], \
                        codec=video_settings['codec'], \
                        tile_names=os.path.join(save_path, self.tile_frame_filename.replace('{:','%').replace('}','')), \
                        output_file=os.path.join(save_path, "video-" + basename + '.mov') \
                    )
                    #print(comm)
                    os.system(comm)

                if save_times:
                    print('Rendering video - times ...')
                    os.system("ffmpeg -r {fps} -i {time_names} -b:v {bitrate} -c:v png -pix_fmt rgba -y {output_file}".format(\
                        fps=fps, \
                        bitrate=video_settings['bitrate'], \
                        time_names=os.path.join(save_path, self.time_frame_filename.replace('{:','%').replace('}','')), \
                        output_file=os.path.join(save_path, "times-" + basename + '.mov') \
                    ))

                if save_elevation:
                    print('Rendering video - elevation & distance ...')
                    os.system("ffmpeg -r {fps} -i {alti_names} -b:v {bitrate} -c:v png -pix_fmt rgba -y {output_file}".format(\
                        fps=fps, \
                        bitrate=video_settings['bitrate'], \
                        alti_names=os.path.join(save_path, self.alti_frame_filename.replace('{:','%').replace('}','')), \
                        output_file=os.path.join(save_path, "altitude-" + basename + '.mov') \
                    ))
                    os.system("ffmpeg -r {fps} -i {dist_names} -b:v {bitrate} -c:v png -pix_fmt rgba -y {output_file}".format(\
                        fps=fps, \
                        bitrate=video_settings['bitrate'], \
                        dist_names=os.path.join(save_path, self.dist_frame_filename.replace('{:','%').replace('}','')), \
                        output_file=os.path.join(save_path, "distance-" + basename + '.mov') \
                    ))
            except:
                raise Exception("FFMPEG Error!")

        print('Done!')
        
        if save_maps:
            im1.show()

    
    def render_elevation_frames(self, save_videos=True, njobs=12, verbose=0,\
                                figsize=(1700,600), xaxis_step=50000, yaxis_step=200, \
                                breaks=[], tests={}, stage_ranges={}):
        from joblib import Parallel, delayed
        from tqdm import tqdm
        
        save_path = tools.anti_overwrite_check(self.path_output)

        if save_path != self.path_output:
            print("Output directory already exists! The output will be forwarded to a new directory '{}' instead.".format(save_path))

        self.path_output = save_path
        
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        
        all_elevation_data = [line['altitude'] for line in self.reader.data]
        all_distance_data = np.array([line['distance'] for line in self.reader.data])

        def process_elevation_frame(index, i):
            elevation_frames = elevation.get_elevation_frame(index, self.all_id_data, all_distance_data, all_elevation_data,\
                                                             figsize=figsize, \
                                                             xaxis_step=xaxis_step, yaxis_step=yaxis_step,\
                                                             breaks=breaks, tests=tests)
            
            elevation_frames[0].save(os.path.join(save_path, self.dist_frame_filename.format(i)))
            elevation_frames[1].save(os.path.join(save_path, self.alti_frame_filename.format(i)))

        results = [r for r in tqdm(Parallel(n_jobs=njobs, verbose=verbose, prefer="threads", return_as='generator', require='sharedmem')(delayed(process_elevation_frame)(index, i) for i, index in enumerate(self.all_id_data)), total=len(self.all_id_data))]

        for i, index in enumerate(self.all_id_data):
            with open(os.path.join(save_path, "indexes.txt"), 'a') as textfile:
                textfile.write("ID {}   {}\n".format(index, self.alti_frame_filename.format(i)))
        
        if save_videos:
            print('Rendering video - elevation & distance ...')
            os.system("ffmpeg -r {fps} -i {alti_names} -b:v {bitrate} -c:v png -pix_fmt rgba -y {output_file}".format(\
                fps=fps, \
                bitrate=video_settings['bitrate'], \
                alti_names=os.path.join(save_path, self.alti_frame_filename.replace('{:','%').replace('}','')), \
                output_file=os.path.join(save_path, 'altitude.mov') \
            ))
            os.system("ffmpeg -r {fps} -i {dist_names} -b:v {bitrate} -c:v png -pix_fmt rgba -y {output_file}".format(\
                fps=fps, \
                bitrate=video_settings['bitrate'], \
                dist_names=os.path.join(save_path, self.dist_frame_filename.replace('{:','%').replace('}','')), \
                output_file=os.path.join(save_path, 'distance.mov') \
            ))

            # video_stage_comm = "ffmpeg -r {fps} -start_number {start} -i {dist_names} -b:v {bitrate} -c:v png -pix_fmt rgba -frames:v {number_of_frames} -y {output_file}"

            # for stage_id, r in stage_ranges.items():
            #     os.system(video_stage_comm.format(fps=fps, \
            #     bitrate=video_settings['bitrate'], \
            #     dist_names=os.path.join(save_path, self.dist_frame_filename.replace('{:','%').replace('}','')), \
            #     output_file=os.path.join(save_path, 'video-distances-etapa-{stage_id}.mov'.format(stage_id))\
            #     ))
            
        print('Done!')
        