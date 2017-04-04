bl_info = {
    "name": "UMOG",
    "author": "Hirad Sabaghian, Micah Johnston, Marsh Poulson, Jacob Luke",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "Node Editor > UMOG",
    "description": "Mesh Manipulation Tools",
    "warning": "prealpha",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"
}


import bpy
import sys

bpy.types.Scene.StartFrame = bpy.props.IntProperty(
        name = "StartFrame", 
        description = "StartFrame",
        default = 1,
        min = 1)

bpy.types.Scene.EndFrame = bpy.props.IntProperty(
        name = "EndFrame", 
        description = "EndFrame",
        default = 2,
        min = 2)

bpy.types.Scene.SubFrames = bpy.props.IntProperty(
        name = "SubFrames", 
        description = "SubFrames",
        default = 1,
        min = 1)

class MyCustomSocket(bpy.types.NodeSocket):
    # Description string
    '''Custom node socket type'''
    bl_idname = 'CustomSocketType'
    # Label for nice name display
    bl_label = 'Custom Node Socket'
    # Socket color
    bl_color = (1.0, 0.4, 0.216, 0.5)

    def draw(self, context, layout, node, x):
        layout.label(self.name)

    def draw_color(self, context, node):
        return (1,1,1,1)

class HelloWorldPanel(bpy.types.Panel):
    bl_idname = "panel.panel3"
    bl_label = "UMOG"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "UMOG"

    def draw(self, context):
        self.layout.operator("mesh.add_cube_sample", icon='RENDER_RESULT', text="Bake Mesh(es)")
        self.layout.prop(bpy.context.scene, 'StartFrame')
        self.layout.prop(bpy.context.scene, 'EndFrame')
        self.layout.prop(bpy.context.scene, 'SubFrames')

class UMOGNode(bpy.types.Node):
    bl_width_min = 10
    bl_width_max = 5000
    _IsUMOGNode = True
    
    bl_label = "UMOGNode"
    
    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "umog_UMOGNodeTree"
    def create(self):
        pass
    
    def init(self, context):
        print('umog node base init')
        self.create()
			
class UMOGReferenceHolder:
    def __init__(self):
        self.references = {}
        
    def getRef(self, key):
        return references[key]
    
    def addRef(self, key, obj):
        references[key] = obj

class addCubeSample(bpy.types.Operator):
    bl_idname = 'mesh.add_cube_sample'
    bl_label = 'Add Cube'
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        return {"FINISHED"}
			
class UMOGMeshInputNode(UMOGNode):
    bl_idname = "umog_MeshInputNode"
    bl_label = "UMOG Mesh Input Node"

    def init(self,context):
        print('initializing umog node')
        self.inputs.new("CustomSocketType", "My Input")
        self.outputs.new("CustomSocketType", "My Output")
        super().init(context)

class UMOGNodeTree(bpy.types.NodeTree):
    bl_idname = "umog_UMOGNodeTree"
    bl_label = "UMOG"
    bl_icon = "SCULPTMODE_HLT"
    
    def __init__(self):
        self.refs = UMOGReferenceHolder()
        #if the current scene has parameters do nothing otherwise adde the global start and end frames
        

def drawMenu(self, context):
    if context.space_data.tree_type != "umog_UMOGNodeTree": return
    
    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    layout.menu("umog_mesh_menu", text="Mesh", icon = "MESH_DATA")
# from animation nodes
def insertNode(layout, type, text, settings = {}, icon = "NONE"):
    operator = layout.operator("node.add_node", text = text, icon = icon)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
            item = operator.settings.add()
            item.name = name
            item.value = value
    return operator
	
#todo creat the menu class
class UMOGMeshMenu(bpy.types.Menu):
    bl_idname = "umog_mesh_menu"
    bl_label = "Mesh Menu"
    
    def draw(self, context):
            layout = self.layout
            insertNode(layout, "umog_MeshInputNode", "Input Mesh")


def register():
    print("begin resitration")
    bpy.types.NODE_MT_add.append(drawMenu)
    bpy.utils.register_class(HelloWorldPanel)
    bpy.utils.register_class(UMOGNodeTree)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.types.NODE_MT_add.remove(drawMenu)
    bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()
