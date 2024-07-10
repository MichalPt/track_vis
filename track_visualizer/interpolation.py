import numpy as np
from track_visualizer import tools
from functools import partial
from scipy.interpolate import interp1d, Akima1DInterpolator

class Interpolator():
    def __init__(self, decoder, density=4, method='akima', kind='cubic', **kwargs):
        ## density ... number of points to be inserted
        ## order of differential to be interpolated, default is 2 (=acceleration)
        self.decoder = decoder
        self.density = density
        
        self.scipy_methods = {'interp1d':partial(interp1d, kind=kind, axis=0, bounds_error=False, **kwargs),\
                              'akima':partial(Akima1DInterpolator, axis=0, extrapolate=True, **kwargs)}
        self.method = self.scipy_methods[method]
        
        self.data = self.interpolate_data_scipy(data=decoder.data)
        

    def interpolate_data_scipy(self, data, **kwargs):
        id_position_data = list()
        position_data = list()

        id_timestamp_data = list()
        timestamp_data = list()

        id_altitude_data = list()
        altitude_data = list()

        id_speed_data = list()
        speed_data = list()

        id_distance_data = list()
        distance_data = list()

        evaluate_speed = False
        evaluate_altitude = False
        evaluate_distance = False
        evaluate_time = False
        
        for line in data:
            if ('timestamp' in line.keys()) and (line['timestamp'] != None):
                id_timestamp_data.append(line['id'])
                timestamp_data.append(tools.time_to_number(line['timestamp']))
                evaluate_time = True
            
            if None not in line['position']:
                id_position_data.append(line['id'])
                position_data.append(line['position'])

            if ('altitude' in line.keys()) and (line['altitude'] != None):
                id_altitude_data.append(line['id'])
                altitude_data.append(line['altitude'])
                evaluate_altitude = True

            if ('speed' in line.keys()) and (line['speed'] != None):
                id_speed_data.append(line['id'])
                speed_data.append(line['speed'])
                evaluate_speed = True

            if ('distance' in line.keys()) and (line['distance'] != None):
                id_distance_data.append(line['id'])
                distance_data.append(line['distance'])
                evaluate_distance = True
        
        id_initial = data[0]['id']
        id_final = data[-1]['id']
        interpolated_id_data = [float(t) for t in np.arange(id_initial, id_final, 1.0 / (self.density + 1))]
        
        spl_position = self.method(id_position_data, position_data)
        interpolated_position_data = spl_position(interpolated_id_data)
        value_dict = {'id':interpolated_id_data, 'position':interpolated_position_data}
        
        if evaluate_time:
            spl_timestamp = self.method(id_timestamp_data, timestamp_data)
            interpolated_timestamp_data = [tools.number_to_time(t) for t in spl_timestamp(interpolated_id_data)]

            value_dict['timestamp'] = interpolated_timestamp_data
        
        if evaluate_speed:
            spl_speed = self.method(id_speed_data, speed_data)
            interpolated_speed_data = spl_speed(interpolated_id_data)
            value_dict['speed'] = interpolated_speed_data
            
        if evaluate_altitude:
            spl_altitude = self.method(id_altitude_data, altitude_data)
            interpolated_altitude_data = spl_altitude(interpolated_id_data)
            value_dict['altitude'] = interpolated_altitude_data

        if evaluate_distance:
            spl_distance = self.method(id_distance_data, distance_data)
            interpolated_distance_data = spl_distance(interpolated_id_data)
            value_dict['distance'] = np.array(interpolated_distance_data) - interpolated_distance_data[0]

        new_data = list()

        for i in range(len(interpolated_id_data)):
            line = {}
            
            for key, value_list in value_dict.items():
                line[key] = value_list[i]
                
            new_data.append(line)

        return new_data

    
    ## later should be put into a class parent to Interpolator and Decoder
    def get_range_suggestions(self, **kwargs):
        return tools.get_range_suggestions(self, **kwargs)

    
    ## later should be put into a class parent to Interpolator and Decoder
    def plot_interval_preview(self, low, high, width=200):
        tools.plot_interval_preview(self, low, high, width=width)




        

        