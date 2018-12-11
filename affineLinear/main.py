import sys
import time

#NECESSARY CONFIGURATION!!!  ###################################################
#projectPath = r"C:\Users\jam771\Desktop\blenderScripts\affineLinear"
projectPath = r"/home/user/Desktop/videoMaking/myBlenderScripts/affineLinear"
################################################################################

if projectPath not in sys.path:
    sys.path.append(projectPath)
    
from helpers import *

def main():
    make3dAxes()

    nPoints = 30
    xs = np.random.uniform(-8,8,(nPoints,1))
    noise = np.random.uniform(-1,1,(nPoints,1))
    f = lambda x: (2/3)*x + 2
    zs = np.array([f(x) for x in xs]) + noise
    ys = np.ones((nPoints,1))

    points = np.concatenate([xs,ys,zs], axis=1)

    spheres = []
    for point in points:
        s = makePoint(point,size=0.10)
        spheres.append(s)


    # bpy.context.scene.frame_current += 10
    for sphere in spheres:
        sphere.keyframe_insert(data_path="location", frame=0)
        sphere.location *= 1.2
        sphere.keyframe_insert(data_path='location', frame=20)
        sphere.location *= (1/1.2)
        sphere.keyframe_insert(data_path='location', frame=40)
    
    lineTail = (-8,1,f(-8))
    lineHead = (8,1,f(8))
    lineOffset = np.array(lineHead) - np.array(lineTail)
    line = makeLineSegment(lineOffset, tail=lineTail)
    
    closestPointToOrigin = np.array([-1,1,1.3])
    normal = np.cross(lineOffset, closestPointToOrigin)
    makePlane((0,0,0), normal=normal/5)




    bpy.context.scene.frame_end = 100







main()
