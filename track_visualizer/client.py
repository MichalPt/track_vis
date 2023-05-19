import requests
from io import BytesIO
from PIL import Image

class MapboxMap():
    def __init__(self, style_id):
        self.style_id = style_id

    def set_map_id(self, map_id):
        self.map_id = map_id

    def set_label(self, label):
        self.label = label


class MapboxClient():
    def __init__(self, username, token):
        self.username = username
        self.token = token
        self.maps = list()
        self.maps_num = 0
        self.active_map = None

    def add_map(self, style_id, label=None):
        if style_id in [m.style_id for m in self.maps]:
            sdict = {m.style_id:m.map_id for m in self.maps}
            smap_id = sdict[style_id]
            print("Map of this style has been already added. It's ID: {map_id}".format(map_id=smap_id))
            self.activate_map(smap_id)
            return
        
        new_map = MapboxMap(style_id)
        new_map.set_map_id(self.maps_num)
        
        if label is None:
            label = 'map{}'.format(new_map.map_id)
        
        new_map.set_label(label)
        
        
        self.maps.append(new_map)
        self.active_map = new_map
        self.maps_num += 1

    def activate_map(self, map_id):
        if map_id >= self.maps_num:
            raise Exception("Requested map doesn't exist. Only these maps ids are available: {}".format(\
                                ', '.join([str(i) for i in list(range(self.maps_num))])))
        
        self.active_map = self.maps[map_id]
        print("Map {map_id}: '{label}' activated.".format(map_id=self.active_map.map_id, label=self.active_map.label))

    def get_url(self, x, y, zoom):
        ### more info: https://docs.mapbox.com/api/maps/static-tiles/
        ### template: https://api.mapbox.com/styles/v1/{username}/{style_id}/tiles/{tilesize}/{z}/{x}/{y}{@2x}

        if self.active_map is None:
            raise Exception("No map is activated! You need to add a map first!")
        
        url = 'https://api.mapbox.com/styles/v1/{username}/{style_id}/tiles/512/{zoom}/{x}/{y}@2x?access_token={token}'.format(\
                username=self.username,
                style_id=self.active_map.style_id,
                zoom=zoom, x=x, y=y,\
                token=self.token,\
               )
        return url

    def get_image(self, x, y, zoom):
        import requests
        from io import BytesIO
        from PIL import Image

        url = self.get_url(x, y, zoom)
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        
        return img