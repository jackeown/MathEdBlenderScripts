import bpy
import numpy as np
import mathutils
import config
import collections

# Functions for compatability between blender versions

def setActiveObject(obj):
    if config.blenderVersion < "2.8":
        bpy.context.scene.objects.active = obj
    else:
        bpy.context.view_layer.objects.active = obj

def selectObjects(objects, deselectOthers = True):
    if deselectOthers:
        bpy.ops.object.select_all(action="DESELECT")


    if config.blenderVersion < "2.8":
        for obj in objects:
            obj.select = True
    else:
        for obj in objects:
            obj.select_set(True)



# more generic helper functions

def move3dCursor(p = (0,0,0)):
    """This will move the blender 3d cursor to 3d coordinate of point p"""
    bpy.context.scene.cursor_location = p
    # bpy.context.space_data.cursor_location = p


def joinNameAndMovePivot(objects, name, pivot):
    setActiveObject(objects[0])
    selectObjects(objects)

    bpy.ops.object.join()
    move3dCursor(pivot)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.object.name = name

def makeSimpleColorMaterial(color, colorName):
    colorMat = bpy.data.materials.new(colorName)
    colorMat.diffuse_color = color
    return colorMat

def setMaterial(obj, material):
    if isinstance(obj, collections.Iterable):
        for x in obj:
            x.data.materials.clear()
            x.data.materials.append(material)
    else:
        obj.data.materials.clear()
        obj.data.materials.append(material)


#  Methods for extracting objects from "bpy.data.objects"

def getNamePrefix(name):
    """For Cylinder.001 returns string "Cylinder" """
    try:
        location = len(name) - "".join(reversed(name)).index(".")
        # index is never used, but this line ensures that the index is an int.
        index = int(name[location:])
        prefix = name[:location-1]
    except Exception:
        prefix = name
    return prefix

def getNameIndex(name):
    """For Cylinder.001 returns int 1"""
    try:
        location = len(name) - "".join(reversed(name)).index(".")
        index = int(name[location:])
    except Exception:
        index = 0
    return index

def getObject(name, index=-1):
    """getObject("Cylinder") will search bpy.data.objects for
    "Cylinder", "Cylinder.001", "Cylinder.002", etc
    and will return the cylinder with the requested index, or None if it's not found.

    index can also be set to negative numbers which
    will be indices backward into the sorted list of objects"""

    names = [x.name for x in bpy.data.objects if getNamePrefix(x.name) == name]
    names = sorted(names, key=getNameIndex)

    obj = None
    if index < 0:
        obj = bpy.data.objects[names[index]]
    else:
        for n in names:
            if getNameIndex(n) == index:
                obj = bpy.data.objects[n]

    return obj



# Methods for making mathematical objects such as Axes, Vectors, Points

def makeVector(offset = np.sqrt([1/3,1/3,1/3]), thickness = 0.05, tail=(0,0,0)):
    offset = np.array(offset)
    tail = np.array(tail)
    length = np.sqrt(offset @ offset.T)
    unitOffset = offset/length
    head = tail+offset
    center = (head+tail)/2

    # A cylinder is initialized vertically
    # The cross-product can give axes to rotate around and arcsin will give angle
    # to rotate by in order to align a newly created cylinder to our intended vector.
    rotationAxis = np.cross(np.array([0,0,1]), offset)
    rotationAngle = (np.pi/2) - np.arcsin(offset[2]/length)
    if np.sqrt(rotationAxis @ rotationAxis.T) < 1e-5 and offset[2] < 0:
        rotationAxis = mathutils.Vector((0,1,0))
        rotationAngle = np.pi
    else:
        rotationAxis = mathutils.Vector(rotationAxis)

    # turn this specification of rotation into something blender can use
    rotationMatrix = mathutils.Matrix.Rotation(rotationAngle, 3, rotationAxis)
    rot = rotationMatrix.to_euler()

    #Adjust rod length and center for cone point at the end.
    coneLength = 5*thickness
    coneRadius = 3*thickness
    length -= coneLength
    center -= (unitOffset*coneLength/2)
    conePosition = (head - unitOffset*coneLength/2)

    # add cylinder and cone to scene
    bpy.ops.mesh.primitive_cylinder_add(radius=thickness, depth = length, location=center, rotation=rot)
    cyl = bpy.context.object

    bpy.ops.mesh.primitive_cone_add(radius1 = coneRadius, depth = coneLength, location = conePosition, rotation = rot)
    cone = bpy.context.object

    # join cylinder with cone and change pivot point
    joinNameAndMovePivot([cyl,cone], "Arrow", tail)
    return bpy.context.object

def make3dAxes(thickness = 0.05, lengths=(16,16,16)):
    red = makeSimpleColorMaterial((1,0,0), "red")
    green = makeSimpleColorMaterial((0,1,0), "green")
    blue = makeSimpleColorMaterial((0,0,1), "blue")

    xp = makeVector(offset = (8,0,0))
    xn = makeVector(offset = (-8,0,0))

    yp = makeVector(offset = (0,8,0))
    yn = makeVector(offset = (0,-8,0))

    zp = makeVector(offset = (0,0,8))
    zn = makeVector(offset = (0,0,-8))


    setMaterial([xp,xn], red)
    setMaterial([yp,yn], green)
    setMaterial([zp,zn], blue)
    joinNameAndMovePivot([xp,xn,yp,yn,zp,zn], "Axes", (0,0,0))

def makePoint(p, size=0.1, smooth = True):
    p = tuple(p)
    if config.blenderVersion < "2.8":
        bpy.ops.mesh.primitive_uv_sphere_add(segments = 7,ring_count=7,location=p, size=size)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments = 7,ring_count=7,location=p, radius=size)

    if smooth:
        bpy.ops.object.shade_smooth()
        bpy.ops.object.modifier_add(type="SUBSURF")

    if config.blenderVersion < "2.8":
        bpy.context.object.modifiers["Subsurf"].levels = 3
    else:
        bpy.context.object.modifiers["Subdivision"].levels = 3
