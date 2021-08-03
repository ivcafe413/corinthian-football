from abc import ABC, abstractmethod

class BaseObject(ABC):
    def __init__(self, dot_map):
        # Game Board-relative coordinates
        self.x = dot_map.x
        self.y = dot_map.y

        self.name = dot_map.name or self.__class__.__name__
        self.hp = dot_map.hp or 1
        
        self.info_list = ["name", "hp"] # List of parameters to display in informational panels

        # 
        self.render_mode = "texture" # 'texture', 'shape', 'sprite'
        self.text_texture = """0""" #

    # @property
    # def render_mode(self):
    #     return self._render_mode 

    # @property
    # def text_texture(self):
    #     return self._text_texture

    @abstractmethod
    def update(self):
        """ Called each frame for Game Object to update itself """
        pass # Abstract