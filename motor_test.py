import time
from gpiozero import CamJamKitRobot
robot = CamJamKitRobot()

robot.forward()
time.sleep(1)

robot.stop()