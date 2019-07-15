import sensor, image, time
from pyb import UART
from pyb import LED
uart = UART(3,115200)                   #初始化串口 波特率 115200
sensor.reset()                          # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)      # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)         # Wait for settings take effect.
clock = time.clock()                    # Create a clock object to track the FPS.
#============================================================================================#
red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)

TaskNum=2   ##任务选择
#============================================================================================#
##圆与线检测给出的两组坐标信息
#检测失败就发送200(160*120)
class info:
    Lx1=200
    Lx2=200
    Ly1=200
    Ly2=200
    Cx=200
    Cy=200
    Cr=200

    L_x1=200
    L_x2=200
    L_y1=200
    L_y2=200
#============================================================================================#
##交叉点
class cross_point:
    x=200
    y=200
    exist_flag=0 ##存在标志
##LED提示函数
def Led_Indicating():
    if(info.Lx1!=200 and info.Cx!=200):
            green_led.on()
            red_led.off()
            blue_led.off()
    elif(info.Lx1==200 and info.Cx!=200):
            red_led.on()
            blue_led.off()
            green_led.off()
    elif(info.Lx1!=200 and info.Cx==200):
            blue_led.on()
            red_led.off()
            green_led.off()
    elif(info.Lx1==200 and info.Cx==200):
            red_led.off()
            blue_led.off()
            green_led.off()

#============================================================================================#
##线检测函数
def Line_Detect(img,min_degree,max_degree):
    info.Lx1=200
    info.Ly1=200
    info.Lx2=200
    info.Ly2=200
    for l in img.find_lines(threshold = 1000, theta_margin = 25, rho_margin = 25):
        if (min_degree <= l.theta()) and (l.theta() <= max_degree):
            info.Lx1=l.x1()
            info.Ly1=l.y1()
            info.Lx2=l.x2()
            info.Ly2=l.y2()
            ##print(l.line())
#============================================================================================#
##圆检测函数
def Circle_Detect(img):
    info.Cx=200
    info.Cy=200
    info.Cr=200
    for c in img.find_circles(threshold = 2000, x_margin = 10, y_margin = 10, r_margin = 10,
            r_min = 2, r_max = 50, r_step = 2):
        info.Cx=c.x()
        info.Cy=c.y()
        info.Cr=c.r()
        ##print(c.circle())
#============================================================================================#
##两线交点检测函数
def CorssPoint_Detect(img):
    cross_point.exist_flag=1
    Line_Detect(img,80,100)  ##检测横线
    if (info.Lx1==200):
        cross_point.exist_flag=0
    else:
        L_x1=info.Lx1
        L_y1=info.Ly1
        L_x2=info.Lx2
        L_y2=info.Ly2
    Line_Detect(img,0,20)   ##检测纵线
    if (info.Lx1==200):
        cross_point.exist_flag=0

    if (cross_point.exist_flag==1):
        img.draw_line((info.Lx1,info.Ly1,info.Lx2,info.Ly2), color = (255, 255, 255))
        img.draw_line((info.L_x1,info.L_y1,info.L_x2,info.L_y2), color = (255, 255, 255))

        k2=(L_y1-L_y2)/(L_x1-L_x2)
        b1=Ly2-k1*Lx2
        b2=L_y2-k2*L_x2
        if (Lx1==Lx2):      ##纵线竖直
            cross_piont.y=60
            cross_piont.x=(cross_piont.y-b2)/k2
        else:
            k1=(Ly1-Ly2)/(Lx1-Lx2)
            cross_piont.y=(b1*k2-k1*b2)/(k2-k1)
            cross_piont.x=(cross_piont.y-b2)/k2
         img.draw_circle(cross_piont.x, cross_piont.y, 3)
    elif (cross_point.exist_flag==0):
        cross_piont.y=200
        cross_piont.x=200

#============================================================================================#
##A2B任务
def A2B_Task(img):
    Circle_Detect(img)
    line_detect(img,0,20)
    img.draw_line((info.Lx1,info.Ly1,info.Lx2,info.Ly2), color = (255, 255, 255))
    img.draw_circle(info.Cx, info.Cy, info.Cr , color = (255, 255, 255))
    A2B_data=bytearray([0xAA,0xAA
        ,info.Lx1,info.Ly1
        ,info.Lx2,info.Ly2
        ,info.Cx,info.Cy
        ,0X00,0X00,0X00,0X00])
    uart.write(A2B_data)
#============================================================================================#
##转圈循迹任务
def Circle_Task(img):
    Circle_Detect(img)
    CorssPoint_Detect(img)
    CorssPoint_data=bytearray
        ([0xAA,0xAA
        ,cross_piont.x,cross_piont.y
        ,0xAA,0xAA
        ,info.Cx,info.Cy
        ,0X00,0X00,0X00,0X00])
    uart.write(CorssPoint_data)
#============================================================================================#


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
#============================================================================================#
    if(TaskNum==1):         ##A2B任务
        A2B_Task(img)
    elif(TaskNum==2):       ##转圈循迹任务
        Circle_Task(img)
#============================================================================================#
    img.draw_cross(80,60,size=5)    ##img中心表征飞机位置
    Led_Indicating()                ##红圆 蓝线 绿全 灭无
    print(clock.fps())              # Note: OpenMV Cam runs about half as fast when connected
                                    # to the IDE. The FPS should increase once disconnected.
#==========================================end===============================================#
