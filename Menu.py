from pygame import Rect

def menu_builder(name: str, index: int, action, **kwargs):
    menu_item = menu_switch[name]
    return menu_item(index, action, **kwargs)

def end_turn(i, action, **kwargs):
    return MenuItem(
        # x, y, w, h, name, caption, action
        20, 20 + (i * 20) + (i * 64), 160 - 40, 64, "end_turn", "End Turn", action,
        **kwargs
    )

menu_switch = {
    "end_turn": end_turn
}

class MenuItem(Rect):
    def __init__(self, x, y, w, h, *args, **kwargs):
        Rect.__init__(self, x, y, w, h)

        self.name = args[0]
        self.caption = args[1]

        self._action = args[2]
        self._kwargs = kwargs

    def action(self):
        return self._action(**self._kwargs)
