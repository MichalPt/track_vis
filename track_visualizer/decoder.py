import numpy as np
from track_visualizer import converters, tools, data

class Decoder():
    data = data.Data()
    density = 0
    
    def __init__(self, gps_file, extension=None):
        self.gps_file = gps_file

        if extension is None:
            extension = gps_file.split('.')[-1]

        self.extension = extension
        self.to_be_masked = False

        decoders = {'fit':self.read_fit_file, 'gpx':self.read_gpx_file }
        supported_extensions = decoders.keys()
        
        if extension not in supported_extensions:
            raise Exception("Input file has unsopported extension '{}'! Only .{} formats are supported.".format(extension, ', .'.join(supported_extensions)))

        self.decoder = decoders[extension]

        self._data = self.decode()
        

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
                        dc = {}
                        if i == 0 and point.latitude is None:
                            continue
                        if point.time is not None:
                            time = point.time.time()
                            dc['timestamp'] = time
                            
                        #data.append({'id':i, 'timestamp':time, 'position':np.array([point.latitude, point.longitude])})
                        dc.update({'id':i, 'position':np.array([point.latitude, point.longitude])})
                        data.append(dc)
                        i += 1
        return data

    
    def read_fit_file(self, path):
        import fitdecode
        
        data = list()
        i = 0
        out = {}
        
        with fitdecode.FitReader(path) as fit_file:
            for frame in fit_file:
                if isinstance(frame, fitdecode.records.FitDataMessage):
                    if frame.has_field('timestamp'):
                        out = {'id':i}
                        timestamp = frame.get_value('timestamp')
                        out['timestamp'] = timestamp.time()
    
                        if frame.has_field('position_lat') and frame.has_field('position_long'):
                            lat = frame.get_value('position_lat')
                            long = frame.get_value('position_long')
                            out['position'] = converters.convert_coords(np.array([lat,long]))
                        else:
                            out['position'] = np.array([None,None])
                    
                        other_fields_to_extract = ['altitude', 'speed', 'distance']
                        
                        for field_name in other_fields_to_extract:
                            if frame.has_field(field_name):
                                value = frame.get_value(field_name)
                                out[field_name] = value
                            else:
                                out[field_name] = None
    
                    if len(out) > 2:
                        data.append(out)
                        i += 1
                        
        return data

        
    def decode(self):
        output = self.decoder(self.gps_file)
        return output

    
    def mask(self, initial_id=None, final_id=None):
        self.to_be_masked = True
        self.mask_ids = [initial_id, final_id]

    
    def unmask(self):
        self.to_be_masked = False
        self.mask_ids = [None, None]

    
    def masked(self, data):
        from_id, to_id = self.mask_ids
        return data[from_id:to_id]
        
    # ## deprecated
    # def interpolate_data_linearly(self, input):
    #     from copy import deepcopy
        
    #     data = deepcopy(input)
    #     enriched = list()
    #     last_line = None
        
    #     for line in data:
    #         if last_line == None:
    #             last_line = line
    #             enriched.append(line)
    #             continue
        
    #         time = last_line['timestamp']
    #         coords0 = last_line['position']
    #         coords1 = line['position']
        
    #         if None in coords1:
    #             coords1 = last_line['position']
    #             line = last_line.copy()
    #             line[0] += 1
    #             line[1] = tools.add_to_time(time, seconds=1)
            
    #         new_line = list()
    #         new_line.append(last_line['id']+0.5)
    #         new_line.append(time)
    #         new_line.append(coords0 + (coords1-coords0)/2)
            
    #         if (len(last_line) == 4) and (len(line) == 4):
    #             speed0 = last_line['speed']
    #             speed1 = line['speed']
    #             new_line.append(np.mean([speed0,speed1]))
                
    #         enriched.append(new_line)
    #         enriched.append(line)
    #         last_line = line
        
    #     return enriched

    # ## deprecated
    # def interpolate_data(self, input, n=4):
    #     from copy import deepcopy
        
    #     data = deepcopy(input)
    #     enriched = list()
    #     last_line = None

    #     #n_range = list(range(n))
        
    #     for line in data:
    #         if last_line == None:
    #             last_line = line
    #             #enriched.append(line)
    #             continue
        
    #         time = last_line['timestamp']
    #         coords0 = last_line['position']
    #         coords1 = line['position']
        
    #         if None in coords1:
    #             coords1 = last_line['position']
    #             line = last_line.copy()
    #             line['id'] += 1
    #             line['timestamp'] = tools.add_to_time(time, seconds=1)

    #         for nn in range(n):
    #             new_line = list()
    #             new_line.append(last_line['id'] + nn/n)
    #             new_line.append(time)
    #             new_line.append(coords0 + (coords1-coords0)*nn/n)
                
    #             if (len(last_line) == 4) and (len(line) == 4):
    #                 speed0 = last_line['speed']
    #                 speed1 = line['speed']
    #                 new_line.append(np.mean([speed0, speed1]))
                
    #             enriched.append(new_line)
                
    #         #enriched.append(line)
    #         last_line = line
        
    #     return enriched

    
    ## later should be put into a class parent to Interpolator and Decoder
    def get_range_suggestions(self, **kwargs):
        return tools.get_range_suggestions(self, **kwargs)

    
    ## later should be put into a class parent to Interpolator and Decoder
    def plot_interval_preview(self, low, high, width=200):
        tools.plot_interval_preview(self, low, high, width=width)