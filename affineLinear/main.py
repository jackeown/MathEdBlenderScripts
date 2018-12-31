import sys
import time

#NECESSARY CONFIGURATION!!!  ###################################################
#projectPath = r"C:\Users\jam771\Desktop\blenderScripts"
projectPath = r"/home/user/Desktop/videoMaking/myBlenderScripts"
################################################################################

if projectPath not in sys.path:
    sys.path.append(projectPath)
    
from helpers import *

def main():
    make3dAxes()

    # generate dataset
    nPoints = 30
    xs = np.random.uniform(-8,8,(nPoints,1))
    noise = np.random.uniform(-1,1,(nPoints,1))
    f = lambda x: (2/3)*x + 2
    zs = np.array([f(x) for x in xs]) + noise
    ys = np.ones((nPoints,1))

    points = np.concatenate([xs,ys,zs], axis=1)

    # make spheres
    spheres = []
    for point in points:
        s = makePoint(point,size=0.10)
        spheres.append(s)

    # make line
    lineTail, lineHead = np.array([-8,1,f(-8)]), np.array([8,1,f(8)])
    lineOffset = lineHead - lineTail
    line = makeLineSegment(lineOffset, tail=lineTail)

    # make plane
    closestPointToOrigin = np.array([-1,1,1.3])
    normal = np.cross(lineOffset, closestPointToOrigin)
    makePlane((0,0,0), normal=normal/4)


    # animate spheres
    for sphere in spheres:
        sphere.keyframe_insert(data_path="location", frame=0)
        sphere.location.z -= 2
        sphere.location.y -= 1
        sphere.keyframe_insert(data_path='location', frame=20)
        sphere.keyframe_insert(data_path='location', frame=40)
        sphere.location.z += 2
        sphere.location.y += 1
        sphere.keyframe_insert(data_path='location', frame=60)

    # animate line
    line.keyframe_insert(data_path="location", frame=0)
    line.location.z -= 2
    line.location.y -= 1
    line.keyframe_insert(data_path="location", frame=20)
    line.keyframe_insert(data_path="location", frame=40)
    line.location.z += 2
    line.location.y += 1
    line.keyframe_insert(data_path="location", frame=60)


    # animate camera
    camera = getObject("Camera")
    selectObjects([camera])
    cameraOrbit(camera)


    bpy.context.scene.frame_current = 0
    bpy.context.scene.frame_end = 2*np.pi/0.01




main()
