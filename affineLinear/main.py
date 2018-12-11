import sys
import time

#NECESSARY CONFIGURATION!!!  ###################################################
projectPath = r"C:\Users\jam771\Desktop\blenderScripts\affineLinear"
################################################################################

if projectPath not in sys.path:
    sys.path.append(projectPath)
    
from helpers import *

def main():
    # print(sys.path)
    make3dAxes()

    points = np.random.uniform(-3,3,(2,3))
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
