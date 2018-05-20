import numpy as np
import cv2
import base64

def resize_image_preserve_ratio(img,scale):
    height,width = img.shape[:2]
    if height < width:
        ratio = scale / float(height)
        height = scale
        width = int(ratio * width)
    elif width < height:
        ratio = scale / float(width)
        height = int(ratio * height)
        width = scale
    else:
        height = scale
        width = scale

    img_tmp = cv2.resize(img,(width,height))
    return img_tmp

def read_one_image_from_b64(db,key_pos):
    db.seek(key_pos)
    line = db.readline()
    str = line.split('\t')
    label_arr = []
    if len(str) >= 3:
        label_arr.append(np.int(str[2]))
        image_b64 = str[1].split(' ')[0].strip()
    else:
        label_tmp = str[1].split(' ')
        image_b64 = label_tmp[0].strip()
        if len(label_tmp) >= 2:
            label_arr.append(np.int(label_tmp[1]))
    img_tmp = np.array(bytearray(base64.b64decode(image_b64)), np.uint8)
    img = cv2.imdecode(img_tmp, cv2.CV_LOAD_IMAGE_COLOR)
    return img