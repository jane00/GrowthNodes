import bpy
from bpy.types import NodeSocket

class TextureSocket(NodeSocket):
    # Description string
    '''Custom Texture socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'TextureSocketType'
    # Label for nice name display
    bl_label = 'Texture Socket'

    objectName = bpy.props.StringProperty()

    texture_index = bpy.props.IntProperty()

    def init(self, context):
        pass

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    # Socket color
    def draw_color(self, context, node):
        return (0, 0, 1, 0.5)

    # these will return a reference to the bind point adn index for passing parameters
    def get_bind_index(self):
        return 'texture_index'