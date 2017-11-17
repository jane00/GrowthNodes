import math
import bpy
from bpy.props import *
from ..utils.debug import *
import random
from ..utils.events import propUpdate

from ..engine import types, engine

class UMOGNodeExecutionProperties(bpy.types.PropertyGroup):
    bl_idname = "umog_NodeExecutionProperties"
    visited = BoolProperty(name = "Visited in Topological Sort", default = False)
    connectedComponent = IntProperty(name = "Connected Component Network of Node",
                                     default = 0)


class UMOGNodeDisplayProperties(bpy.types.PropertyGroup):
    bl_idname = "umog_NodeDisplayProperties"
    useCustomColor = BoolProperty(name = "Use Custom Color", default = False)
    customColor = FloatVectorProperty(name = "Custom Color", default = (0.0, 0.0, 0.0),
                                      min = 0, max = 1)
    highlightColor = FloatVectorProperty(name = "Highlight Color",
                                         default = (0.6, 0.4, 0.4), min = 0, max = 1)

class UMOGNode(bpy.types.Node):
    bl_width_min = 40
    bl_width_max = 5000

    _IsUMOGNode = True
    _IsInputNode = False
    _IsOutputNode = False

    bl_label = "UMOGNode"

    # unique string for each node; don't change it at all
    identifier = StringProperty(name = "Identifier", default = "")

    # used for the listboxes in the sidebar
    activeInputIndex = IntProperty()
    activeOutputIndex = IntProperty()

    # can contain: 'NO_EXECUTION', 'NOT_IN_SUBPROGRAM',
    #              'NO_AUTO_EXECUTION', 'NO_TIMING',
    options = set()

    # can be "NONE", "ALWAYS" or "HIDDEN_ONLY"
    dynamicLabelType = "NONE"

    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "umog_UMOGNodeTree"


        self.width_hidden = 100
        self.identifier = createIdentifier()

    def init(self, context):
        pass

    def free(self):
        for socket in self.inputs:
            socket.destroy()
        for socket in self.outputs:
            socket.destroy()
        self.destroy()
        print("freed")

    def refreshNode(self):
        for socket in self.inputs:
            socket.refreshSocket()
        self.refresh()

    def refreshOnFrameChange(self):
        pass

    def packSockets(self):
        for socket in self.inputs:
            socket.packSocket()
        for socket in self.outputs:
            socket.packSocket()

    # functions subclasses can override
    ######################################

    def update(self):
        pass

    def refresh(self):
        pass

    def refreshOnFrameChange(self):
        pass

    def destroy(self):
        pass

    # this will be called when the node is executed by bake meshes
    # will be called each iteration
    def execute(self, refholder):
        pass

    # will be called once before the node will be executed by bake meshes
    # refholder is passed to this so it can register any objects that need it
    def preExecute(self, refholder):
        pass

    # will be called once at the end of each frame
    def postFrame(self, refholder):
        pass

    def postBake(self, refholder):
        pass


    def socketMoved(self):
        self.socketChanged()

    def customSocketNameChanged(self, socket):
        self.socketChanged()

    def socketRemoved(self):
        self.socketChanged()

    def socketChanged(self):
        """
        Use this function when you don't need
        to know what happened exactly to the sockets
        """
        pass

    def removeSocket(self, socket):
        index = socket.index
        if socket.isOutput:
            if index < self.activeOutputIndex:
                self.activeOutputIndex -= 1
        else:
            if index < self.activeInputIndex:
                self.activeInputIndex -= 1
        socket.sockets.remove(socket)

    def storeCustomColor(self):
        currentColor = self.color
        redIsClose = math.isclose(currentColor[0], self.display.highlightColor[0],
                                  abs_tol = 0.01)
        greenIsClose = math.isclose(currentColor[1], self.display.highlightColor[1],
                                    abs_tol = 0.01)
        blueIsClose = math.isclose(currentColor[2], self.display.highlightColor[2],
                                   abs_tol = 0.01)

        if not redIsClose or not greenIsClose or not blueIsClose:
            self.display.customColor = self.color
            self.display.useCustomColor = self.use_custom_color

    def enableUnlinkedHighlight(self):
        self.storeCustomColor()
        self.use_custom_color = True
        self.color = self.display.highlightColor

    def disableUnlinkedHighlight(self):
        self.use_custom_color = self.display.useCustomColor
        self.color = self.display.customColor

    @property
    def nodeTree(self):
        return self.id_data

    @property
    def hasInputLinks(self):
        for inputSocket in self.inputs:
            if len(inputSocket.links) > 0:
                return True
        return False

    @property
    def hasOutputLinks(self):
        for outputSocket in self.outputs:
            if len(outputSocket.links) > 0:
                return True
        return False

    @property
    def isLinked(self):
        return self.hasOutputLinks or self.hasInputLinks

    @property
    def activeInputSocket(self):
        if len(self.inputs) == 0:
            return None
        return self.inputs[self.activeInputIndex]

    @property
    def activeOutputSocket(self):
        if len(self.outputs) == 0:
            return None
        return self.outputs[self.activeOutputIndex]

    @property
    def sockets(self):
        return list(self.inputs) + list(self.outputs)

    def newInput(self, idName, name, identifier = None, alternativeIdentifier = None,
                 **kwargs):
        if identifier is None:
            identifier = name
        socket = self.inputs.new(idName + 'SocketType', name, identifier + self.nodeTree.getNextUniqueID())
        socket.originalName = socket.name
        self._setAlternativeIdentifier(socket, alternativeIdentifier)
        self._setSocketProperties(socket, kwargs)
        return socket

    def newOutput(self, idName, name, identifier = None, alternativeIdentifier = None,
                  **kwargs):
        if identifier is None:
            identifier = name
        socket = self.outputs.new(idName + 'SocketType', name, identifier + self.nodeTree.getNextUniqueID())
        socket.originalName = socket.name
        self._setAlternativeIdentifier(socket, alternativeIdentifier)
        self._setSocketProperties(socket, kwargs)
        return socket

    def _setAlternativeIdentifier(self, socket, alternativeIdentifier):
        if isinstance(alternativeIdentifier, str):
            socket.alternativeIdentifiers = [alternativeIdentifier]
        elif isinstance(alternativeIdentifier, (list, tuple, set)):
            socket.alternativeIdentifiers = list(alternativeIdentifier)

    def _setSocketProperties(self, socket, properties):
        for key, value in properties.items():
            setattr(socket, key, value)

    # engine
    def get_operation(self, input_types):
        return engine.Operation(engine.NOP, [], [], [], [])

    def get_buffer_values(self):
        return []


def createIdentifier():
    identifierLength = 15
    characters = "abcdefghijklmnopqrstuvwxyz" + "0123456789"
    choice = random.SystemRandom().choice
    return "_" + ''.join(choice(characters) for _ in range(identifierLength))


def nodeToID(node):
    return (node.id_data.name, node.name)


def isUMOGNode(node):
    return getattr(node, "_isUMOGNode", False)

class UMOGOutputNode(UMOGNode):
    _IsOutputNode = True

    def init(self, context):
        super().init(context)

    def output_value(self, value):
        pass

    def write_keyframe(self, refholder, frame):
        pass

class UMOGInputNode(UMOGNode):
    _IsInputNode = True

    def init(self, context):
        super().init(context)

def register():
    bpy.types.Node.toID = nodeToID
    bpy.types.Node.isUMOGNode = BoolProperty(default = False, get = isUMOGNode)

    # PointerProperties can only be added after the PropertyGroup is registered
    bpy.types.Node.execution = PointerProperty(type = UMOGNodeExecutionProperties)
    bpy.types.Node.display = PointerProperty(type = UMOGNodeDisplayProperties)

def unregister():
    del bpy.types.Node.toID
    del bpy.types.Node.isUMOGNode
