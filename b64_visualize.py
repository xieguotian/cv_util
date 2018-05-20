import numpy as np
import sys
import cv2
import base64
import matplotlib.pyplot as plt
from matplotlib.image import  imsave
import argparse
from collections import OrderedDict
import os

'''
normalize image in a square box, with keeping ratio of width and height.

param:
    img: image that to be normailized.
    box_len: the target width of the square box.
'''
def norm_image(img,box_len=100):
    ih,iw = img.shape[:2]

    if ih>=iw:
        nh = np.int(box_len)
        nw = np.int(np.round(np.float(box_len) / ih * iw))
    else:
        nw = np.int(box_len)
        nh = np.int(np.round(np.float(box_len) / iw * ih))

    nimg = np.zeros((box_len,box_len,3),np.uint8)
    #nimg = np.random.randint(0,255,(1,1,3))
    harf_h = np.int((box_len - nh) / 2)
    harf_w = np.int((box_len - nw) / 2)

    nimg_tmp = cv2.resize(img,(nw,nh))
    nimg[harf_h:harf_h+nimg_tmp.shape[0],harf_w:harf_w+nimg_tmp.shape[1],:]  =  nimg_tmp
    return nimg

'''
shown image in a sqaure tiles.

param:
    image_tuple: a sequence of images to be shown, color images ( channel==3 ).
    box_len: the Width of square box to show one image.
    boder: boder width among images.
'''
def show_tile(image_tuple,box_len=100,boder=10):
    num_image = len(image_tuple)
    show_height = np.int(np.ceil(np.sqrt(num_image)))
    show_width = np.int(show_height)

    box_height = np.int(box_len + boder)
    box_width = np.int(box_len + boder)
    channel = 3
    #out_array = np.zeros((box_height*show_height,box_width*show_width,channel),np.uint8)
    out_array = np.tile(np.random.randint(0,256,(1,1,channel)),(box_height*show_height,box_width*show_width,1)).astype(np.uint8)
    for ix,img in enumerate(image_tuple):
        r = np.int(ix / show_height)
        c = ix % show_height

        nimg = norm_image(img,box_len)
        out_array[r*box_height:r*box_height+nimg.shape[0],
        c*box_width:c*box_width+nimg.shape[1],:] = nimg
    return out_array[:,:,[2,1,0]]

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "b64_file_name",
        help="file of b64 format file name. with format: key\\timage\\tlabel"
    )
    parser.add_argument(
        "--num_images_per_screen",
        type=int,
        default=400,
        help="number of images to be shown per screen."
    )
    parser.add_argument(
        "--box_width",
        type=int,
        default=100,
        help="width of box to show one image"
    )
    parser.add_argument(
        "--boder_width",
        type=int,
        default=2,
        help="width of boder among images"
    )
    parser.add_argument(
        "--b64_pos_line",
        type=str,
        default="",
        help="file contains information of position of each line of base64"
    )
    parser.add_argument(
        "--save_folder",
        type=str,
        default="",
        help="save folder for display"
    )
    parser.add_argument(
        "--not_display",
        action='store_true',
        help="display or not"
    )
    parser.add_argument(
        "--group",
        action='store_true',
        help="display or not"
    )
    parser.add_argument(
        "--show_all",
        action='store_true',
        help='show all image in a group'
    )
    parser.add_argument(
        "--not_sort",
        action='store_true',
        help='sort key'
    )
    args = parser.parse_args()
    file_name = args.b64_file_name
    step = args.num_images_per_screen
    box_width = args.box_width
    boder_width = args.boder_width
    b64_pos_line = args.b64_pos_line
    save_folder = args.save_folder
    not_display = args.not_display
    is_grouped = args.group
    show_all = args.show_all
    not_sort = args.not_sort

    if not save_folder=="":
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

    count = 0
    with open(file_name) as fid:
        img_arr = []
        label_arr = []
        if b64_pos_line=="":
            for line in fid:
                str = line.split('\t')
                if len(str)>=3:
                    label_arr.append(np.int(str[2]))
                    image_b64 = str[1].split(' ')[0].strip()
                else:
                    label_tmp = str[1].split(' ')
                    image_b64 = label_tmp[0].strip()
                    if len(label_tmp)>=2:
                        label_arr.append(np.int(label_tmp[1]))
                img_tmp = np.array(bytearray(base64.b64decode(image_b64)),np.uint8)
                img = cv2.imdecode(img_tmp,cv2.CV_LOAD_IMAGE_COLOR)
                img_arr.append(img)
                if (not not_display):
                    print img.shape

                count+=1
                if(count%step)==0:
                    print "number %d"%(count/step)
                    tile_imgs = show_tile(img_arr,box_width,boder_width)
                    if not save_folder=="":
                        imsave(save_folder+"/%06d.png"%(count/step),tile_imgs)
                    if (not not_display):
                        plt.imshow(tile_imgs)
                        plt.title('images %d-%d'%(count-step+1,count))
                        print label_arr
                        plt.show()
                    img_arr = []
                    label_arr = []
        else:
            if not is_grouped:
                with open(b64_pos_line) as fid2:
                    for line in fid2:
                        str_tmp = line.split('\t')
                        pos = np.int64(str_tmp[2])
                        fid.seek(pos)
                        line = fid.readline()
                        str = line.split('\t')
                        if len(str)>=3:
                            label_arr.append(np.int(str[2]))
                            image_b64 = str[1].split(' ')[0].strip()
                        else:
                            label_tmp = str[1].split(' ')
                            image_b64 = label_tmp[0].strip()
                            if len(label_tmp)>=2:
                                label_arr.append(np.int(label_tmp[1]))
                        img_tmp = np.array(bytearray(base64.b64decode(image_b64)),np.uint8)
                        img = cv2.imdecode(img_tmp,cv2.CV_LOAD_IMAGE_COLOR)
                        img_arr.append(img)
                        if (not not_display):
                            print img.shape

                        count+=1
                        if(count%step)==0:
                            print "number %d"%(count/step)
                            tile_imgs = show_tile(img_arr,box_width,boder_width)
                            if not save_folder=="":
                                imsave(save_folder+"/%06d.png"%(count/step),tile_imgs)
                            if (not not_display):
                                plt.imshow(tile_imgs)
                                plt.title('images %d-%d'%(count-step+1,count))
                                print label_arr
                                plt.show()
                            img_arr = []
                            label_arr = []
            else:
                group_dict = OrderedDict()
                with open(b64_pos_line) as fid2:
                    for line in fid2:
                        str_tmp = line.split('\t')
                        pos = np.int64(str_tmp[2])
                        label = np.int64(str_tmp[1])
                        image_key = str_tmp[0]

                        if label in group_dict:
                            group_dict[label].append([image_key,pos])
                        else:
                            group_dict[label] = [[image_key,pos]]
                num_show_group = np.uint32(np.sqrt(step))
                count = 0
                if not not_sort:
                    all_keys = sorted(group_dict)
                else:
                    all_keys = group_dict.keys()
                for idx,key in enumerate(all_keys):
                    group = group_dict[key]
                    len_g = len(group)
                    print len(group)
                    #print group
                    #for _,pos in group[:num_show_group]:
                    if show_all:
                        g_idx_all=0
                        while g_idx_all < len_g:
                            for g_idx in range(g_idx_all,g_idx_all+num_show_group):
                                if g_idx >= len_g:
                                    img_arr.append(np.zeros((100, 100, 3)))
                                    continue
                                pos = group[g_idx][1]
                                fid.seek(pos)
                                line = fid.readline()
                                str = line.split('\t')
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
                                img_arr.append(img)
                                if (not not_display):
                                    print img.shape
                            g_idx_all += num_show_group
                            count = count + 1
                            if g_idx_all >= len_g:
                                while not(count % (num_show_group) == 0):
                                    for g_idx in range(num_show_group):
                                        img_arr.append(np.zeros((100, 100, 3)))
                                    count = count+1
                            if count % (num_show_group) == 0:
                                print "number %d" % (count / num_show_group)
                                tile_imgs = show_tile(img_arr, box_width, boder_width)
                                if not save_folder == "":
                                    imsave(save_folder + "/%04d_%04d_%06d.png" % (idx,key,count / num_show_group), tile_imgs)
                                if (not not_display):
                                    plt.imshow(tile_imgs)
                                    plt.title('images %d-%d' % (count - num_show_group + 1, count))
                                    print label_arr
                                    plt.show()
                                img_arr = []
                                label_arr = []
                    else:
                        for g_idx in range(num_show_group):
                            if g_idx>=len_g:
                                img_arr.append(np.zeros((100,100,3)))
                                continue
                            pos = group[g_idx][1]
                            fid.seek(pos)
                            line = fid.readline()
                            str = line.split('\t')
                            if len(str)>=3:
                                label_arr.append(np.int(str[2]))
                                image_b64 = str[1].split(' ')[0].strip()
                            else:
                                label_tmp = str[1].split(' ')
                                image_b64 = label_tmp[0].strip()
                                if len(label_tmp)>=2:
                                    label_arr.append(np.int(label_tmp[1]))
                            img_tmp = np.array(bytearray(base64.b64decode(image_b64)),np.uint8)
                            img = cv2.imdecode(img_tmp,cv2.CV_LOAD_IMAGE_COLOR)
                            img_arr.append(img)
                            if (not not_display):
                                print img.shape
                        count = count + 1
                        if count % (num_show_group) == 0:
                            print "number %d"%(count/num_show_group)
                            tile_imgs = show_tile(img_arr,box_width,boder_width)
                            if not save_folder=="":
                                imsave(save_folder+"/%06d.png"%(count/num_show_group),tile_imgs)
                            if (not not_display):
                                plt.imshow(tile_imgs)
                                plt.title('images %d-%d'%(count-num_show_group+1,count))
                                print label_arr
                                plt.show()
                            img_arr = []
                            label_arr = []
                step = num_show_group



        if(count%step)!=0:
            while True:
                for g_idx in range(num_show_group):
                    img_arr.append(np.zeros((100, 100, 3)))
                count+=1
                if count %(num_show_group)==0:
                    break
            print "number %d"%(count/step)
            tile_imgs = show_tile(img_arr,box_width,boder_width)
            if not save_folder=="":
                imsave(save_folder+"/%06d.png"%(count/step),tile_imgs)
            if (not not_display):
                plt.imshow(tile_imgs)
                plt.title('images %d-%d'%(count-step+1,count))
                print label_arr
                plt.show()
            img_arr = []
            label_arr = []
        print "end of data base of b64."







