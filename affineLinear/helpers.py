import bpy
import numpy as np
import mathutils

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
    # print(names)
    names = sorted(names, key=getNameIndex)

    obj = None
    if index < 0:
        obj = bpy.data.objects[names[index]]
    else:
        for n in names:
            if getNameIndex(n) == index:
                obj = bpy.data.objects[n]

    return obj



def move3dCursor(p = (0,0,0)):
    """This will move the blender 3d cursor to 3d coordinate of point p"""
    bpy.context.scene.cursor_location = p
    # bpy.context.space_data.cursor_location = p

def makeVector(offset = np.sqrt([1/3,1/3,1/3]), thickness = 0.05, tail=(0,0,0)):
    offset = np.array(offset)
    length = np.sqrt(offset @ offset.T)
    unitOffset = offset/length
    tail = np.array(tail)
    head = tail+offset
    center = (head+tail)/2

    #Cross product will give axes to rotate around and arcsin will give angle.
    rotationAxis = mathutils.Vector(np.cross(np.array([0,0,1]), offset))
    rotationAngle = (np.pi/2) - np.arcsin(offset[2]/length)
    rotationMatrix = mathutils.Matrix.Rotation(rotationAngle, 3, rotationAxis)
    rot = rotationMatrix.to_euler()

    #Adjust rod length and center for cone point at the end.
    coneLength = 5*thickness
    coneRadius = 3*thickness
    length -= coneLength
    center -= (unitOffset*coneLength/2)

    conePosition = (head - unitOffset*coneLength/2)
    bpy.ops.mesh.primitive_cylinder_add(radius=thickness, depth = length, location=center, rotation=rot)
    bpy.ops.mesh.primitive_cone_add(radius1 = coneRadius, depth = coneLength, location = conePosition, rotation = rot)


def make3dAxes(thickness = 0.05, lengths=(16,16,16)):
    makeVector(offset = (8,0,0))
    makeVector(offset = (-8,0,0))

    makeVector(offset = (0,8,0))
    makeVector(offset = (0,-8,0))

    makeVector(offset = (0,0,8))
    makeVector(offset = (0,0,-8))

def makePoint(p, size=0.1):
    p = tuple(p)
    try: # > blender 2.8
        bpy.ops.mesh.primitive_uv_sphere_add(segments = 7,ring_count=7,location=p, radius=size)
    except Exception:
        bpy.ops.mesh.primitive_uv_sphere_add(segments = 7,ring_count=7,location=p, size=size)

    bpy.ops.object.shade_smooth()
    bpy.ops.object.modifier_add(type="SUBSURF")
    try: # < blender 2.8
        bpy.context.object.modifiers["Subsurf"].levels = 3
    except Exception: # >= 2.8
        bpy.context.object.modifiers["Subdivision"].levels = 3
