import cv2

def preprocess(img,scale = 15):
    '''
        功能：图像预处理
        :参数: img: 一张灰度图像
        :返回值:
                mask:输入图像检测横竖线后的mask（图像）
                contours: 检测mask图像得到的多个轮廓（矩形）
    '''
    thresh_img = cv2.adaptiveThreshold(~img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2) #自适应二值化
    h_img = thresh_img.copy()
    v_img = thresh_img.copy()

    # scale值越大，检测到的线数量越多

    h_size = int(h_img.shape[1] / scale)
    h_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (h_size, 1))  # 形态学因子
    h_erode_img = cv2.erode(h_img, h_structure, 1)  #腐蚀
    h_dilate_img = cv2.dilate(h_erode_img, h_structure, 1) #膨胀

    v_size = int(v_img.shape[0] / scale)
    v_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_size))  # 形态学因子
    v_erode_img = cv2.erode(v_img, v_structure, 1)
    v_dilate_img = cv2.dilate(v_erode_img, v_structure, 1)

    mask = h_dilate_img + v_dilate_img
    # joint = cv2.bitwise_and(h_dilate_img, v_dilate_img)  #横竖线的交点

    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return mask, contours