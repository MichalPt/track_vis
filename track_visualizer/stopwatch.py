from track_visualizer import tools
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

class Stopwatch():
    columns = {'test_id':int, 'section_id':int, 'targeted_time':float, 'measured_time':float}
    
    save_format = "RT{:01d}-{:01d}-{:06d}.png"
    save_final_diff = "RT{:01d}-{:01d}-final.png"
    save_label = "RT{:01d}-{:01d}-label.png"
    save_target = "RT{:01d}-{:01d}-target.png"
    
    def __init__(self, text_file_path, path_output, fps=60):
        self.text_file_path = text_file_path
        self.path_output = path_output
        
        test_results = list()
        assert '.txt' in text_file_path
        
        with open(self.text_file_path, 'r') as file:
            for line in file:
                test_results.append({key:typ(val) for (key, typ), val in zip(self.columns.items(), line.split('\t'))})
                
        self.data = test_results
        self.fps = 60

    
    def get_RT_time_frame(self, value, color='white', delta = 16, num_format_1='{:02.0f}', num_format_2='{:02.0f}', font_size=150, figsize=(600,150)):
        img = Image.new('RGBA', figsize, (0,0,0,0))
        draw  = ImageDraw.Draw(img)
        font = ImageFont.truetype("C:/Users/micha/Documents/Software/fonts/DigitalDismay.ttf", font_size)
        font_dot = ImageFont.truetype("C:/Windows/fonts/consola.ttf", font_size)
        draw.text((figsize[0] /2 - delta, font_size), num_format_1.format(np.sign(value) * int(value)), fill=color, font=font, align='right', anchor='rb')
        draw.text((figsize[0] /2 + delta * 1.4, font_size), num_format_2.format(abs((value - int(value))  * 100)), fill=color, font=font, align='left', anchor='lb')
        draw.text((figsize[0] /2, font_size), '.', fill=color, font=font_dot, anchor='mb')
        return img
    
    def render(self, save_video=True, video_settings={'bitrate':'8M', 'fps':60}):
        save_path = tools.anti_overwrite_check(self.path_output)

        if save_path != self.path_output:
            print("Output directory already exists! The output will be forwarded to a new directory '{}' instead.".format(save_path))

        self.path_output = save_path
        
        font_size = 150
        font_path = "C:/Users/micha/Documents/Software/fonts/DigitalDismay.ttf"
        
        figsize=(600,150)
        
        
        for line in tqdm(self.data, desc="RTs & sections"):
            times = np.floor(np.arange(0, line['measured_time'], 1/self.fps, dtype=float)*100)/100
            times = np.append(times, line['measured_time'])
            print(times[-1], line['measured_time'])
            
            test_directory = os.path.join(save_path, 'RT{:01d}'.format(line['test_id']))
            
            if not os.path.isdir(test_directory):
                os.makedirs(test_directory)
        
            for i, time in enumerate(times):
                img = self.get_RT_time_frame(time, color='white',font_size=font_size, figsize=figsize)
                img.save(os.path.join(test_directory, self.save_format.format(line['test_id'], line['section_id'], i)))
        
            img_fin = self.get_RT_time_frame(line['measured_time'] - line['targeted_time'], color='red', num_format_1='{:+03.0f}',font_size = font_size, figsize=figsize)
            img_fin.save(os.path.join(test_directory, self.save_final_diff.format(line['test_id'], line['section_id'])))
        
            img_label = Image.new('RGBA', figsize, (0,0,0,0))
            draw  = ImageDraw.Draw(img_label)
            font = ImageFont.truetype("C:/Users/micha/Documents/Software/fonts/DigitalDismay.ttf", font_size)
            draw.text((figsize[0] /2, font_size), 'f0-f{:d}'.format(line['section_id']), fill='white', font=font, anchor='mb')
            img_label.save(os.path.join(test_directory, self.save_label.format(line['test_id'], line['section_id'])))

            if save_video:
                try:
                    print('Rendering video - times ...')
                    comm = "ffmpeg -r {fps} -i {time_names} -b:v {bitrate} -c:v png -pix_fmt rgba -y {output_file}".format(\
                        fps=video_settings['fps'], \
                        bitrate=video_settings['bitrate'], \
                        time_names=os.path.join(test_directory, self.save_format.replace('{:06d}','%06d').format(line['test_id'], line['section_id'])), \
                        output_file=os.path.join(test_directory, "times-" + 'RT{}-{}.mov'.format(line['test_id'], line['section_id'])) \
                    )
                    print(comm)
                    os.system(comm)
                except:
                    raise Exception("FFMPEG Error!")

            target_time_frame = self.get_RT_time_frame(line['targeted_time'], color='white', font_size=font_size, figsize=figsize)
            target_time_frame.save(os.path.join(test_directory, self.save_target.format(line['test_id'], line['section_id'])))
            