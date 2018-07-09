import torch
import os
import cv2

import numpy as np
from torch.multiprocessing import Pool

from darknet import Darknet19
import utils.yolo as yolo_utils
import utils.network as net_utils
from utils.timer import Timer
import cfgs.config as cfg


def preprocess(fname):
    # return fname
    image = cv2.imread(fname)
    im_data = np.expand_dims(yolo_utils.preprocess_test((image, None, cfg.inp_size))[0], 0)
    return image, im_data, fname


# hyper-parameters
# npz_fname = 'models/yolo-voc.weights.npz'
# h5_fname = 'models/yolo-voc.weights.h5'
trained_model = cfg.trained_model
# trained_model = os.path.join(cfg.train_output_dir, 'darknet19_voc07trainval_exp3_158.h5')
thresh = 0.1
#im_path = 'demo'
dir_path='demo'
# ---

net = Darknet19()#load model
net_utils.load_net(trained_model, net)#load weights
# net.load_from_npz(npz_fname)
# net_utils.save_net(h5_fname, net)
net.cuda()#use GPU
net.eval()
print('load model succ...')

t_det = Timer()
t_total = Timer()
# im_fnames = ['person.jpg']
for n,par in enumerate(sorted(os.listdir(dir_path))) :
    print "hahahaha"
    im_path=os.path.join(dir_path,par)
    #im_fnames = sorted((fname for fname in os.listdir(im_path) if os.path.splitext(fname)[-1] == '.JPG'))#shuffle data
    im_fnames = sorted(fname for fname in os.listdir(im_path) if os.path.splitext(fname)[-1] == '.JPG' or os.path.splitext(fname)[-1] == '.jpg')
    print im_fnames
    print im_path
    im_fnames = (os.path.join(im_path, fname) for fname in im_fnames)
    print "ooook"
    #print im_fnames
    #pool = Pool(processes=1)
    cut_path='./result/demo_our/'+par
    #cut_path = './result/cut_cloth/' + 'top_1_00%d'%n
    if not os.path.isdir(cut_path):
        os.mkdir(cut_path)
    #for i, (image, im_data,im_name) in enumerate(pool.imap(preprocess, im_fnames, chunksize=1)):
    #for i, (image, im_data, im_name) in enumerate(preprocess(im_fnames)):
    for i,fname in enumerate(im_fnames):
        try:
            (image, im_data, im_name)=preprocess(fname)
        except:
            print "picture error"
            continue
        t_total.tic()
        im_data = net_utils.np_to_variable(im_data, is_cuda=True, volatile=True).permute(0, 3, 1, 2)
        im_name=os.path.split(im_name)[-1]
        print im_name
        t_det.tic()
        bbox_pred, iou_pred, prob_pred = net(im_data)
        det_time = t_det.toc()
        # to numpy
        bbox_pred = bbox_pred.data.cpu().numpy()
        iou_pred = iou_pred.data.cpu().numpy()
        prob_pred = prob_pred.data.cpu().numpy()

        # print bbox_pred.shape, iou_pred.shape, prob_pred.shape

        bboxes, scores, cls_inds = yolo_utils.postprocess(bbox_pred, iou_pred, prob_pred, image.shape, cfg, thresh)
        for num, bbox in enumerate(bboxes):
            cut_image = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            cv2.imwrite(os.path.join(cut_path,str(num)+'_'+im_name), cut_image)
        im2show = yolo_utils.draw_detection(image, bboxes, scores, cls_inds, cfg)

        if im2show.shape[0] > 1100:
            im2show = cv2.resize(im2show, (int(1000. * float(im2show.shape[1]) / im2show.shape[0]), 1000))
        #cv2.imshow('test', im2show)
        cv2.imwrite("./result/test/{}".format(im_name), im2show)
        total_time = t_total.toc()
        # wait_time = max(int(60 - total_time * 1000), 1)
        #cv2.waitKey(0)


        if i % 1 == 0:
            format_str = 'frame: %d, (detection: %.1f Hz, %.1f ms) (total: %.1f Hz, %.1f ms)'
            print(format_str % (
                i, 1. / det_time, det_time * 1000, 1. / total_time, total_time * 1000))

            t_total.clear()
            t_det.clear()

