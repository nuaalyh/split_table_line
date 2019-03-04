'''
    :功能: 图像旋转校正(默认图像内有直线，否则返回原图)
    :参数: img: 需校正的图像
    :返回值: 校正后的图像
    :入口函数: rotation_correct(img)
'''


import cv2
import math
import numpy as np
from scipy import ndimage

def rotation_correct(img): #图像倾斜校正
    edges = cv2.Canny(img, 50, 150, apertureSize=3)

    # 霍夫变换
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
    if len(lines) <= 0:  #未检测到直线
        return img

    for rho, theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
    if x1 == x2 or y1 == y2:  #无需校正
        return img
    t = float(y2 - y1) / (x2 - x1)
    rotate_angle = math.degrees(math.atan(t)) # 倾斜角度
    if rotate_angle > 45:
        rotate_angle = -90 + rotate_angle
    elif rotate_angle < -45:
        rotate_angle = 90 + rotate_angle
    rotate_img = ndimage.rotate(img, rotate_angle,cval=255)
    return  rotate_img