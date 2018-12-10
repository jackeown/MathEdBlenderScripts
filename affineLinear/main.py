import sys
import time

#NECESSARY CONFIGURATION!!!  ###################################################
projectFolder = "/home/user/Desktop/videoMaking/myBlenderScripts/affineLinear"

if projectFolder not in sys.path:
    sys.path.append(projectFolder)

################################################################################

from helpers import *

def main():
    # print(sys.path)
    make3dAxes()

    points = np.random.uniform(-3,3,(100,3))
    for point in points:
        makePoint(point,size=0.02)
        makeVector(point, tail=(0,0,0))
        # move3dCursor((1,2,3))
        # time.sleep(1)

    # print(getObject("Cylinder",-2))
    # print(getObject("Cylinder",-1))

    # points = np.random.uniform(-5,5,(20,3))
    # for point in points:
    #     makePoint(point)






main()
