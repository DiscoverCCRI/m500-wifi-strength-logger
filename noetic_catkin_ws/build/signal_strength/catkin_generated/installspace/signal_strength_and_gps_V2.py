#!/usr/bin/env python3
import rospy
import os
import csv
from std_msgs.msg import String
from pymavlink import mavutil

log_path = 'test.csv'
csv_header = ['Uptime','Signal Strength (dBm)','Lat(deg)','Lon(deg)','Alt(m)','Vel(m/s)','fix type','H_acc(m)','V-acc(m)','Sats_Visible','eph','epv','cog','alt_ellipsoid','vel_acc (m/s)','hdg_acc','yaw']

def loop():
    # Setup publisher node
    rospy.init_node('signal_strength_pub', anonymous=True)
    pub = rospy.Publisher('signal_strength_info', String, queue_size=10)
    
    # loop executes at 2 Hz (wifi strength command loses accuracy at rates higher than 2 Hz)
    rate = rospy.Rate(2) 

    # Open CSV log file and write the header
    log = open(log_path,'w')
    log_writer = csv.writer(log)
    log_writer.writerow(csv_header)

    # Setup Mavlink Connection (Note: Only one local, on board mavlink connection can be made on port 14551 at a time. 
    #                           Up to 16 external, off board connections can be made on port 14550
    #                           Also note that voxl waits for heartbeats on 14551, so we need to send one.)
    connection = mavutil.mavlink_connection('udpin:localhost:14551')
    
    # Send a heartbeat
    connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                                    mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
    
    while not rospy.is_shutdown():
        
        # Wait for GPS Data Mavlink message for 2 sec(blocking=true waits for message)
        GPS_data = connection.recv_match(type='GPS_RAW_INT',blocking=True, timeout=2)

        # Ensure valid data recieved
        valid_gps_data = False
        if not GPS_data:
            GPS_string=' | GPS INFO: No GPS Data Recieved'
        elif GPS_data.get_type() == "BAD_DATA":
            GPS_string=' | GPS INFO: Bad GPS Data Recieved'
        else:
            # Message is valid, convert raw data to desired units
            valid_gps_date = True
            gps_time = GPS_data.time_usec/1000000
            lat_deg = GPS_data.lat/10000000
            lon_deg = GPS_data.lon/10000000
            alt_m = GPS_data.alt/1000
            vel_ms = GPS_data.vel/100
            fix_type = GPS_data.fix_type
            h_acc_m = GPS_data.h_acc/1000
            v_acc_m = GPS_data.v_acc/1000
            sats = GPS_data.satellites_visible
            eph = GPS_data.eph
            epv = GPS_data.eph
            cog = GPS_data.cog
            alt_ellipsoid = GPS_data.alt_ellipsoid
            vel_acc_ms = GPS_data.vel_acc/1000
            hdg_acc = GPS_data.hdg_acc
            yaw = GPS_data.yaw

            GPS_string = f" | GPS INFO: lat(deg) = {lat_deg}, lon(deg) = {lon_deg}, " \
                         f"alt(m) = {alt_m}, vel(m/s) = {vel_ms}, fix type = {fix_type}, " \
                         f"h_acc(m) = {h_acc_m}, v_acc(m) = {v_acc_m}, Sats(#) = {sats}"

        # Get signal strength info from iw command
        sig_str_cmd = os.popen('iw dev wlan0 link | grep signal').read()
        
        # Ensure command worked
        if sig_str_cmd: # wifi command succeeded
            sig_str_cmd_list = sig_str_cmd.split()

            # parse text to grab wifi RSSI signal strength in dBm
            dBm = float(sig_str_cmd_list[1])
            signal_strength_string = f"Signal Strength is {dBm} dBm on adapter wlan0"
        else: # wifi command failed
            signal_strength_string ="Wifi command failed"

        # combine GPS string and signal strength string then log and publish the wifi quality
        combined_string = signal_strength_string + GPS_string
        rospy.loginfo(combined_string)
        pub.publish(combined_string)

        # if gps and wifi data, log info as a csv file
        if valid_gps_data and sig_str_cmd:
            csv_data = [gps_time, dBm, lat_deg, lon_deg, 
                       alt_m, vel_ms, fix_type, h_acc_m,
                       v_acc_m, sats, eph, epv, cog,
                       alt_ellipsoid, vel_acc_ms, hdg_acc,
                       yaw]
            log_writer.writerow(csv_data)

        # rate.sleep attempts to sleep for time required for loop to execute at above rospy.Rate of 2 Hz
        rate.sleep()


# Run the above loop as long as ROS isn't interrupted
if __name__ == '__main__':
    try:
        loop()
    except rospy.ROSInterruptException:
        pass

