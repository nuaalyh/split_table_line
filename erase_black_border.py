'''
    :功能: 去除图像黑边
    :参数: img: 输入图像(灰度图像)
           position：需要处理的位置，可选择：TOP(图片顶边),BOTTOM(图片底边),ALL(四边全部)
           auto_threshold：True:自动计算边框去黑边阈值，False：默认设置5
    :返回值: 去除黑边后的图像
    :入口函数: erase_img_black_border(img, position='ALL', auto_threshold = False)
'''

import cv2
from preprocess import preprocess


def locate_index(ls,flag,ratio_threshold): #定位索引，确定去黑边的阈值，阈值设置最佳[0.7,0.8]
    res = 0
    ls_reverse = ls[::-1]
    if flag == 'asc':  # 升序：从左到右
        for i in range(len(ls)):
            if ls[i] > ratio_threshold:
                res = i + 1 # +1是因为剪切位置 = 黑边位置 + 1个像素
    elif flag == 'desc': #降序：从右到左
        for i in range(len(ls)):
            if ls_reverse[i] > ratio_threshold:
                res = i + 1
    return res + 1 # 这里+1是因为获得mask的腐蚀步骤腐蚀了一点边缘

def calc_erase_threshold(img):

    h, w = img.shape
    mask,  _ = preprocess(img)

    row_top_sum = []
    row_bottom_sum = []
    col_left_sum = []
    col_right_sum = []

    total_row = w * 255
    total_col = h * 255

    for i in range(15):  # 计算最上十行的每行亮度值占比
        sum = 0
        for j in range(w):
            sum += mask[i][j]
        row_top_sum.append(sum / total_row)
    top_threshold = locate_index(row_top_sum, 'asc', 0.7)

    for i in range(h - 15, h):  # 计算最下十行的每行亮度值占比
        sum = 0
        for j in range(w):
            sum += mask[i][j]
        row_bottom_sum.append(sum / total_row)
    bottom_threshold = locate_index(row_bottom_sum,'desc',0.8)

    for j in range(15):  # 计算最左十列的每列亮度值占比
        sum = 0
        for i in range(h):
            sum += mask[i][j]
        col_left_sum.append(sum / total_col)
    left_threshold = locate_index(col_left_sum,'asc',0.7)

    for j in range(w - 15, w):  # 计算最右十列的每列亮度值占比
        sum = 0
        for i in range(h):
            sum += mask[i][j]
        col_right_sum.append(sum / total_col)
    right_threshold = locate_index(col_right_sum,'desc',0.8)

    return top_threshold, bottom_threshold, left_threshold, right_threshold

def erase_img_black_border(img, position='all', auto_threshold = True):

    h, w = img.shape

    if auto_threshold:
        top_threshold, bottom_threshold, left_threshold, right_threshold = calc_erase_threshold(img)
    else:
        top_threshold, bottom_threshold, left_threshold, right_threshold = 7,5,5,5

    # print(top_threshold, bottom_threshold, left_threshold, right_threshold)

    if position ==  "top":
        for j in range(top_threshold):
            img[j,:] = 255
    elif position == "bottom":
        for j in range(h - bottom_threshold, h):
            img[j,:] = 255
    elif position == "all":
        for j in range(top_threshold): #上边阈值以内的行设为白色
            img[j,:] = 255
        for j in range(h - bottom_threshold, h): #下边
            img[j,:] = 255
        for i in range(left_threshold): #左边
            img[:,i] = 255
        for i in range(w - right_threshold, w): #右边
            img[:,i] = 255
    else:
        print("Parameter Error！")

    return img