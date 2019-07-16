import sensor, image, time
from pyb import UART
from pyb import LED
from math import floor
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

TaskNum=1   ##任务选择
#============================================================================================#
##圆与线检测给出的两组坐标信息
#检测失败就发送200(160*120)
class info_class:
    Lx1=200
    Lx2=200
    Ly1=200
    Ly2=200
    theta=200
    rho=200
    Cx=200
    Cy=200
    Cr=200

    L_x1=200
    L_x2=200
    L_y1=200
    L_y2=200
    Test_flag=0
info=info_class()
#============================================================================================#
##交叉点
class cross_point_class:
    x=80
    y=60
    exist_flag=0 ##存在标志
cross_point=cross_point_class()
#============================================================================================#
##接收
class receive(object):
    uart_buf = []
    _data_len = 0
    _data_cnt = 0
    state = 0
Receive=receive()
#============================================================================================#
#串口通信协议接收
def Receive_Prepare(data):

    if Receive.state==0:

        if data == 0xAA:#帧头
            Receive.state = 1
            Receive.uart_buf.append(data) #将数据保存到数组里面
        else:
            Receive.state = 0

    elif Receive.state==1:
        if data == 0xAF:#帧头
            Receive.state = 2
            Receive.uart_buf.append(data) #将数据保存到数组里面
        else:
            Receive.state = 0

    elif Receive.state==2:
        if data <= 0xFF:#数据个数
            Receive.state = 3
            Receive.uart_buf.append(data) #将数据保存到数组里面
        else:
            Receive.state = 0

    elif Receive.state==3:
        if data <= 33:
            Receive.state = 4
            Receive.uart_buf.append(data) #将数据保存到数组里面
            Receive._data_len = data
            Receive._data_cnt = 0
        else:
            Receive.state = 0

    elif Receive.state==4:
        if Receive._data_len > 0:
            Receive. _data_len = Receive._data_len - 1
            Receive.uart_buf.append(data) #将数据保存到数组里面
            if Receive._data_len == 0:
                Receive.state = 5
        else:
            Receive.state = 0

    elif Receive.state==5:
        Receive.state = 0
        Receive.uart_buf.append(data) #将数据保存到数组里面
        Receive_Anl(Receive.uart_buf,Receive.uart_buf[3]+5) #还原数据个数，数据的总个数为6
        Receive.uart_buf=[]#清空缓冲区，准备下次接收数据
    else:
        Receive.state = 0

#============================================================================================#
#读取串口缓存
def uart_read_buf():
    i = 0
    buf_size = uart.any() #判断是否有串口数据
    while i<buf_size:
        Receive_Prepare(uart.readchar()) #读取串口数据
        i = i + 1
#============================================================================================#
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
    info.theta=200
    info.rho=200
    for l in img.find_lines(threshold = 1000, theta_margin = 25, rho_margin = 25):
        if (min_degree <= l.theta()) and (l.theta() <= max_degree):
            info.Lx1=l.x1()
            info.Ly1=l.y1()
            info.Lx2=l.x2()
            info.Ly2=l.y2()
            info.theta=l.theta()
            info.rho=l.rho()
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
    k1=200
    k2=200
    b1=200
    b2=200
    cross_point.y=200
    cross_point.x=200
    cross_point.exist_flag=1
    info.Test_flag=2
    Line_Detect(img,60,120)  ##检测横线
    if (info.Lx1==200):
        cross_point.exist_flag=0
        info.Test_flag-=1
    else:
        info.L_x1=info.Lx1
        info.L_y1=info.Ly1
        info.L_x2=info.Lx2
        info.L_y2=info.Ly2
    Line_Detect(img,0,30)   ##检测纵线
    if (info.L_x1==200):
        cross_point.exist_flag=0
        info.Test_flag-=1

    if (cross_point.exist_flag==1):
        img.draw_line((info.Lx1,info.Ly1,info.Lx2,info.Ly2), color = (255, 255, 255))
        img.draw_line((info.L_x1,info.L_y1,info.L_x2,info.L_y2), color = (255, 255, 255))

        k2=(info.L_y1-info.L_y2)/(info.L_x1-info.L_x2)
        b1=info.Ly2-k1*info.Lx2
        b2=info.L_y2-k2*info.L_x2
        if (info.Lx1==info.Lx2):      ##纵线竖直
            cross_point.x=info.Lx1
            cross_point.y=k2*info.Lx1+b2
        elif (info.L_y1==info.L_y2):   ##横线水平
            cross_point.y=info.L_y1
            cross_point.x=(info.L_y1-b1)/k1
        else:
            k1=(info.Ly1-info.Ly2)/(info.Lx1-info.Lx2)
            cross_point.y=(b1*k2-k1*b2)/(k2-k1)
            cross_point.x=(cross_point.y-b2)/k2

#============================================================================================#
##A2B任务
def A2B_Task(img):
    Circle_Detect(img)
    Line_Detect(img,0,30)
    img.draw_line((info.Lx1,info.Ly1,info.Lx2,info.Ly2), color = (255, 255, 255))
    img.draw_circle(info.Cx, info.Cy, info.Cr , color = (255, 255, 255))
    A2B_data=bytearray([0xAA,0xAA
        ,info.rho,info.theta
        ,info.Cx,info.Cy
        ,0X00,0X00
        ,0X00,0X00
        ,0X00,0X00])
    uart.write(A2B_data)
#============================================================================================#
##转圈循迹任务
def Circle_Task(img):
    Circle_Detect(img)
    CorssPoint_Detect(img)
    ##img.draw_circle(info.Cx, info.Cy, info.Cr , color = (255, 255, 255))
    img.draw_circle(floor(cross_point.x), floor(cross_point.y),5, color = (255, 255, 255))
    img.draw_line((info.Lx1,info.Ly1,info.Lx2,info.Ly2), color = (255, 255, 255))
    img.draw_line((info.L_x1,info.L_y1,info.L_x2,info.L_y2), color = (255, 255, 255))
    CorssPoint_data=bytearray([0xAA,0xAA
        #,cross_point.x,cross_point.y
        ,info.Cx,info.Cy
        ,0X00,0X00
        ,0X00,0X00
        ,0X00,0X00])
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
    #print(clock.fps())              # Note: OpenMV Cam runs about half as fast when connected
                                    # to the IDE. The FPS should increase once disconnected.

    #print(info.Test_flag)
    print(info.theta)
    print(info.rho)
#==========================================end===============================================#

