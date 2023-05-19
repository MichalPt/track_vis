import numpy as np
from track_visualizer import converters, tools

class Decoder():
    def __init__(self, gps_file, extension=None, interpolate=True):
        self.gps_file = gps_file

        if extension is None:
            extension = gps_file.split('.')[-1]

        self.extension = extension

        decoders = {'fit':self.read_fit_file, 'gpx':self.read_gpx_file }
        supported_extensions = decoders.keys()
        
        if extension not in supported_extensions:
            raise Exception("Input file has unsopported extension '{}'! Only .{} formats are supported.".format(extension, ', .'.join(supported_extensions)))

        self.decoder = decoders[extension]

        self._data = self.decode()

        if interpolate:
            self.data = self.interpolate_data_linearly(self._data)
        else:
            self.data = self._data
        

    def read_gpx_file(self, path):
        import gpxpy
        import gpxpy.gpx
        
        data = list()
        
        with open(path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            i = 0
            
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        if i ==0 and point.latitude is None:
                            continue
                        time = point.time.time()
                        data.append([i, time, np.array([point.latitude, point.longitude])])
                        i += 1
        return data

    
    def read_fit_file(self, path):
        import fitdecode
        
        data = list()
        i = 0
        
        with fitdecode.FitReader(path) as fit_file:
            for frame in fit_file:
                if isinstance(frame, fitdecode.records.FitDataMessage):
                    out = [i, ]
                    
                    if frame.has_field('timestamp'):
                        timestamp = frame.get_value('timestamp')
                        out.append(timestamp.time())
    
                    if frame.has_field('position_lat') and frame.has_field('position_long'):
                        lat = frame.get_value('position_lat')
                        long = frame.get_value('position_long')
                        out.append(converters.convert_coords(np.array([lat,long])))
                    elif i > 0:
                        out.append(np.array([None,None]))
                    
                    if frame.has_field('speed'):
                        speed = frame.get_value('speed')
                        out.append(speed)
    
                    if len(out) > 2:
                        data.append(out)
                        i += 1
                        
        return data

        
    def decode(self):
        output = self.decoder(self.gps_file)
        return output


    def interpolate_data_linearly(self, input):
        from copy import deepcopy
        
        data = deepcopy(input)
        enriched = list()
        last_line = None
        
        for line in data:
            if last_line == None:
                last_line = line
                enriched.append(line)
                continue
        
            time = last_line[1]
            coords0 = last_line[2]
            coords1 = line[2]
        
            if None in coords1:
                coords1 = last_line[2]
                line = last_line.copy()
                line[0] += 1
                line[1] = tools.add_to_time(time, seconds=1)
            
            new_line = list()
            new_line.append(last_line[0]+0.5)
            new_line.append(time)
            new_line.append(coords0 + (coords1-coords0)/2)
            
            if (len(last_line) == 4) and (len(line) == 4):
                speed0 = last_line[3]
                speed1 = line[3]
                new_line.append(np.mean([speed0,speed1]))
                
            enriched.append(new_line)
            enriched.append(line)
            last_line = line
        
        return enriched