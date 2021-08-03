from objects.BaseObject import BaseObject

class BasicTurret(BaseObject):
    def __init__(self, dot_map):
        BaseObject.__init__(self, dot_map)
        # 

    @property
    def text_texture(self):
        return """/\\"""