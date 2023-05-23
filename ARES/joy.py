#!/usr/bin/env python

import rospy
import roslaunch
from sensor_msgs.msg import Joy, CompressedImage, Imu
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Int16
import torch
import cv2
from PIL import Image
import numpy as np
import pandas
from tf.transformations import euler_from_quaternion
from math import pi

uuid = roslaunch.rlutil.get_or_generate_uuid( None, False )
roslaunch.configure_logging( uuid )
joy_launch_file = "/home/samet/Desktop/Arayuz7/joy.launch"
roslaunch_parent = roslaunch.parent.ROSLaunchParent( uuid, [joy_launch_file] )
pub = rospy.Publisher('compressed_image_topic_2', CompressedImage, queue_size=1)

model = torch.hub.load("/home/samet/yolov5", "custom", "/home/samet/yolov5/best_m.pt", source="local")

hiz=Twist()
hiz.linear.x = 0.0
hiz.angular.z = 0.0

maxHizSiniri = 0.5 
minHizSiniri = -0.5
hizDegistirmeMiktari = 0.01
basamakSayisi = maxHizSiniri / hizDegistirmeMiktari 

def HizAlma(hizVerisi):
    global hiz, kontrol
    if kontrol == 1 or kontrol == -2:
        hiz.linear.x = hizVerisi.linear.x
        hiz.angular.z = hizVerisi.angular.z
        rospy.Publisher( "/cmd_vel", Twist, queue_size=1 ).publish( hiz ) 
        print("Lineer Hiz: ", hiz.linear.x)
        print("Acisal Hiz: ", hiz.angular.z)

yaw = 0.0
def ImuAlma(imuVerisi):
    global kontrol, ilk_yaw, yaw
    rot_q = imuVerisi.orientation
    (roll, pitch, yaw) = euler_from_quaternion([rot_q.x, rot_q.y, rot_q.z, rot_q.w])

def HizYayinlama():
    global hiz, hizDegistirmeMiktari
    rospy.Publisher( "/cmd_vel", Twist, queue_size=1 ).publish( hiz ) 
    print("Lineer Hiz: ", hiz.linear.x)
    print("Acisal Hiz: ", hiz.angular.z)

def Dur():
    global hiz, hizDegistirmeMiktari
    print("DUR!")
    for i in range( int( abs( ( hiz.linear.x ) * 10 * ( 0.1 / hizDegistirmeMiktari ) ) ) ):
        if hiz.linear.x > 0:
            hiz.linear.x -= hizDegistirmeMiktari
        else:
            hiz.linear.x += hizDegistirmeMiktari
        HizYayinlama()
    for i in range( int( abs( (hiz.angular.z) * 10 * ( 0.1 / hizDegistirmeMiktari ) ) ) ):
        if hiz.angular.z > 0:
            hiz.angular.z -= hizDegistirmeMiktari
        else:
            hiz.angular.z += hizDegistirmeMiktari
            HizYayinlama()

def LineerHizArttirma():
    global hiz, hizDegistirmeMiktari
    if hiz.linear.x < maxHizSiniri:
        hiz.linear.x += hizDegistirmeMiktari
        HizYayinlama()

def LineerHizAzaltma():
    global hiz, hizDegistirmeMiktari
    if hiz.linear.x > minHizSiniri:
        hiz.linear.x -= hizDegistirmeMiktari
        HizYayinlama()

def AcisalHizArttirma():
    global hiz, hizDegistirmeMiktari
    if hiz.angular.z < maxHizSiniri:
        hiz.angular.z += hizDegistirmeMiktari
        HizYayinlama()

def AcisalHizAzaltma():
    global hiz, hizDegistirmeMiktari
    if hiz.angular.z > minHizSiniri:
        hiz.angular.z -= hizDegistirmeMiktari
        HizYayinlama()

def JoystickAcisalHizAyarlama(veri):
    global hiz
    hiz.angular.z = veri
    HizYayinlama()

def JoystickLineerHizAyarlama(veri):
    global hiz
    hiz.linear.x = veri
    HizYayinlama()

bitkiTespiti=0 
def BitkiIslemleri(bitkiTespitiKontrolu):
    global bitkiTespiti
    bitkiTespiti = bitkiTespitiKontrolu.data
    print("Bitki Tespiti: ", bitkiTespiti)

# def EskiYolaDon():
#     global kontrol, yaw, ilk_yaw, bitkiTespiti
#     hiz.linear.x = 0.0
#     print(ilk_yaw, yaw)
#     if (ilk_yaw - yaw) > 0.03:
#         hiz.angular.z = -0.170
#         print("Sagaaaa")
#     elif (ilk_yaw - yaw) < -0.03:
#         hiz.angular.z = 0.170
#         print("Solaaa")
#     else:
#         print("Donus Bitti")
#         hiz.angular.z = 0.0
#         bitkiTespiti = 0
#     HizYayinlama()
        
def Don(istenilenYaw):
    global hiz, kontrol, bitkiTespiti, number_pub
    hiz.linear.x = 0.0
    print("Istek Yaw", istenilenYaw)
    if ( istenilenYaw >= ( ( -1 ) * pi ) and istenilenYaw <= ( ( -1 ) * ( pi / 2 ) ) and yaw > ( pi / 2 ) and yaw < ( pi ) ) or ( istenilenYaw >= ( pi / 2 ) and istenilenYaw <= ( pi ) and yaw < ( ( -1 ) * ( pi / 2 ) ) and yaw > ( ( -1 ) * pi ) ):
        if istenilenYaw-yaw > 0.05:
            print("Saga")
            hiz.angular.z = -0.25
            HizYayinlama()
        elif istenilenYaw-yaw < -0.05:
            print("Sola")
            hiz.angular.z = 0.25
            HizYayinlama()
        else:
            print("Donus Bitti")
            hiz.angular.z = 0.0
            HizYayinlama()
            bitkiTespiti = 3
            number_pub.publish(3)
    else:
        if istenilenYaw-yaw > 0.05:
            print("Sola")
            hiz.angular.z = 0.25
            HizYayinlama()
        elif istenilenYaw-yaw < -0.05:
            print("Saga")
            hiz.angular.z = -0.25
            HizYayinlama()
        else:
            print("Donus Bitti")
            hiz.angular.z = 0.0
            HizYayinlama()
            bitkiTespiti = 3
            number_pub.publish(3)

number_pub = rospy.Publisher('/bitki_tespiti', Int16, queue_size=1)
sayac = 0
ilk_yaw = 0.0
geciciKontrol = 0
def OtonomIslemler(kameraVerisi):
    global kontrol, bitkiTespiti, sayac, geciciKontrol, ilk_yaw, number_pub
    merkezKontrolu=0
    np_arr = np.frombuffer(kameraVerisi.data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    #frame = cv2.resize(frame, (1280, 720))
    if kontrol == 2:
        sayac += 1
        if sayac % 7 == 0:
            sayac = 0
            if bitkiTespiti == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                results = model(pil_image)
                df = results.pandas().xyxy[0]
                sonuc_list = df.values.flatten().tolist()
                try:
                    centerY = int( ( sonuc_list[1]+sonuc_list[3] ) / 2 )
                    ilkX = int(sonuc_list[0])
                    sonX = int(sonuc_list[2])
                    centerX = int( ( sonuc_list[0]+sonuc_list[2] ) / 2 )
                    merkezKontrolu = 1
                except IndexError: 
                    print("Bitki Bulunamadi")
                    hiz.linear.x = 0.20
                    HizYayinlama()
            if merkezKontrolu == 1:
                if bitkiTespiti == 0: 
                    if len(sonuc_list) != 0:
                        cv2.circle(frame, (ilkX, 350), 5, (0, 0, 255), 5)
                        cv2.circle(frame, (sonX, 350), 5, (0, 0, 255), 5)
                        if geciciKontrol==0:
                            ilk_yaw = yaw
                            print("Ilk Yaw: ", yaw)
                            geciciKontrol=1
                        if centerY > 450:#500
                            hiz.linear.x = 0.0
                            if ilkX < 400:
                                hiz.angular.z = 0.3 #0.230
                            elif sonX > 800:
                                hiz.angular.z = -0.3#-0.230
                            else:
                                hiz.angular.z = 0.0
                                bitkiTespiti=1
                                number_pub.publish(bitkiTespiti)
                        else:
                            hiz.linear.x = 0.17 #0.20 
                        HizYayinlama()
                    else:
                        hiz.linear.x = 0.16#0.20
                        HizYayinlama()
                print("Bitki Bulundu!")
                text = f"{sonuc_list[6]} {sonuc_list[4]:.2f}"
                cv2.rectangle(frame, (round(int(sonuc_list[0]),0), round(int(sonuc_list[1]),0)), (round(int(sonuc_list[2]),0), round(int(sonuc_list[3]),0)), (0, 0, 255), 2)
                cv2.rectangle(frame, (round(int(sonuc_list[0]),0), round(int(sonuc_list[1]),0)), (round(int(sonuc_list[0]),0)+200, round(int(sonuc_list[1]),0)-50), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, text, (round(int(sonuc_list[0])) + 10, round(int(sonuc_list[1])) - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            if bitkiTespiti == 2:
                print("Eski Yola Donuluyor")
                Don(ilk_yaw)    
            elif bitkiTespiti == 4:
                bitkiTespiti = 0
                print("Yeni Bitki Aranmaya Baslaniyor!")
                
            
    cv2.line( frame, (0, 450), (1280, 450), (0, 0, 0), thickness = 2 )
    cv2.line( frame, (400, 0), (400, 720), (0, 0, 0), thickness = 2 )
    cv2.line( frame, (800, 0), (800, 720), (0, 0, 0), thickness = 2 )
    encode_param = [ int( cv2.IMWRITE_JPEG_QUALITY ), 100 ]
    ( _, img_encoded ) = cv2.imencode( '.jpeg', frame, encode_param )
    msg = CompressedImage()
    msg.header.stamp = rospy.Time.now()
    msg.format = "jpeg"
    msg.data = img_encoded.tobytes()
    pub.publish(msg)
    
 
kontrol = -1
def KontrolIslemleri( kontrolVerisi ):
    global roslaunch_parent, kontrol
    kontrol = int( kontrolVerisi.data )
    print("Kontrol: ", kontrol)
    if kontrol == -1:
        Dur()
        roslaunch_parent.shutdown()
    elif kontrol == 0:
        roslaunch_parent = roslaunch.parent.ROSLaunchParent( uuid, [joy_launch_file] )
        roslaunch_parent.start()
        rospy.loginfo("Joystick Moda Geciliyor!")
    elif kontrol == 1:
        roslaunch_parent.shutdown()
        rospy.loginfo("Arayuz Moda Geciliyor")
    elif kontrol == 2:
        rospy.loginfo("Otonom Moda Geciliyor")

def JoystickIslemleri(joystickVerisi):
    global basamakSayisi
    if joystickVerisi.buttons[0] == 1: #Yesil tus
        Dur()
    if joystickVerisi.axes[7] == 1: #Siyah ust tus
        LineerHizArttirma()
    elif joystickVerisi.axes[7] == -1: #Siyah alt tus
        LineerHizAzaltma()
    if joystickVerisi.axes[6] == 1: #Siyah sol tus
        AcisalHizArttirma()
    elif joystickVerisi.axes[6] == -1: #Siyah sag tus
        AcisalHizAzaltma() 
    if joystickVerisi.axes[3] != 0: #Sag Joysitck Sola-Saga
        JoystickAcisalHizAyarlama( hizDegistirmeMiktari * int( joystickVerisi.axes[3] * ( basamakSayisi ) ) ) #Hizi olceklendirip gonderiyoruz.
    if joystickVerisi.axes[1] != 0: #Sol Joystick Ileri-Geri
        JoystickLineerHizAyarlama( hizDegistirmeMiktari * int( joystickVerisi.axes[1] * ( basamakSayisi ) ) )

def kapatma():
    rospy.loginfo("Kapatiliyor!")
    Dur()
    
roslaunch.pmon._init_signal_handlers()
rospy.init_node('joy_topic_launcher', anonymous=True)   
# rospy.Subscriber('/imu/data', Imu, ImuAlma) 
rospy.Subscriber('/cmd_vel1', Twist, HizAlma) 
rospy.Subscriber("/joy", Joy, JoystickIslemleri) 
rospy.Subscriber("/modKontrolu", String, KontrolIslemleri) 
rospy.Subscriber("/zed2/zed_node/rgb_raw/image_raw_color/compressed", CompressedImage, OtonomIslemler) 
rospy.Subscriber("/ilac", Int16, BitkiIslemleri)
rospy.Subscriber('/imu/data', Imu, ImuAlma) 
rospy.on_shutdown(kapatma)
rospy.spin()
