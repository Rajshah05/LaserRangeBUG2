#!/usr/bin/env python

import rospy
import numpy

from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

thetarobot=0
xrobotstart=0
yrobotstart=0
thetarobotstart=0
xgoal=0
ygoal=0
xrobot=0
yrobot=0
status=[]
laserdata=[]
def callback_robotcpose(msg):
    global thetarobot
    global xrobot
    global yrobot
    xrobot = msg.pose.pose.position.x
    yrobot = msg.pose.pose.position.y
    worirobot = msg.pose.pose.orientation.w
    xorirobot = msg.pose.pose.orientation.x
    yorirobot = msg.pose.pose.orientation.y
    zorirobot = msg.pose.pose.orientation.z
    roll = pitch = yaw = 0.0
    orientation_list = [xorirobot, yorirobot, zorirobot, worirobot]
    (roll, pitch, yaw) = euler_from_quaternion(orientation_list)
    thetarobot = yaw
    print xrobot
    print yrobot
    print thetarobot


def callback_laserscan(msg):
    global status
    global laserdata
    laserdata = list(msg.ranges)
    R = laserdata[1:70]
    FR = laserdata[71:143]
    F = laserdata[144:216]
    FL = laserdata[217:290]
    L = laserdata[291:361]
    
    R_=FR_=F_=FL_=L_=0
    if 0.34<min(R)<1.2:
        R_=1
    if 0.34<min(FR)<1:
        FR_=1
    if 0.34<min(F)<1:
        F_=1
    if 0.34<min(FL)<1:
        FL_=1
    if 0.34<min(L)<1.2:
        L_=1
    status=[L_,FL_,F_,FR_,R_]
    print(status)
    


def merge():
    global xrobot
    global yrobot
    global thetarobot
    global xrobotstart
    global yrobotstart
    global tehtarobotstart
    global xgoal
    global ygoal
    global status
    global laserdata
    rospy.init_node('merge', anonymous=True)

    robotstartpose = rospy.wait_for_message('/base_pose_ground_truth', Odometry)
    xrobotstart = robotstartpose.pose.pose.position.x
    yrobotstart = robotstartpose.pose.pose.position.y
    worirobot = robotstartpose.pose.pose.orientation.w
    xorirobot = robotstartpose.pose.pose.orientation.x
    yorirobot = robotstartpose.pose.pose.orientation.y
    zorirobot = robotstartpose.pose.pose.orientation.z
    roll = pitch = yaw = 0.0
    orientation_list = [xorirobot, yorirobot, zorirobot, worirobot]
    (roll, pitch, yaw) = euler_from_quaternion(orientation_list)
    thetarobotstart = yaw
    print xrobotstart
    print yrobotstart
    print thetarobotstart

    goalpose = rospy.wait_for_message("/homing_signal", PoseStamped)
    xgoal = goalpose.pose.position.x
    ygoal = goalpose.pose.position.y
    print xgoal
    print ygoal

    rospy.Subscriber('/base_pose_ground_truth', Odometry, callback_robotcpose)
 
    rospy.Subscriber('/base_scan', LaserScan, callback_laserscan)

    
    slope=numpy.arctan((ygoal-yrobotstart)/abs(xgoal-xrobotstart))
    if slope<0 and xgoal-xrobotstart<0:
        slope=-(3.14159265359+slope)
    if slope>0 and xgoal-xrobotstart<0:
        slope=3.14159265359-slope
    print slope

    

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(1000)
    vel_msg=Twist()
    while not rospy.is_shutdown():
        while abs(thetarobot-slope)>=0.01:#abs(thetarobot-slope)>=0.01:
            vel_msg.angular.z=-0.4
            pub.publish(vel_msg)
            print("Entering Goal seek mode. Orienting towards Goal")
    

        vel_msg1=Twist()
        while status!=[0,1,1,1,0]and status!=[1,1,0,0,1]and status!=[1,0,0,1,1]and status!=[1,1,1,0,1]and status!=[1,0,1,1,1]and status!=[1,1,1,1,0]and status!=[0,1,1,1,1]and status!=[1,1,1,0,0]and status!=[0,0,1,1,1]and status!=[0,1,0,0,0]and status!=[0,0,1,0,0] and status!=[0,0,0,1,0] and status!=[0,1,1,0,0]and status!=[0,0,1,1,0]:
            vel_msg1.linear.x=1
            pub.publish(vel_msg1)
            if numpy.sqrt(numpy.square(yrobot-ygoal) + numpy.square(xrobot-xgoal))<=0.25:
                rospy.signal_shutdown("Reached the Goal !!!")
        
        def wallfollow():
            global laserdata
            global status
            global ygoal
            global yrobot
            global xgoal
            global xrobot
            global yrobotstart
            global xrobotstart
            check=True
            print("entered wall follow mode")
            while True:
                print("Wall Follow mode on")
                vel_msg3=Twist()
                while status!=[1,1,0,0,0] and status!=[1,0,0,0,0]:
                    vel_msg3.angular.z=-0.4
                    pub.publish(vel_msg3)
                vel_msg4=Twist()
                while status!=[0,1,1,1,0]and status!=[1,1,0,0,1]and status!=[1,0,0,1,1]and status!=[1,1,1,0,1]and status!=[1,0,1,1,1]and status!=[1,1,1,1,0]and status!=[0,1,1,1,1]and status!=[1,1,1,0,0]and status!=[0,0,1,1,1]and status!=[0,1,0,0,0]and status!=[0,0,1,0,0] and status!=[0,0,0,1,0] and status!=[0,1,1,0,0]and status!=[0,0,1,1,0] and status==[1,1,0,0,0]:
                    vel_msg4.linear.x=0.5
                    pub.publish(vel_msg4)
                    if numpy.sqrt(numpy.square(yrobot-ygoal) + numpy.square(xrobot-xgoal))<=0.25:
                        rospy.signal_shutdown("Reached the Goal !!!")
                    if abs(((ygoal-yrobot)/(xgoal-xrobot))-((yrobot-yrobotstart)/(xrobot-xrobotstart)))<0.025:
                        if check==False:
                            break
                    
                if abs(((ygoal-yrobot)/(xgoal-xrobot))-((yrobot-yrobotstart)/(xrobot-xrobotstart)))<0.025:
                    if check==False:
                        break
                    
                if status==[1,0,0,0,0,] or status==[0,0,0,0,0]:
                    vel_msg5=Twist()
                    while status!=[1,1,0,0,0] and status!=[0,1,0,0,0] and status!=[0,1,1,1,0]and status!=[1,1,0,0,1]and status!=[1,0,0,1,1]and status!=[1,1,1,0,1]and status!=[1,0,1,1,1]and status!=[1,1,1,1,0]and status!=[0,1,1,1,1]and status!=[1,1,1,0,0]and status!=[0,0,1,1,1]and status!=[0,1,0,0,0]and status!=[0,0,1,0,0] and status!=[0,0,0,1,0] and status!=[0,1,1,0,0]and status!=[0,0,1,1,0]:
                        check=False
                        vel_msg5.angular.z=+0.4
                        vel_msg5.linear.x=0.2
                        pub.publish(vel_msg5)
                        if numpy.sqrt(numpy.square(yrobot-ygoal) + numpy.square(xrobot-xgoal))<=0.25:
                            rospy.signal_shutdown("Reached the Goal !!!")
                        if abs(((ygoal-yrobot)/(xgoal-xrobot))-((yrobot-yrobotstart)/(xrobot-xrobotstart)))<0.025:
                            if check==False:
                                break
                    
            
        if status==[0,1,1,1,0] or status==[1,1,0,0,1] or status==[1,0,0,1,1] or status==[1,1,1,0,1] or status==[1,0,1,1,1] or status==[1,1,1,1,0] or status==[0,1,1,1,1] or status==[1,1,1,0,0] or status==[0,0,1,1,1]or status==[0,1,0,0,0]or status==[0,0,1,0,0] or status==[0,0,0,1,0] or status==[0,1,1,0,0]or status==[0,0,1,1,0]:
            wallfollow()
    

    rospy.spin()
	
if __name__ == '__main__':
    merge()

