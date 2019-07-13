import sensor, image, time
from pyb import UART
uart = UART(3,115200)#初始化串口 波特率 115200
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.
##binary_thresholds=[(0,150)]

##圆与线检测给出的两组坐标信息
class info:
    Lx1=0
    Lx2=0
    Ly1=0
    Ly2=0
    Cx=0
    Cy=0
    Cr=0

##线检测函数
def line_detect(img,min_degree,max_degree):
    for l in img.find_lines(threshold = 1000, theta_margin = 25, rho_margin = 25):
        if (min_degree <= l.theta()) and (l.theta() <= max_degree):
            info.Lx1=l.x1()
            info.Ly1=l.y1()
            info.Lx2=l.x2()
            info.Ly2=l.y2()
            ##print(l.line())
##圆检测函数
def circle_detect():
    for c in img.find_circles(threshold = 2000, x_margin = 10, y_margin = 10, r_margin = 10,
            r_min = 2, r_max = 50, r_step = 2):
        info.Cx=c.x()
        info.Cy=c.y()
        info.Cr=c.r()
        ##print(c.circle())
##A2B任务检测以及划线
def A2B_detect():
    circle_detect()
    line_detect(img,0,20)
    img.draw_line((info.Lx1,info.Ly1,info.Lx2,info.Ly2), color = (255, 255, 255))
    img.draw_circle(info.Cx, info.Cy, info.Cr , color = (255, 255, 255))

while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    A2B_detect()
    img.draw_cross(80,60,size=5)
    A2B_data=bytearray([0xAA,0xAA
        ,info.Lx1,info.Ly1
        ,info.Lx2,info.Ly2
        ,info.Cx,info.Cy
        ,0X00,0X00])
    uart.write(A2B_data)
    print(clock.fps())              # Note: OpenMV Cam runs about half as fast when connected
                                    # to the IDE. The FPS should increase once disconnected.

