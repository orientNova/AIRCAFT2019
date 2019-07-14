import sensor, image, time
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_auto_gain(False)            #颜色识别关闭自动增益
sensor.set_auto_whitebal(False)        #颜色识别关闭白平衡
clock = time.clock()                # Create a clock object to track the FPS.

black=(-255,-100,0,0,0,0)##red = (minL, maxL, minA, maxA, minB, maxB)
##image.find_blobs(thresholds, roi=Auto, x_stride=2, y_stride=1, invert=False, area_threshold=10, pixels_threshold=10, merge=False, margin=0, threshold_cb=None, merge_cb=None)


while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    for blob1 in image.find_blobs([black])
        img.draw_rectangle(blob1.rect())
        img.draw_cross(blob1.cx(),blob1.cy())

    print(clock.fps())
