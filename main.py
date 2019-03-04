'''
识别图片中的表格并分割图像：将图像分为三部分：
第一部分是表格以上内容，第二部分是表格分割的单元格集合（二维列表），第三部分是表格以下内容
入口函数：split_img(img)
'''

import cv2
import numpy as np
import os
from preprocess import preprocess
from is_there_table import is_there_table
from rotation_correct import rotation_correct
from erase_black_border import erase_img_black_border

def showimg(img,windowname = ""): #显示图像
    cv2.namedWindow(windowname,cv2.WINDOW_NORMAL)
    cv2.imshow(windowname,img)
    cv2.waitKey()

def simplify_list(ls): #简化列表，去除列表中十分相近的元素
    ls = sorted(ls)
    res = [ls[0]]
    for i in range(len(ls) - 1):
        if ls[i + 1] - ls[i] > 10:
            res.append(ls[i + 1])  # 去除相近的元素
    return res

def max_rect(contours):
    max_contour = contours[0]
    max_area = 0
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            max_contour = cnt
    x, y, w, h = cv2.boundingRect(max_contour)
    return x,y,w,h


def detect_table(img, mask, contours, pattern): #检测表格横线竖线
    '''
        检测图中表格的水平和竖直直线
        :参数: img: 一张有表格的灰度图像，没有表格的图像处理会出现错误
               mask, contours: preprocess函数输出
               pattern: 'line':检测行
                        'cell':检测行和列
        :返回值: hors: 图片表格的水平直线的纵坐标的列表
                 vers: 图片表格的垂直直线的横坐标的列表
    '''


    # 默认一页只有一张表情况下
    '''
    表格定位
    '''
    # 找到最大的矩形框，代表表格
    x,y,w,h = max_rect(contours)

    minLineLength = 200
    maxLineGap = 15
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 80, minLineLength, maxLineGap) #霍夫变换检测横线
    hors = []  # 存储横线纵坐标
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            # cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255)) #画直线
            y_diff = abs(y1 - y2)  # 横线
            if y_diff < 2 and y < y1 < y + h:  # 检测table范围内的水平横线
                hors.append(y1)
    hors = simplify_list(hors) #去除重复的横线

    if pattern == 'line':
        return hors,x,w

    '''
    上述霍夫变换检测横线效果好，但是检测竖线效果不佳，漏检情况较严重。所以竖线检测采用以下新的方法
    '''
    mid_of_cell = []  # 表格横向单元格上下中点位置
    for i in range(len(hors) - 1):
        mid_of_cell.append(np.int(np.ceil((hors[i] + hors[i + 1]) / 2)))
    # print(mid_of_cell)
    vers = []  #存储竖线横坐标
    for j in mid_of_cell:  # 遍历像素找竖线位置，竖线横坐标存储在ver_res中
        temp = []
        for i in range(x - 10, x + w + 10):  # table边框宽范围以内(边缘范围适当扩充)
            if mask[j][i] > 253:
                temp.append(i)
        # print(temp)
        vers = list(set(vers) | set(temp))
    vers = simplify_list(vers)

    if pattern == 'cell':
        return hors,vers






def split_img(img, mask,  contours, pattern = 'cell'):
    '''
        分割图像，将图像分为三部分：
        第一部分是表格以上内容，第二部分是表格分割的单元格集合（二维列表），第三部分是表格以下内容
        :参数: img: 输入图像
               mask, contours: preprocess函数输出
               pattern: 'line':表格部分按行分割
                        'cell':表格部分按列分割
        :返回值: 分割后的图像列表，第一个元素是表格以上内容，第二个元素是表格分割的单元格集合（二维列表），第三个元素是表格以下内容
    '''
    res = []

    if pattern == 'line':
        hors,x,w = detect_table(img,mask,contours,pattern)
        m = len(hors) - 1  # 表格行
        tablelines = [0 for row in range(m)]
        for i in range(m):
            tablelines[i] = img[hors[i]:hors[i+1], x : x + w ]
            # tablelines[i] = erase_img_black_border(tablelines[i])
            # showimg(tablelines[i])
            cv2.imwrite("./result/2/table_line/table_line_{}.png".format(i),tablelines[i])
        res.append(img[:hors[0] - 1, :])
        res.append(tablelines)
        res.append(img[hors[-1] + 1:, :])  # 表格以下部分
        # 去除黑边
        res[0] = erase_img_black_border(res[0], 'bottom', False)
        res[2] = erase_img_black_border(res[2], 'top', False)
        return  res

    elif pattern == 'cell':
        hors, vers = detect_table(img, mask,  contours)
        m = len(hors) - 1 #表格行
        n = len(vers) - 1 # 表格列

        tablecells = [ [0 for col in range(n)] for row in range(m)]
        for i in range(m):
            for j in range(n):
                # print(i,j)
                tablecells[i][j] = img[hors[i]:hors[i+1],vers[j]:vers[j+1]]
                # showimg(tablecells[i][j])
                tablecells[i][j] = erase_img_black_border(tablecells[i][j])
                # showimg(tablecells[i][j])
                # cv2.imwrite("./result/13/new/{}-{}.png".format(i,j),tablecells[i][j])
        res.append(img[:hors[0] - 1, :])
        res.append(tablecells)
        res.append(img[hors[-1] + 1:, :])  # 表格以下部分
        # 去除黑边
        res[0] = erase_img_black_border(res[0], 'bottom', False)
        res[2] = erase_img_black_border(res[2], 'top', False)
        return res

    else:
        print("Wrong pattern parameter!")


    

if __name__=='__main__':
    src_img = cv2.imread('result/2/new/0-0.png')
    src_img1 = cv2.imread('result/2/new/0-1.png')
    # src_img = rotation_correct(src_img)
    # src_img = cv2.resize(src_img,(800,1000)) #size = (w,h) 必须resize到（800，1000）这个尺寸
    # showimg(src_img)
    if src_img is None:
        print("Image read failed!")
        os._exit(1)
    if len(src_img.shape) == 3:
        img = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)


    # mask, contours = preprocess(img)

    # cv2.imwrite("9_mask_resize.png",mask)
    # res = [] #结果
    # if is_there_table(img, mask, contours):
    #     res = split_img(img, mask,  contours)
    #     # print(np.array(res[1]).shape) #检查表格分割后的单元格数量
    # else:
    #     res.append(img)
    #     # print(len(res)) #等于1代表无表格图像返回自身


    # x,y,w,h = max_rect(contours)
    # hors = []

    # row_sum = []
    #
    # for i in range(y+5,y+h-5):
    #     sum = 0
    #     for j in range(x+5,x+w-10): # +5,-10是将左右两边排除
    #         sum += mask[i][j]
    #     row_sum.append(sum)
    # print(row_sum)
    # for i in range(len(row_sum)):
    #     if row_sum[i] > 0:
    #         hors.append(i)
    #
    # hors = [i+y for i in hors]
    # print(hors)
    # res = [hors[0]]
    # for i in range(len(hors) - 1):
    #     if hors[i+1] - hors[i] > 2:
    #         res.append(hors[i+1])
    #
    # print(res)





