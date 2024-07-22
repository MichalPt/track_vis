import numpy as np
from track_visualizer import tools
from track_visualizer.data import Data

class Track():
    data = Data()
    density = 0
    to_be_masked = False
    distance_shift = 0

    
    def __init__(self, data):
        self._data = data
        #self.distance_shift = 0

    
    def add_to_distance(shift):
        self.distance_shift = shift


    def mask(self, initial_id=None, final_id=None):
        self.to_be_masked = True
        self.mask_ids = [initial_id, final_id]

    
    def unmask(self):
        self.to_be_masked = False
        self.mask_ids = [None, None]

    
    def masked(self, data):
        from_id, to_id = self.mask_ids
        return data[from_id:to_id]

    
    def get_range_suggestions(self, **kwargs):
        return tools.get_range_suggestions(self, **kwargs)

    
    def plot_interval_preview(self, low, high, width=200):
        tools.plot_interval_preview(self, low, high, width=width)


#     def save_as_svg(self, path):
#             rt_id = 1
#     rt_decoder = Decoder("C:/Users/micha/Downloads/rt-{}.gpx".format(rt_id))
# rt_interpolated = Interpolator(rt_decoder, density=0)