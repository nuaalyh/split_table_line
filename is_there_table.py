'''
    检测图像中是否存在表格
    :参数: img: 一张灰度图像
           mask, contours: preprocess函数输出
    :返回值: True: 输入图像中存在表格
            False: 输入图像中不存在表格
'''

import cv2

def is_there_table(img, mask, contours):

    h, w = img.shape
    contours_candidate = []  #对检测到的mask中的矩形框进行筛选
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area < 0.02 * h * w:  # 文件中最小的一张表格面积占整页的4%，所以设置阈值为整页面积的2%，若检测的轮廓面积大小小于阈值，则认为没有表格
            continue
        contours_candidate.append(cnt)
    size = len(contours_candidate)
    if size <= 0:
        return False
    else:
        return True