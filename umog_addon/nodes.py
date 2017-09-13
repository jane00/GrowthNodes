import bpy
import bmesh
import copy
import numpy as np
import pyximport
pyximport.install()
from . events import events

# try:
#     PYDEV_SOURCE_DIR = "/usr/lib/eclipse/plugins/org.python.pydev_5.6.0.201703221358/pysrc"
#     import sys
#     if PYDEV_SOURCE_DIR not in sys.path:
#         sys.path.append(PYDEV_SOURCE_DIR)
#     import pydevd
#     print("debugging enabled")
# except:
#     print("no debugging enabled")
    
#begin base node classes

class UMOGNode(bpy.types.Node):
    bl_width_min = 10
    bl_width_max = 5000

    _IsUMOGNode = True
    
    bl_label = "UMOGNode"
    
    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "umog_UMOGNodeTree"
    
    def init(self, context):
        print('umog node base init')
    #this will be called when the node is executed by bake meshes
    #will be called each iteration
    def execute(self, refholder):
        pass
    #will be called once before the node will be executed by bake meshes
    #refholder is passed to this so it can register any objects that need it
    def preExecute(self, refholder):
        pass
    #will be called once at the end of each frame
    def postFrame(self, refholder):
        pass
    #will be called once right before bake returns
    def postBake(self, refholder):
        pass

# the base class for pure sink nodes
class UMOGOutputNode(UMOGNode):
    _OutputNode = True
    def init(self, context):
        super().init(context)

#end base node classes

#BEGIN: UMOG_NODES
class TextureAlternatorNode(UMOGNode):
    bl_idname = "umog_TextureAlternatorNode"
    bl_label = "UMOG Texture Alternator"
    
    def init(self, context):
        self.inputs.new("TextureSocketType", "Texture0")
        self.inputs.new("TextureSocketType", "Texture1")
        self.inputs.new("IntegerSocketType", "Integer0")
        self.outputs.new("TextureSocketType", "Output")
        super().init(context)

    def execute(self, refholder):
        try:
            counter_index = self.inputs[2].links[0].to_socket.integer_value
        except:
            print("no integer as input")
        
        if (counter_index %2) == 0:
            try:
                fn = self.inputs[0].links[0].from_socket
                self.outputs[0].texture_index = fn.texture_index
                print("use texture 0")
            except:
                print("no texture as input")
        else:
            try:
                fn = self.inputs[1].links[0].from_socket
                self.outputs[0].texture_index = fn.texture_index
                print("use texture 1")
            except:
                print("no texture as input")

class IntegerNode(UMOGNode):
    bl_idname = "umog_IntegerNode"
    bl_label = "UMOG Integer"
    
    input_value = bpy.props.IntProperty()
    
    def init(self, context):
        self.outputs.new("IntegerSocketType", "Integer0")
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "input_value", text="Value")


    def preExecute(self, refholder):
        #consider saving the result from this
        self.outputs[0].integer_value = self.input_value

class IntegerFrameNode(UMOGNode):
    bl_idname = "umog_IntegerFrameNode"
    bl_label = "UMOG Integer Frame"
    
    def init(self, context):
        self.outputs.new("IntegerSocketType", "Integer0")
        self.outputs[0].integer_value = 0
        super().init(context)
    
    def preExecute(self, refholder):
        self.outputs[0].integer_value = 0
    
    def execute(self, refholder):
        pass
        
    def postFrame(self, refholder):
        self.outputs[0].integer_value = self.outputs[0].integer_value + 1
        print("Frame Counter " + str(self.outputs[0].integer_value))
        
class IntegerSubframeNode(UMOGNode):
    bl_idname = "umog_IntegerSubframeNode"
    bl_label = "UMOG Integer Subframe"
    
    def init(self, context):
        self.outputs.new("IntegerSocketType", "Integer0")
        self.outputs[0].integer_value = 0
        super().init(context)
    
    def preExecute(self, refholder):
        self.outputs[0].integer_value = 0
    
    def execute(self, refholder):
        self.outputs[0].integer_value = self.outputs[0].integer_value + 1
        print("Subrame Counter " + str(self.outputs[0].integer_value))
        
    def postFrame(self, refholder):
        self.outputs[0].integer_value = 0

class IntegerMathNode(UMOGNode):
    bl_idname = "umog_IntegerMathNode"
    bl_label = "UMOG Integer Math"
    
    fixed_items = bpy.props.EnumProperty(items= 
        (('0', '+', 'addition'),    
        ('1', '-', 'subtraction'),    
        ('2', '*', 'multiplication'),    
        ('3', '/', 'division'),
        ('4', '^', 'exponentiation'),
        ('5', '%', 'modulus'),
        ),
        name = "fixed list") 
    
    def init(self, context):
        self.outputs.new("IntegerSocketType", "Integer0")
        self.inputs.new("IntegerSocketType", "Integer0")
        self.inputs.new("IntegerSocketType", "Integer0")
        self.outputs[0].integer_value = 0
        super().init(context)
    
    def execute(self, refholder):
        if self.fixed_items == '0':
            print("addition")
            self.outputs[0].integer_value = (self.inputs[0].links[0].from_socket.integer_value +
                self.inputs[1].links[0].from_socket.integer_value)
        elif self.fixed_items == '1':
            print("subtraction")
            self.outputs[0].integer_value = (self.inputs[0].links[0].from_socket.integer_value - 
                self.inputs[1].links[0].from_socket.integer_value)
        elif self.fixed_items == '2':
            print("multiplication")
            self.outputs[0].integer_value = (self.inputs[0].links[0].from_socket.integer_value * 
                self.inputs[1].links[0].from_socket.integer_value)
        elif self.fixed_items == '3':
            print("division")
            try:
                self.outputs[0].integer_value = (self.inputs[0].links[0].from_socket.integer_value / 
                    self.inputs[1].links[0].from_socket.integer_value)
            except:
                print("div by zero")
        elif self.fixed_items == '4':
            print("exponentiation")
            self.outputs[0].integer_value = (self.inputs[0].links[0].from_socket.integer_value ^ 
                self.inputs[1].links[0].from_socket.integer_value)
        elif self.fixed_items == '5':
            print("modulus")
            try:
                self.outputs[0].integer_value = (self.inputs[0].links[0].from_socket.integer_value % 
                    self.inputs[1].links[0].from_socket.integer_value)
            except:
                print("mod by zero")
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "fixed_items", 'Operation')


class UMOGNoiseGenerationNode(UMOGNode):
    bl_idname = "umog_NoiseGenerationNode"
    bl_label = "UMOG Noise Generation Node"
    
    def init(self, context):
        print('initializing umog noise node')
        self.inputs.new("NodeSocketInt", "X")
        self.inputs.new("NodeSocketInt", "Y")
        self.inputs.new("NodeSocketInt", "Z")
        self.outputs.new("NodeSocketInt", "Output")
        super().init(context)
        
    def execute(self, refholder):
        print("noise node execution")

class GetTextureNode(UMOGNode):
    bl_idname = "umog_GetTextureNode"
    bl_label = "Get Texture Node"

    texture = bpy.props.StringProperty()

    def init(self, context):
        self.outputs.new("TextureSocketType", "Output")
        super().init(context)

    def draw_buttons(self, context, layout):
        #layout.operator("umog.select_texture", text = "Select Texture").pnode = self.name
        layout.prop_search(self, "texture", bpy.data, "textures", icon="TEXTURE_DATA", text="")
        try:
            #only one template_preview can exist per screen area https://developer.blender.org/T46733
            #make sure that at most one preview can be opened at any time
            if self.select and (len(bpy.context.selected_nodes) == 1):
                layout.template_preview(bpy.data.textures[self.texture])
        except:
            pass

    def update(self):
        pass
    
    def execute(self, refholder):
        #print("get texture node execution, texture: " + self.texture)
        #print("texture handle: " + str(self.outputs[0].texture_index))
        #print(refholder.np2dtextures[self.outputs[0].texture_index])
        pass
        
    def preExecute(self, refholder):
        #consider saving the result from this
        self.outputs[0].texture_index = refholder.getRefForTexture2d(self.texture)
        
class SetTextureNode(UMOGOutputNode):
    bl_idname = "umog_SetTextureNode"
    bl_label = "Set Texture Node"

    texture = bpy.props.StringProperty()

    texture_index = bpy.props.IntProperty()
    def init(self, context):
        self.inputs.new("TextureSocketType", "Input")
        super().init(context)

    def draw_buttons(self, context, layout):
        #layout.operator("umog.select_texture", text = "Select Texture").pnode = self.name
        layout.prop_search(self, "texture", bpy.data, "textures", icon="TEXTURE_DATA", text="")
        try:
            #only one template_preview can exist per screen area https://developer.blender.org/T46733
            #make sure that at most one preview can be opened at any time
            if self.select and (len(bpy.context.selected_nodes) == 1):
                layout.template_preview(bpy.data.textures[self.texture])
        except:
            pass

    def update(self):
        pass
    
    def execute(self, refholder):
        refholder.np2dtextures[self.texture_index] = copy.deepcopy(refholder.np2dtextures[self.inputs[0].links[0].from_socket.texture_index])
        print("setting texture " + str(self.texture_index) + " " + str(self.inputs[0].links[0].from_socket.texture_index))
        pass
        
    def preExecute(self, refholder):
        #consider saving the result from this
        self.texture_index = refholder.getRefForTexture2d(self.texture)
        
class SaveTextureNode(UMOGOutputNode):
    bl_idname = "umog_SaveTextureNode"
    bl_label = "Save Texture Node"
    
    temp_texture_prefix = "__umog_texture_saver_"
    texture_name_temp = bpy.props.StringProperty()
    file_path = bpy.props.StringProperty(subtype = 'DIR_PATH')
    file_name = bpy.props.StringProperty(default="img")
    
    file_name_diff = bpy.props.IntProperty()

    texture_index = bpy.props.IntProperty()
    def init(self, context):
        self.inputs.new("TextureSocketType", "Input")
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "file_path", text="Path")
        layout.prop(self, "file_name", text="File Name")

    def update(self):
        pass
    
    def execute(self, refholder):
        refholder.handleToImage(self.inputs[0].links[0].from_socket.texture_index, bpy.data.images[self.texture_name_temp])
        image = bpy.data.images[self.texture_name_temp]
        image.filepath_raw = self.file_path + self.file_name + str(self.file_name_diff) + ".png"
        image.file_format = 'PNG'
        image.save()
        self.file_name_diff = self.file_name_diff + 1
        pass
        
    def preExecute(self, refholder):
        self.file_name_diff = 0
        image = bpy.data.images.new(self.temp_texture_prefix + self.name, width=bpy.context.scene.TextureResolution, height=bpy.context.scene.TextureResolution)
        self.texture_name_temp = image.name
        cTex = bpy.data.textures.new(self.temp_texture_prefix + self.name, type = 'IMAGE')
        cTex.image = image
        print("texture name: " + self.texture_name_temp)
        pass
        
    def postBake(self, refholder):
        bpy.data.textures.remove(bpy.data.textures[self.texture_name_temp])
        bpy.data.images.remove(bpy.data.images[self.texture_name_temp])
        pass

#begin mesh manipulation nodes
class SculptNode(UMOGOutputNode):
    bl_idname = "umog_SculptNode"
    bl_label = "Sculpt Node"

    mesh_name = bpy.props.StringProperty()
    stroke_pressure = bpy.props.FloatProperty(min=0.0001, max=2.0, default=1.0)
    stroke_size = bpy.props.IntProperty(default=44)
    dyntopo_detail = bpy.props.FloatProperty(min=0.1, max=5, default=1.5, precision=1)
    
    def init(self, context):
        #self.inputs.new("BaseInputSocketType", "Input")
        super().init(context)

    def draw_buttons(self, context, layout):
        #layout.operator("umog.select_mesh", text = "Select Mesh").pnode = self.name
        layout.prop_search(self, "mesh_name", bpy.data, "objects", icon="MESH_CUBE", text="")
        layout.prop(self, "stroke_pressure", text="Stroke Pressure")
        layout.prop(self, "stroke_size", text="Stroke Size")
        layout.prop(self, "dyntopo_detail", text="Precision Level")

    def update(self):
        pass
    
    def execute(self, refholder):
        #print("sculpt node execution, mesh: " + self.mesh_name)            
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[self.mesh_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[self.mesh_name]

        for area in bpy.context.screen.areas:
            #print(area.type)
            if area.type == 'VIEW_3D':
                ctx = bpy.context.copy()
                ctx['area'] = area
                ctx['region'] = area.regions[-1]

                bpy.ops.view3d.view_selected(ctx)

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.normals_make_consistent()
                
                bpy.ops.object.mode_set(mode = 'SCULPT')
                
                bpy.data.brushes["SculptDraw"].stroke_method = "DOTS"
                bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
                
                if not bpy.context.sculpt_object.use_dynamic_topology_sculpting:
                    bpy.ops.sculpt.dynamic_topology_toggle()
                    bpy.context.scene.tool_settings.sculpt.detail_type_method = 'CONSTANT'
                    bpy.context.scene.tool_settings.sculpt.constant_detail = self.dyntopo_detail

                obj = bpy.context.active_object
                verts = list(obj.data.vertices)

                mouse_width = int(area.width/2)
                mouse_height = int(area.height/2)

                for vert in verts:
                    bpy.ops.sculpt.brush_stroke(ctx, stroke=[{
                        "name": "first",
                        "mouse" : (mouse_width , mouse_height),
                        "is_start": True,
                        "location": obj.matrix_world * vert.co,
                        "pressure": self.stroke_pressure,
                        'pen_flip': False,
                        'time': 1.0,
                        "size": self.stroke_size}])
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.view3d.view_selected(ctx)
                print("SCULPT DYNAMIC FINISHED")
        
    def preExecute(self, refholder):
        pass

class SculptNDNode(UMOGOutputNode):
    bl_idname = "umog_SculptNDNode"
    bl_label = "Sculpt ND Node"

    mesh_name = bpy.props.StringProperty()
    stroke_pressure = bpy.props.FloatProperty(min=0.0001, max=2.0, default=1.0)
    stroke_size = bpy.props.IntProperty(default=44)

    def init(self, context):
        # self.inputs.new("BaseInputSocketType", "Input")
        super().init(context)

    def draw_buttons(self, context, layout):
        # layout.operator("umog.select_mesh", text = "Select Mesh").pnode = self.name
        layout.prop_search(self, "mesh_name", bpy.data, "objects", icon="MESH_CUBE", text="")
        layout.prop(self, "stroke_pressure", text="Stroke Pressure")
        layout.prop(self, "stroke_size", text="Stroke Size")


    def update(self):
        pass
    
    def execute(self, refholder):
        #print("sculpt node execution, mesh: " + self.mesh_name)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[self.mesh_name].select = True
        bpy.context.scene.objects.active = bpy.data.objects[self.mesh_name]

        for area in bpy.context.screen.areas:
            #print(area.type)
            if area.type == 'VIEW_3D':
                ctx = bpy.context.copy()
                ctx['area'] = area
                ctx['region'] = area.regions[-1]

                bpy.ops.view3d.view_selected(ctx)

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.normals_make_consistent()
                
                bpy.ops.object.mode_set(mode = 'SCULPT')
                
                bpy.data.brushes["SculptDraw"].stroke_method = "DOTS"
                bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
                
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting:
                    bpy.ops.sculpt.dynamic_topology_toggle()

                obj = bpy.context.active_object
                verts = list(obj.data.vertices)
                #print(str(len(verts)))

                mouse_width = int(area.width/2)
                mouse_height = int(area.height/2)

                for vert in verts:
                    bpy.ops.sculpt.brush_stroke(ctx, stroke=[{
                        "name": "first",
                        "mouse" : (mouse_width , mouse_height),
                        "is_start": True,
                        "location": obj.matrix_world * vert.co,
                        "pressure": self.stroke_pressure,
                        'pen_flip': False,
                        'time': 1.0,
                        "size": self.stroke_size}])
                bpy.ops.object.mode_set(mode = 'OBJECT')
                #print("ALL GOOD!")
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.view3d.view_selected(ctx)
                print("SCULPT STATIC FINISHED")
                
    def preExecute(self, refholder):
        pass

class DisplaceNode(UMOGOutputNode):
    bl_idname = "umog_DisplaceNode"
    bl_label = "Displace Node"
    
    temp_texture_prefix = "__umog_internal_"

    mesh_name = bpy.props.StringProperty()
    mesh_dupl_name = bpy.props.StringProperty()
    
    texture_name_temp = bpy.props.StringProperty()
    
    mesh_name_index = bpy.props.IntProperty()

    use_subdiv = bpy.props.BoolProperty(default=True)
    mod_midlevel = bpy.props.FloatProperty(min=0.0, max=1.0, default=0.5)	
    mod_strength = bpy.props.FloatProperty(default=1.0)
    
    def init(self, context):
        self.inputs.new("TextureSocketType", "Texture")
        super().init(context)

    def draw_buttons(self, context, layout):
        #layout.operator("umog.select_mesh", text = "Select Mesh").pnode = self.name
        layout.prop_search(self, "mesh_name", bpy.data, "objects", icon="MESH_CUBE", text="")
        layout.prop(self, "use_subdiv", text="Subdivide")		
        layout.prop(self, "mod_midlevel", text="Midlevel")
        layout.prop(self, "mod_strength", text="Strength")

    def update(self):
        pass
    
    def execute(self, refholder):
        print("sculpt node execution, mesh: " + self.mesh_name)
        refholder.handleToImage(self.inputs[0].links[0].to_socket.texture_index, bpy.data.images[self.texture_name_temp])
        
        obj = bpy.data.objects[self.mesh_name]

        if self.inputs["Texture"].is_linked:
			
            if self.use_subdiv:
                oname="SUBDIV"
                mod = obj.modifiers.new(name=oname, type='SUBSURF')
                bpy.ops.object.modifier_apply(modifier=oname)

            oname="DSIPLACE"
            mod = obj.modifiers.new(name=oname, type='DISPLACE')
            dir(mod)
            mod.texture = bpy.data.textures[self.texture_name_temp]
            mod.mid_level = self.mod_midlevel
            mod.strength = self.mod_strength
            bpy.ops.object.modifier_apply(modifier=oname)
        else:
            print("no texture specified")

    def preExecute(self, refholder):
        image = bpy.data.images.new(self.temp_texture_prefix + self.name, width=bpy.context.scene.TextureResolution, height=bpy.context.scene.TextureResolution)
        self.texture_name_temp = image.name
        cTex = bpy.data.textures.new(self.temp_texture_prefix + self.name, type = 'IMAGE')
        cTex.image = image
        print("texture name: " + self.texture_name_temp)
        pass
    
    def postBake(self, refholder):
        bpy.data.textures.remove(bpy.data.textures[self.texture_name_temp])
        bpy.data.images.remove(bpy.data.images[self.texture_name_temp])
        pass

class BMeshNode(UMOGOutputNode):
    bl_idname = "umog_BMeshNode"
    bl_label = "BMesh Node"

    mesh_name = bpy.props.StringProperty()
    mesh_dupl_name = bpy.props.StringProperty()
    
    mesh_name_index = bpy.props.IntProperty()
    
    mod_list_handle = bpy.props.IntProperty()
    
    def init(self, context):
        self.inputs.new("TextureSocketType", "Input")
        super().init(context)

    def draw_buttons(self, context, layout):
        #layout.operator("umog.select_mesh", text = "Select Mesh").pnode = self.name
        layout.prop_search(self, "mesh_name", bpy.data, "objects", icon="MESH_CUBE", text="")


    def update(self):
        pass
    
    def execute(self, refholder):
        try:
            print("sculpt node execution, mesh: " + self.mesh_name)
        except:
            pass
        
        try:
            fn = self.inputs[0].links[0].to_socket
            texture_handle = fn.texture_index
            #copy the mesh and hid the original
        except:
            print("no texture as input")
        bm = bmesh.new()   # create an empty BMesh
        bm.from_mesh(bpy.data.meshes[bpy.data.objects[self.mesh_name].data.name])
        
        bmesh.ops.poke(bm, faces=bm.faces)
        
        cx, cy =0,0
        tr = bpy.context.scene.TextureResolution -1
        for vert in bm.verts:
            #displace along normal by texture
            factor = (refholder.np2dtextures[texture_handle].item(cx,cy,3)) + 0.1
            #print("factor: " + str(factor) + " x:" + str(cx) + " y:" + str(cy))
            #print("vertex: " + str(vert.co.x) + "," + str(vert.co.y) + "," + str(vert.co.z))
            vert.co = vert.co + (factor * vert.normal )
            if cx == tr:
                cx =0
                cy = cy+1
            else:
                cx = cx +1
                
            if cy == tr:
                cy = 0
            
        bm.to_mesh(bpy.data.meshes[bpy.data.objects[self.mesh_name].data.name])
        bm.free()
        
    def preExecute(self, refholder):
        pass

class BMeshCurlNode(UMOGOutputNode):
    bl_idname = "umog_BMeshCurlNode"
    bl_label = "BMesh Curl Node"

    mesh_name = bpy.props.StringProperty()
    mesh_dupl_name = bpy.props.StringProperty()
    
    mesh_name_index = bpy.props.IntProperty()
    
    
    
    mod_list_handle = bpy.props.IntProperty()
    
    def init(self, context):
        self.inputs.new("TextureSocketType", "Input")
        super().init(context)

    def draw_buttons(self, context, layout):
        #layout.operator("umog.select_mesh", text = "Select Mesh").pnode = self.name
        layout.prop_search(self, "mesh_name", bpy.data, "objects", icon="MESH_CUBE", text="")


    def update(self):
        pass
    
    def execute(self, refholder):
        try:
            print("sculpt node execution, mesh: " + self.mesh_name)
        except:
            pass
        try:
            fn = self.inputs[0].links[0].to_socket
            texture_handle = fn.texture_index
            #copy the mesh and hid the original
        except:
            print("no texture as input")
        
        bm = bmesh.new()   # create an empty BMesh
        bm.from_mesh(bpy.data.meshes[bpy.data.objects[self.mesh_name].data.name])
        
        #bmesh.ops.inset_region(bm, faces=bm.faces, thickness=0.4)
        #bmesh.ops.inset_region(bm, faces=bm.faces, thickness=0, depth=-0.5)
        bmesh.ops.poke(bm, faces=bm.faces)
        
        cx, cy =0,0
        tr = bpy.context.scene.TextureResolution -1
        for vert in bm.verts:
            #displace along normal by texture
            factor = (refholder.np2dtextures[texture_handle].item(cx,cy,3)) + 0.1
            #print("factor: " + str(factor) + " x:" + str(cx) + " y:" + str(cy))
            #print("shell factor: " + str(vert.calc_shell_factor()))
            if vert.calc_shell_factor() > 1.01:
                vert.co = vert.co + (factor * vert.normal )
                if cx == tr:
                    cx =0
                    cy = cy+1
                else:
                    cx = cx +1
                    
                if cy == tr:
                    cy = 0
        
        bm.to_mesh(bpy.data.meshes[bpy.data.objects[self.mesh_name].data.name])
        bm.free()
        
    def preExecute(self, refholder):
        pass
#begin reaction nodes
class ReactionDiffusionNode(UMOGNode):
    bl_idname = "umog_ReactionDiffusionNode"
    bl_label = "Reaction Diffusion Node"
    
    feed = bpy.props.FloatProperty(default= 0.055)
    kill = bpy.props.FloatProperty(default= 0.062)
    Da = bpy.props.FloatProperty(default= 1.0)
    Db = bpy.props.FloatProperty(default= 0.5)
    dt = bpy.props.FloatProperty(default= 1.0)

    def init(self, context):
        self.outputs.new("TextureSocketType", "A'")
        self.outputs.new("TextureSocketType", "B'")
        self.inputs.new("TextureSocketType", "A")
        self.inputs.new("TextureSocketType", "B")
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "feed", "Feed")
        layout.prop(self, "kill", "Kill")
        layout.prop(self, "Da", "Da")
        layout.prop(self, "Db", "Db")
        layout.prop(self, "dt", "dt")

    def update(self):
        pass
    
    def execute(self, refholder):
        #compute A'
        mask = np.array([[0.05, 0.2, 0.05], [0.2, -1, 0.2], [0.05, 0.2, 0.05]])
        Ap = refholder.np2dtextures[self.outputs[0].texture_index]
        A = refholder.np2dtextures[self.inputs[0].links[0].from_socket.texture_index]
        LA = copy.deepcopy(A)
        events.convolve2d(Ap, mask, LA)
        
        Bp = refholder.np2dtextures[self.outputs[1].texture_index]
        B = refholder.np2dtextures[self.inputs[1].links[0].from_socket.texture_index]
        LB = copy.deepcopy(B)
        events.convolve2d(Bp, mask, LB)
        
        events.ReactionDiffusion2d(A,Ap, LA, B, Bp, LB, mask, self.Da, self.Db, self.feed, self.kill, self.dt)
        
        
        
    def preExecute(self, refholder):
        self.outputs[0].texture_index = refholder.createRefForTexture2d()
        self.outputs[1].texture_index = refholder.createRefForTexture2d()
        
class ConvolveNode(UMOGNode):
    bl_idname = "umog_ConvolveNode"
    bl_label = "Convolve Node"

    def init(self, context):
        self.outputs.new("TextureSocketType", "out")
        self.inputs.new("TextureSocketType", "in")
        super().init(context)

    def draw_buttons(self, context, layout):
        pass
        
    def update(self):
        pass
    
    def execute(self, refholder):
        #compute A'
        print("convolve node")
        mask = np.array([[0.05, 0.2, 0.05], [0.2, -1, 0.2], [0.05, 0.2, 0.05]])
        A = refholder.np2dtextures[self.inputs[0].links[0].from_socket.texture_index]
        Ap = refholder.np2dtextures[self.outputs[0].texture_index]
        events.convolve2d(A, mask, Ap)
        
        print(" convolve min, max " + str(np.amin(Ap)) + "," + str(np.amax(Ap)))

        
    def preExecute(self, refholder):
        self.outputs[0].texture_index = refholder.createRefForTexture2d()

class Mat3Node(UMOGNode):
    bl_idname = "umog_Mat3Node"
    bl_label = "Matrix"

    #matrix = bpy.props.FloatVectorProperty(size = 16,subtype='MATRIX', default = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    matrix = bpy.props.FloatVectorProperty(size = 16, default = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    
    
    def init(self, context):
        self.outputs.new("Mat3SocketType", "Output")
        self.inputs.new("Mat3SocketType", "Input")
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'matrix')

            
    def execute(self, refholder):
        print('begin matrix')
        for elem in self.matrix:
            print(elem)
    
#END: UMOG_NODES
