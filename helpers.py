import bpy
import numpy as np
import mathutils
import config
import collections

# path = os.path.abspath(os.path.dirname(__file__))
# if path not in sys.path:
#     sys.path.append(path)

from manimTexHelpers import TEMPLATE, tex_hash, tex_to_svg_file


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

def getRotationFromVector(offset):
    """Should turn a vector into euler rotations for moving the z axis to this orientation"""
    offset = np.array(offset)
    length = np.sqrt(offset @ offset.T)
    rotationAxis = np.cross(np.array([0,0,1]), np.array(offset))
    rotationAngle = (np.pi/2) - np.arcsin(offset[2]/length)
    if np.sqrt(rotationAxis @ rotationAxis.T) < 1e-5 and offset[2] < 0:
        rotationAxis = mathutils.Vector((0,1,0))
        rotationAngle = np.pi
    else:
        rotationAxis = mathutils.Vector(rotationAxis)

    # turn this specification of rotation into something blender can use
    rotationMatrix = mathutils.Matrix.Rotation(rotationAngle, 3, rotationAxis)
    rot = rotationMatrix.to_euler()
    return rot

def move3dCursor(p = (0,0,0)):
    """This will move the blender 3d cursor to 3d coordinate of point p"""
    bpy.context.scene.cursor_location = p
    # bpy.context.space_data.cursor_location = p

def cameraLookAt(camera, point):
    point = mathutils.Vector(point)
    loc_camera = camera.location

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    camera.rotation_euler = rot_quat.to_euler()

def cameraOrbit(camera, duration = 5, radius=40, height=3, revolutions=1, speed=3):
    tick = speed/100
    for theta in np.arange(0,2*np.pi*revolutions,tick):
        camera.location = (radius*np.cos(theta), radius*np.sin(theta), height)
        cameraLookAt(camera,(0,0,0))
        bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocRot')
        bpy.context.scene.frame_current += 1

def joinNameAndMovePivot(objects, name, pivot):
    pivot = np.array(pivot)
    setActiveObject(objects[0])
    selectObjects(objects)

    bpy.ops.object.join()
    move3dCursor(pivot)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.object.name = name
    return bpy.context.object

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


# Set up default theme materials: (maybe allow modification of this in config?)

themeMaterials = {
    "primary": (1,1,0),
    "secondary": (0,1,1),
    "highlight": (1,1,1),
    "red": (1,0,0),
    "green": (0,1,0),
    "blue": (0,0,1),
    "shadow": (0,0,0)
}

themeMaterials = {key: makeSimpleColorMaterial(themeMaterials[key],key) for key in themeMaterials}


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

    if len(names) == 0:
        print("Object '{}' not found!".format(name))
        return None

    if index < 0:
        obj = bpy.data.objects[names[index]]
    else:
        for n in names:
            if getNameIndex(n) == index:
                obj = bpy.data.objects[n]

    return obj

def getCollection(name, index=-1):
    """Does the same thing as getObject, but for blender collections instead"""
    names = [x.name for x in bpy.data.collections if getNamePrefix(x.name) == name]
    names = sorted(names, key=getNameIndex)

    if len(names) == 0:
        print("Collection '{}' not found!".format(name))
        return None

    if index < 0:
        obj = bpy.data.collections[names[index]]
    else:
        for n in names:
            if getNameIndex(n) == index:
                obj = bpy.data.collections[n]

    return obj



# Methods for making mathematical objects such as Lines, Planes, Axes, Vectors, Points


def makePlane(offset, normal=(1,1,1), material=themeMaterials["primary"]):
    normal = np.array(normal)
    size = np.sqrt(normal @ normal.T)
    rot = getRotationFromVector(normal)
    bpy.ops.mesh.primitive_plane_add(location=offset, rotation=rot, size=size)
    return bpy.context.object

def makeVector(offset = np.sqrt([1/3,1/3,1/3]), withCone = True, thickness = 0.05, tail=(0,0,0), material=themeMaterials["primary"]):
    offset = np.array(offset)
    tail = np.array(tail)
    length = np.sqrt(offset @ offset.T)
    unitOffset = offset/length
    head = tail+offset
    center = (head+tail)/2

    rot = getRotationFromVector(offset)

    #Adjust rod length and center for cone point at the end.
    coneLength = 5*thickness
    coneRadius = 3*thickness
    length -= coneLength
    center -= (unitOffset*coneLength/2)
    conePosition = (head - unitOffset*coneLength/2)

    # add cylinder and cone to scene
    bpy.ops.mesh.primitive_cylinder_add(radius=thickness, depth = length, location=center, rotation=rot)
    cyl = bpy.context.object

    if withCone:
        bpy.ops.mesh.primitive_cone_add(radius1 = coneRadius, depth = coneLength, location = conePosition, rotation = rot)
        cone = bpy.context.object

    # join cylinder with cone and change pivot point
    name = "Vector" if withCone else "LineSegment"
    thingsToJoin = [cyl]
    if withCone:
        thingsToJoin.append(cone)

    joinNameAndMovePivot(thingsToJoin, name, tail)
    setMaterial(bpy.context.object, material)
    return bpy.context.object

def makeLineSegment(offset = np.sqrt([1/3,1/3,1/3]), withCone = False, thickness = 0.05, tail=(0,0,0), material=themeMaterials["primary"]):
    return makeVector(offset = offset, withCone = withCone, thickness = thickness, tail=tail, material=material)

def make3dAxes(thickness = 0.05, lengths=(16,16,16), withLabels = True):
    red = themeMaterials["red"] #makeSimpleColorMaterial((1,0,0), "red")
    green = themeMaterials["green"] #makeSimpleColorMaterial((0,1,0), "green")
    blue = themeMaterials["blue"] #makeSimpleColorMaterial((0,0,1), "blue")

    xp = makeVector(offset = (8,0,0), material=red)
    xn = makeVector(offset = (-8,0,0), material=red)

    yp = makeVector(offset = (0,8,0), material=green)
    yn = makeVector(offset = (0,-8,0), material=green)

    zp = makeVector(offset = (0,0,8), material=blue)
    zn = makeVector(offset = (0,0,-8), material=blue)

    stuffToJoin = [xp,xn,yp,yn,zp,zn]
    if withLabels:
        xlabel = makeTex("$x$-axis", location = (9,0,0), material=red)
        ylabel = makeTex("$y$-axis", location = (0,9,0), material=green)
        zlabel = makeTex("$z$-axis", location = (0,0,9), material=blue)
        # stuffToJoin.extend([xlabel,ylabel,zlabel])

    joinNameAndMovePivot(stuffToJoin, "Axes", (0,0,0))

def makePoint(p, size=0.1, smooth = True, material=themeMaterials["primary"]):
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

    setMaterial(bpy.context.object, material)
    return bpy.context.object




# Methods for dealing with LaTeX (for math and other text)

def makeTex(expression, location=(0,0,0), scale=2, trackCamera = True, material=themeMaterials["secondary"], thickness=0.3):
    location = np.array(location)
    svgPath = tex_to_svg_file(expression, TEMPLATE)
    bpy.ops.import_curve.svg(filepath=svgPath)
    collectionName = tex_hash(expression, TEMPLATE) + ".svg"
    collection = getCollection(collectionName)

    obj = joinNameAndMovePivot(collection.objects, expression, collection.objects[0].location)
    bpy.ops.object.convert()

    obj.scale *= (100 * scale)
    obj.location = location

    selectObjects([obj])
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0,0,-thickness)})
    bpy.ops.object.editmode_toggle()


    if trackCamera:
        bpy.ops.object.constraint_add(type='COPY_ROTATION')
        bpy.context.object.constraints["Copy Rotation"].target = bpy.data.objects["Camera"]

    setMaterial(obj,material)

    return obj