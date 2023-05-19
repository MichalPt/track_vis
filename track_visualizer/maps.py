import os
from PIL import Image
from track_visualizer import converters

class MapsHandler():
    dirs = "{zoom}/{x}/{y}"
    logfile_name = "style.log"
    
    def __init__(self, client, path_tiles_cache):
        self.path_tiles_cache = path_tiles_cache
        self.client = client

        if self.client.active_map is None:
            print("Client has no active maps! Don't forget to add one first!")

    def log_cache_dir_compatibility(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)
            
        logfile_path = os.path.join(path, self.logfile_name)
        style_id = self.client.active_map.style_id
        
        with open(logfile_path, 'w') as file:
            file.write('style_id:{}'.format(style_id))
    
    def check_cache_dir_compatibility(self, path):
        logfile_path = os.path.join(path, self.logfile_name)
        style_id = self.client.active_map.style_id
        
        with open(logfile_path, 'r') as file:
            for line in file:
                if 'style' in line:
                    cached_style_id = line.split(':',1)[1]
        
        assert cached_style_id == style_id, "Directory already contains data for different map style! Change active map label."
        
        
    def save_9tiles(self, lat, lon, zoom):
        x, y, z = converters.deg2num(lat, lon, zoom)
        images = list()
        
        maindir = self.client.active_map.label
        path_cache = os.path.join(self.path_tiles_cache, maindir)
        
        if os.path.isdir(path_cache):
            self.check_cache_dir_compatibility(path_cache)
        else:
            self.log_cache_dir_compatibility(path_cache)
        
        super_tile = Image.new('RGB', (3*1024, 3*1024), (250,250,250))
        
        for i in range(-1,2):
            for j in range(-1,2):
                tile_path = os.path.join(path_cache, self.dirs.format(zoom=z, x=x+i, y=y+j), "tile.png")
                
                if os.path.exists(tile_path):
                    img = Image.open(tile_path)
                else:
                    # url = get_url(xx + i, yy + j, zoom, source=source)
                    # img = get_image(url)
                    img = self.client.get_image(x+i, y+j, z)
                    newdir = os.path.join(path_cache, self.dirs.format(zoom=z, x=x+i, y=y+j))
                    os.makedirs(newdir)
                    img.save(tile_path)
    
                super_tile.paste(img, (1024*(i+1), 1024*(j+1)))
    
        super_tile_path = os.path.join(path_cache, self.dirs.format(zoom=z, x=x, y=y), "supertile.png")
        
        if not os.path.isfile(super_tile_path):
            super_tile.save(super_tile_path, 'PNG')
    
        return super_tile