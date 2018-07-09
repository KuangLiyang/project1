#encoding:utf-8
import torch
import os
import shutil
import cv2
import util
import numpy as np
from torch.multiprocessing import Pool

from darknet import Darknet19
import utils.yolo as yolo_utils
import utils.network as net_utils
from utils.timer import Timer
import cfgs.config as cfg

from resnet import getmodel
from resnet import cloth_num
def preprocess(fname):
    # return fname
    image = cv2.imread(fname)
    im_data = np.expand_dims(yolo_utils.preprocess_test((image, None, cfg.inp_size))[0], 0)
    return image, im_data, fname

def get_ImData(fname):
    im_data = np.expand_dims(yolo_utils.preprocess_test((fname, None, cfg.inp_size))[0], 0)
    return im_data
# hyper-parameters
# npz_fname = 'models/yolo-voc.weights.npz'
# h5_fname = 'models/yolo-voc.weights.h5'
Cut_Path='./result/cut/'
ClassPath='./num_class/trainclass.txt'
InfoPicPath          ='./interface/tmp/wx_info/tmp_pic.txt'
InfoPicLikePath      ='./interface/tmp/wx_info/tmp_pic_like.txt'
InfoPicPathRec       ='./interface/tmp/wx_info/tmp_rec.txt'
InfoPicLikePathRec   ='./interface/tmp/wx_info/tmp_rec_like.txt'
InfoDir='./interface/tmp/wx_info/tmp.txt'
AgeInfoDir='./num_class/ClothRetrival/AgeLists/age_cloth.txt'
StyInfoDir='./num_class/ClothRetrival/AttributeLists/style_cloth.txt'
VerInfoDir='./num_class/ClothRetrival/AttributeLists//version_cloth.txt'
ClassInfoDir='./num_class/ClothRetrival/ClassLists/class_cloth.txt'
PrinceInfoDir='./num_class/ClothRetrival/PrincesLists/cloth_prince.txt'
class NetInit(object):

    def __init__(self):
        self.img_uploader = util.FTP_Uploader()
        self.face = util.Face_Detect()
        # =================================检索列表===============================
        #年龄列表'
        self.ageLists={}
        fp_ages=open(AgeInfoDir,'r')
        for ages_lists in fp_ages:
            age_num,age_lists=ages_lists[:-1].split(':')
            self.ageLists[age_num.encode('utf-8')]=age_lists
        fp_ages.close()
        #类别列表
        self.classLists={}
        fp_classes=open(ClassInfoDir,'r')
        for classes_lists in fp_classes:
            class_num,class_lists=classes_lists[:-1].split(':')
            #print class_num
            self.classLists[class_num.encode('utf-8')]=class_lists
        fp_classes.close()
        #print self.classLists
        #款式列表
        self.versionLists={}
        fp_versions=open(VerInfoDir,'r')
        for versions_lists in fp_versions:
            print versions_lists
            version_num, version_lists = versions_lists[:-1].split(':')
            self.versionLists[version_num.encode('utf-8')] = version_lists
        fp_versions.close()
        # 风格列表
        self.styleLists = {}
        fp_styles = open(StyInfoDir, 'r')
        for styles_lists in fp_styles:
            style_num, style_lists = styles_lists[:-1].split(':')
            self.styleLists[style_num.encode('utf-8')] = style_lists
        fp_styles.close()
        # 价钱列表
        self.princeLists = {}
        fp_princes = open(PrinceInfoDir, 'r')
        for princes_lists in fp_princes:
            prince_num, prince_value = princes_lists[:-1].split('\t')
            self.princeLists[prince_num.encode('utf-8')] = prince_value
        fp_princes.close()
        #print self.princeLists
        self.bboxes=[]
        self.scores=[]
        self.cls_inds=[]
        self.cls_res = []
        self.cls_score = []
        self.cls_res_top5 = []
        self.cls_score_top5 = []
        #Init for resnet
        with open(ClassPath,'r') as file:
            num_classes=[]
            for eachline in file:
                numclass=eachline.split('\t')[-1][:-1]
                num_classes.append(numclass)
        self.num_classes=num_classes
        model_res = getmodel(restore=1)
        torch.nn.DataParallel(model_res).cuda()
        self.model_res=model_res
        self.trained_model = cfg.trained_model
        #Init for yolov2
        # trained_model = os.path.join(cfg.train_output_dir, 'darknet19_voc07trainval_exp3_158.h5')
        self.thresh = 0.5
        self.im_path = 'demo'
        # ---
        net = Darknet19()  # load model
        net_utils.load_net(self.trained_model, net)  # load weights
        # net.load_from_npz(npz_fname)
        # net_utils.save_net(h5_fname, net)
        net.cuda()  # use GPU
        net.eval()
        self.net=net
        print('load model succ...')
    #=====================================================通过cls_rec cls_score 过滤top5=================================================================================
    def top_filter_for_class(self,cls_rec,cls_score,filter_class):
        cls_rec_out=[]
        cls_score_out=[]
        len_max=max(len(cls_rec),len(cls_score))
        for num,i in cls_rec:
            if num>=len_max:
                break
            if filter_class not in i:
                continue
            cls_rec_out.append(cls_rec_out)
            cls_score_out.append(cls_score_out)

        return (cls_rec_out,cls_score_out)



    # image 原始图像 bboxes 识别框坐标 scores识别置信度 cls_res 第一个分类类别 cls_score 第一个分类置信度 f_info 识别文本信息 f_pic识别的类别信息 cls_res_top5前十个分类类别
    # cls_score_top5前十个分类置信度，f_pic_like识别的相似类别信息，f_pic_rec根据类别推荐的信息，f_pic_rec_like根据相似类别推荐的信息，cls_inds识别的大类别
    def retrival_filter(self,cloth_num,retrival_params,sex_dec,age_dec):
        # params---->sex，prince1,prince2,dress,top,bottom,version,style,age_value
        #------------------------------sex-------------------------------------------
        sex_cloth = str(cloth_num.split('_')[1])

        sex=None
        if '自动' in retrival_params[0].encode('utf-8'):
            sex = sex_dec
        elif '全选' in retrival_params[0].encode('utf-8'):
            sex=None
        elif '女装' in retrival_params[0].encode('utf-8'):
            sex = '2'
        elif '男装' in retrival_params[0].encode('utf-8'):
            sex = '1'
        #print "sex_cloth"
        #print sex_cloth
        #print sex
        #print "----------------ssssssssssssssssssssex----------------"
        #print cloth_num,sex_cloth,sex
        if sex!=None and str(sex) not in sex_cloth:
            return 0
        # else:
       # print "sex-------------------------ok------------------"

        #-----------------------------prince----------------------------------------------
        prince_cloth=float(self.princeLists[cloth_num])
        #print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
        #print prince_cloth,retrival_params[1],retrival_params[2]
        if retrival_params[1]!=None and prince_cloth<float(retrival_params[1]):
            #print "oooooooooooooooooooook1"
            return 0
        if retrival_params[2]!=None and prince_cloth>float(retrival_params[2]):
            #print "oooooooooooooooooooook2"
            return 0

        #print "prince-------------------------ok------------------"
        #-----------------------------------class-------------------------------------------------
        dress_flag=1
        if 'dress' not in cloth_num:
            dress_flag=0
        else:
            if retrival_params[3]!=None and retrival_params[3]!='全选':
                if retrival_params[3]=='不选':
                    if 'dress' in cloth_num:
                        dress_flag=0
                else:
                    dress_cloth=self.classLists[retrival_params[3].encode('utf-8')].split('\t')
                    if cloth_num not in dress_cloth:
                        dress_flag=0

        # print "==+++++++++++++++++++++++++++++++++++"
        # print retrival_params[4],cloth_num
        top_flag=1
        if 'top' not in cloth_num:
            top_flag=0
        else:
            if retrival_params[4]!=None and retrival_params[4] != '全选':
                if retrival_params[4]=='不选':
                    if 'top' in cloth_num:
                        top_flag=0
                else:
                    top_cloth=self.classLists[retrival_params[4].encode('utf-8')].split('\t')
                    if cloth_num not in top_cloth:
                        top_flag=0
        bottom_flag=1
        if 'top' in cloth_num or 'dress' in cloth_num:
            bottom_flag=0
        else:
            if retrival_params[5] != None and retrival_params[5] != '全选':
                if retrival_params[5]=='不选':
                    if 'dress' not in cloth_num and 'top' not in cloth_num:
                        bottom_flag=0
                else:
                    bottom_cloth=self.classLists[retrival_params[5].encode('utf-8')].split('\t')
                    if cloth_num not in bottom_cloth:
                        bottom_flag=0
        if dress_flag==0 and top_flag==0 and bottom_flag==0:
            return 0
        #print "class-------------------------ok------------------"
        #------------------------------------------------attribute---------------------------------------------------------------
        version_flag=1
        if retrival_params[6] != None and '全选' not in retrival_params[6]:
            version_cloth=self.versionLists[retrival_params[6].encode('utf-8')].split('\t')
            if cloth_num not in version_cloth:
                version_flag=0
        style_flag=1
        if retrival_params[7] != None and '全选' not in retrival_params[7]:
            style_cloth=self.styleLists[retrival_params[7].encode('utf-8')].split('\t')
            if cloth_num not in style_cloth:
                style_flag = 0
        if version_flag==0 or style_flag==0:
            return 0
       # print "attribute-------------------------ok------------------"
        #age
        if retrival_params[8] != None and retrival_params[8] != '全选':

            if retrival_params[8]=='自动':
                if age_dec<30:
                    age_cloth=self.ageLists['18-30'].split('\t')
                elif age_dec<60:
                    age_cloth=self.ageLists['30-40'].split('\t')
                else:
                    age_cloth = self.ageLists['40以上'].split('\t')
                age_cloth_other = self.ageLists['其他'].split('\t')
                if cloth_num not in age_cloth and cloth_num not in age_cloth_other:
                    return 0
            else:
                age_cloth=self.ageLists[retrival_params[8].encode('utf-8')].split('\t')
                if cloth_num not in age_cloth:
                    return 0
        #print 'allllllll_____ok'
        return 1

    def draw_detection_rec(self,im, bboxes, cls_inds, scores, cls_res_top, cls_score_top, f_info, f_pic,f_pic_like, f_pic_rec, f_pic_rec_like, thr=0.3,flag=1,sex_dec=0,age_dec=18,retrival_params=None):
        # draw image
        # print 'aaaaaaaaaaaaaaaaaaaaaaaa'
        # print labels
        # print bboxes
        # print scores
        # print cls_score
        cls_min=18
        rec_min=18
        dec_min=25
        #print "cls_res====================="
        #print cls_res_top
        #print cls_score_top
        colors1 = (225, 225, 0)
        colors2 = (220, 20, 60)
        imgcv = np.copy(im)
        h, w, _ = imgcv.shape
        thick = int((h + w) / 300)
        res_out=[]
        score_out=[]
        count=0
        shutil.rmtree(Cut_Path)
        os.mkdir(Cut_Path)

        for i, box in enumerate(bboxes):#遍历所有识别到的框

            cut_image = im[box[1]:box[3], box[0]:box[2]]
            if scores[i] < 0.3:
                #print "continue"
                continue
            if len(cls_score_top)<=i:
                break
            if cls_score_top[i][0] == 1 or cls_score_top[i][0] == 0:
                continue # 对应大类匹配标志 （衣服对衣服 裤子对裤子）

            if i >= len(cls_res_top):
                break
            rec_flag=0

            res_out.append([])
            score_out.append([])
            sex_flag=0
            sex=0
            for num,t1 in enumerate(cls_res_top[i]):
                # if t1 == 'inroom':
                #     continue
                if cls_inds[i] == 0:  # top
                    if ("top" not in t1):
                        continue
                elif cls_inds[i] == 1:
                    if ('skirt' not in t1):
                        continue
                elif cls_inds[i] == 2:
                    if ('dress' not in t1):
                        continue
                else:
                    if ('pants' not in t1) and ('jeans' not in t1):
                        continue
                if self.retrival_filter(t1,retrival_params,sex_dec,age_dec)==0:
                    continue
                #rec_flag=1
                # if sex_flag==0:
                #     if sex_dec:
                #         sex=sex_dec
                #     else:
                #         sex=t1.split('_')[1]
                #     sex_flag=1
                # sex_cloth = t1.split('_')[1]
                # if sex !=sex_cloth:
                #     continue

                # print "???????????????????????"
                # print res_out
                # print i
                # print t1
                if cls_score_top[i][num]<=cls_min:
                    break
                else:
                    score_out[count].append(cls_score_top[i][num])
                    res_out[count].append(t1)

            #print "len_maxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            #print res_out[count],score_out[count]
            len_max = min(len(res_out[count]),len(score_out[count]))
            #print len_max
            #print len_max
            # if rec_flag==0:
            #     continue
            label=[]
            if (score_out[count])==[]:
                continue
            #print 'score_out--------------------ok-------------------'
            if score_out[count][0] < dec_min:

                #print 'scoreeeeeeeeeeee_like'
                if score_out[count][0]>cls_min:
                    #print 'score_out_tre--------------------ok-------------------like'
                    if flag:#如果识别服装，则存截图
                        cut_for_intel = cv2.resize(cut_image,(int(1000. * float(cut_image.shape[1]) / cut_image.shape[0]), 1000))
                        cv2.imwrite(os.path.join(Cut_Path,"2_%d-%s.jpg"%(count,res_out[count][0])),cut_for_intel)
                    info_dir = res_out[count][0] + '\n'
                    f_pic_like.write(info_dir)
                    rec_num = 0

                    for i1 in range(10):
                        if i1 >= len_max:
                            break

                        if score_out[count][i1] > rec_min:
                            rec_num += 1
                            info_dir = res_out[count][i1] + '\t'
                            f_pic_rec_like.write(info_dir)
                        if rec_num >= 3:
                            break
                    f_pic_rec_like.write('\n')
                    label = 'like_' + res_out[count][0]


                    cv2.rectangle(imgcv, (box[0], box[1]), (box[2], box[3]), colors1, thick)
                    # mess = '%s: %.3f' % (label, scores[i])
                    mess = '%s: %.3f' % (label, score_out[count][0])
                    cv2.putText(imgcv, mess, (box[0], box[1] - 12), 0, 1e-3 * h, colors1, thick // 3)
                    info = "det:%0.3f\tscore:%0.3f\tclass:%s\n" % (score_out[count][0], scores[count], label)
                    f_info.write(info)
                    count += 1
            else:
                if flag:  # 如果识别服装，则存截图
                    cut_for_intel = cv2.resize(cut_image,(int(1000. * float(cut_image.shape[1]) / cut_image.shape[0]), 1000))
                    cv2.imwrite(os.path.join(Cut_Path, "1_%d-%s.jpg" % (count,res_out[count][0])), cut_for_intel)
                label = res_out[count][0]
                #print 'score_out_tre--------------------ok-------------------'
                info_dir = label + '\n'
                f_pic.write(info_dir)
                rec_num = 0
                for i1 in range(1,10):
                    #print i1
                    if i1>=len_max:
                        break
                    if score_out[count][i1] > rec_min:
                        rec_num += 1
                        info_dir = res_out[count][i1] + '\t'
                        f_pic_rec.write(info_dir)
                    if rec_num >= 3:
                        break
                f_pic_rec.write('\n')
                cv2.rectangle(imgcv, (box[0], box[1]), (box[2], box[3]), colors2, thick)

                # mess = '%s: %.3f' % (label, scores[i])
                mess = '%s: %.3f' % (label, score_out[count][0])
                cv2.putText(imgcv, mess, (box[0], box[1] - 12), 0, 1e-3 * h, (0, 255, 0), thick // 3)
                info = "det:%0.3f\tscore:%0.3f\tclass:%s\n" % (score_out[count][0], scores[count], label)
                f_info.write(info)
                count += 1
        return imgcv
    def get_dec_inds(self):
        return self.cls_inds
    def get_cloth_num(self,cut_img):
        res_num, res_score = cloth_num(cut_img, self.model_res)
        res_class=[]
        for i in res_num:
            res_class.append(self.num_classes[i])
        return res_class, res_score
    def cloth_test(self,path_in='./interface/intel_pic/pair.jpg',cut_out='./interface/cut_pic/'):
        #服装识别
        (image, im_data, im_name) = preprocess(path_in)
        im_data = net_utils.np_to_variable(im_data, is_cuda=True, volatile=True).permute(0, 3, 1, 2)
        im_name = os.path.split(im_name)[-1]
        bbox_pred, iou_pred, prob_pred = self.net(im_data)
        # to numpy
        bbox_pred = bbox_pred.data.cpu().numpy()
        iou_pred = iou_pred.data.cpu().numpy()
        prob_pred = prob_pred.data.cpu().numpy()

        # print bbox_pred.shape, iou_pred.shape, prob_pred.shape
        # print "oooooooooooooooo2"
        #self.bboxes, self.scores, self.cls_inds = yolo_utils.postprocess(bbox_pred, iou_pred, prob_pred, image.shape, cfg, self.thresh)
        bboxes, scores, cls_inds = yolo_utils.postprocess(bbox_pred, iou_pred, prob_pred, image.shape,
                                                                         cfg, self.thresh)
        #服装分类
        cls_res = []
        cls_score = []
        cls_res_top5 = []
        cls_score_top5 = []
        cut_dec=[]
        if os.path.isdir(cut_out):
            shutil.rmtree(cut_out)
        os.mkdir(cut_out)
        for i, bbox in enumerate(bboxes):

            # print "bbox",bbox
            #print "start===================================================%d" % i
            cut_image = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            res_num, res_score = cloth_num(cut_image, self.model_res)
            cls_res.append(self.num_classes[res_num[0]])
            cls_re = []
            for n in range(10):
                cls_re.append(self.num_classes[res_num[n]])
                # print "++++++++++++++++++++++++++++++"+str(n)
                # print Cnum[0][n],res_num[0]
                # print self.num_classes[Cnum[0][n]]
            # print "-------------"
            # print res_score
            # If the adjacent two types of differentiation is too small,it is considered that the category that the category can not be determined
            if res_score[0] < 12 and res_score[1] * 1.0 / res_score[0] > 0.9:
                # print res_score[1]*1.0/res_score[0]
                cls_score.append(0)
            else:
                # If two overlapping frames of the same category exceed 0.4,only the box with the largest weight is saved
                for j, obox in enumerate(bboxes[:i]):
                    # (bbox[0], bbox[1]), (bbox[2], bbox[3])
                    if obox[2] > bbox[0] and obox[3] > bbox[1] and obox[0] < bbox[2] and obox[1] < bbox[3]:
                        print "------------------------xiangjiao------------------------------"
                        box_inter = (
                        max(obox[0], bbox[0]), max(obox[1], bbox[1]), min(obox[2], bbox[2]), min(obox[3], bbox[3]))
                        area1 = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        area2 = (obox[2] - obox[0]) * (obox[3] - obox[1])
                        area_min = min((area1, area2))
                        area_inter = (box_inter[2] - box_inter[0]) * (box_inter[3] - box_inter[1])
                        # print area_min,area_inter
                        if area_inter * 1.0 / area_min >= 0.4:
                            print "====================YEEEEEES++++++++++++++++"
                            if cls_res[i] == cls_res[j]:
                                if res_score[0] > cls_score[j]:
                                    if cls_score[j] != 0:
                                        cls_score[j] = 1
                                        cls_score_top5[j][0] = 1
                                else:
                                    res_score[0] = 1
                                    break
                cls_score.append(res_score[0])
            cls_res_top5.append(cls_re)
            #print cls_score
            cls_score_top5.append(res_score)

            # print res_num
            # cls_score.append(res_score)
            # print "resnet"
            # print cls_res,cls_score

           # # cut_for_intel = cv2.resize(cut_image, (800, 500))
            print "===================================================%d" % i
            cut_for_intel = cv2.resize(cut_image, (int(1000. * float(cut_image.shape[1]) / cut_image.shape[0]), 1000))#存储识别到的服装
            cut_dec.append(cut_for_intel)
            cv2.imwrite(os.path.join(cut_out, "%d_%s" % (i, im_name)), cut_for_intel)
        #print cls_inds
        #print cls_res_top5
        return cls_inds,cls_res_top5,cls_score_top5,cut_dec

    def test(self,path_in='demo',path_out='./interface/tmp/wx_d',cut_path='./result/cut/',retrival_params=['自动',None,None,'全选','全选','全选','全选','全选','全选']):
        #Read Infomation
        #params---->sex，prince1,prince2,dress,top,bottom,version,style,age_value
        #print "Test"
        t_det = Timer()
        t_total = Timer()
        # im_fnames = ['person.jpg']
        im_fnames = sorted((fname for fname in os.listdir(path_in) if os.path.splitext(fname)[-1] == '.jpg'))  # shuffle data
        # shutil.rmtree(cut_path)
        # os.mkdir(cut_path)
        for i in im_fnames:
            im_fname =os.path.join(path_in, i)
            #im_fnames = (os.path.join(path_in, fname) for fname in im_fnames)
            #print im_fname
            self.people_sex = None
            self.people_age = 20
            if '自动' in retrival_params[0] or '自动' in retrival_params[-1]:
                try:
                    #self.img_uploader.run(im_fname)
                    self.result=self.face.run(im_fname)
                    #print self.result

                    if len(self.result)==1:
                        if self.result[0][u'faceAttributes'][u'gender']==u'female':
                            self.people_sex='2'
                        else:
                            self.people_sex='1'
                    self.people_age=self.result[0][u'faceAttributes'][u'age']
                    #print "people_sex:"
                    #print self.people_sex
                except:
                    print "can't found face identify"
                    pass

            print 'sex:'
            print self.people_sex
            #pool = Pool(processes=1)
            #print "HAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

            #for i, (image, im_data, im_name) in enumerate(pool.imap(preprocess, im_fnames, chunksize=1)):
            (image, im_data, im_name)=preprocess(im_fname)
            t_total.tic()
            im_data = net_utils.np_to_variable(im_data, is_cuda=True, volatile=True).permute(0, 3, 1, 2)
            im_name = os.path.split(im_name)[-1]
            # print im_name
            t_det.tic()
            #print "oooooooooooooooo1"
            bbox_pred, iou_pred, prob_pred = self.net(im_data)
            det_time = t_det.toc()
            # to numpy
            bbox_pred = bbox_pred.data.cpu().numpy()
            iou_pred = iou_pred.data.cpu().numpy()
            prob_pred = prob_pred.data.cpu().numpy()

            # print bbox_pred.shape, iou_pred.shape, prob_pred.shape
            #print "oooooooooooooooo2"
            self.bboxes, self.scores, self.cls_inds = yolo_utils.postprocess(bbox_pred, iou_pred, prob_pred, image.shape, cfg, self.thresh)
            #print image.shape
            #print "bboxes"
            #print bboxes
            #print "HAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            cls_res=[]
            cls_score=[]
            cls_res_top5=[]
            cls_score_top5=[]
            flag=0
            for i,bbox in enumerate(self.bboxes):
                #print "bbox",bbox
                print "start===================================================%d" % i
                cut_image=image[bbox[1]:bbox[3],bbox[0]:bbox[2]]
                res_num, res_score=cloth_num(cut_image,self.model_res)
                cls_res.append(self.num_classes[res_num[0]])
                cls_re=[]
                for n in range(10):
                    cls_re.append(self.num_classes[res_num[n]])
                    #print "++++++++++++++++++++++++++++++"+str(n)
                    #print Cnum[0][n],res_num[0]
                    #print self.num_classes[Cnum[0][n]]
                #print "-------------"
                #print res_score
                #If the adjacent two types of differentiation is too small,it is considered that the category that the category can not be determined
                if res_score[0]<12 and res_score[1]*1.0/res_score[0]>0.9:
                    #print res_score[1]*1.0/res_score[0]
                    cls_score.append(0)
                else:
                #If two overlapping frames of the same category exceed 0.4,only the box with the largest weight is saved
                    for j,obox in enumerate(self.bboxes[:i]):
                        # (bbox[0], bbox[1]), (bbox[2], bbox[3])
                        if obox[2]>bbox[0] and obox[3]>bbox[1] and obox[0]<bbox[2] and obox[1]<bbox[3]:
                            print "------------------------xiangjiao------------------------------"
                            box_inter=(max(obox[0],bbox[0]),max(obox[1],bbox[1]),min(obox[2],bbox[2]),min(obox[3],bbox[3]))
                            area1=(bbox[2]-bbox[0])*(bbox[3]-bbox[1])
                            area2=(obox[2]-obox[0])*(obox[3]-obox[1])
                            area_min=min((area1,area2))
                            area_inter=(box_inter[2]-box_inter[0])*(box_inter[3]-box_inter[1])
                            #print area_min,area_inter
                            if area_inter*1.0/area_min>=0.5:
                                print "====================YEEEEEES++++++++++++++++"
                                #if cls_res[i]==cls_res[j]:
                                if res_score[0]>cls_score[j]:
                                    if cls_score[j]!=0:
                                        cls_score[j]=1
                                        cls_score_top5[j][0]=1
                                else:
                                    res_score[0]=1
                                    break
                    cls_score.append(res_score[0])
                cls_res_top5.append(cls_re)
                #print cls_score
                cls_score_top5.append(res_score)


                #print res_num
                #cls_score.append(res_score)
                #print "resnet"
                #print cls_res,cls_score

                #cut_for_intel = cv2.resize(cut_image, (800, 500))
                #print "===================================================%d"%i
                #cut_for_intel = cv2.resize(cut_image, (int(1000. * float(cut_image.shape[1]) / cut_image.shape[0]), 1000))
                #cv2.imwrite(os.path.join(cut_path,"%d_%s"%(i,im_name)),cut_for_intel)
            self.cls_res = cls_res
            self.cls_score = cls_score
            self.cls_res_top5 = cls_res_top5
            self.cls_score_top5 = cls_score_top5
            #im2show = yolo_utils.draw_detection(image, bboxes, scores, cls_inds, cfg)
            #print "cls_inds:"
            #print type(self.cls_inds),self.cls_inds
            # print "cls_res:"
            #
            # cls_res=np.array(cls_res)
            #print type(cls_res),cls_res
            # image 原始图像 bboxes 识别框坐标 scores识别置信度 cls_res 第一个分类类别 cls_score 第一个分类置信度 f_info 识别文本信息 f_pic识别的类别信息 cls_res_top5前十个分类类别
            # cls_score_top5前十个分类置信度，f_pic_like识别的相似类别信息，f_pic_rec根据类别推荐的信息，f_pic_rec_like根据相似类别推荐的信息，cls_inds识别的大类别
            f_info = open(InfoDir, 'w')
            f_pic = open(InfoPicPath, 'w')
            f_pic_like = open(InfoPicLikePath, 'w')
            f_pic_rec = open(InfoPicPathRec, 'w')
            f_pic_rec_like = open(InfoPicLikePathRec, 'w')
            im2show = self.draw_detection_rec(image, self.bboxes,self.cls_inds, self.scores,self.cls_res_top5,self.cls_score_top5,f_info,f_pic,f_pic_like,f_pic_rec,f_pic_rec_like,sex_dec=self.people_sex,age_dec=self.people_age, retrival_params=retrival_params)
            f_info.close()
            f_pic.close()
            f_pic_like.close()
            f_pic_rec.close()
            f_pic_rec_like.close()
            #for i,j in enumerate(cls_res):
            #    info = "识别概率:%0.2f\t准确度:%0.2f\t类别:%s\n" % ((i[0][1]), i[0][0], score_class)

            if im2show.shape[0] > 1100:
                im2show = cv2.resize(im2show, (int(1000. * float(im2show.shape[1]) / im2show.shape[0]), 1000))
            # cv2.imshow('test', im2show)
            #cv2.imwrite("./result/test/{}".format(im_name), im2show)
            cv2.imwrite(os.path.join(path_out,im_name),im2show)
            total_time = t_total.toc()
            # wait_time = max(int(60 - total_time * 1000), 1)
            # cv2.waitKey(0)


                #format_str = 'frame: %d, (detection: %.1f Hz, %.1f ms) (total: %.1f Hz, %.1f ms)'
                #print(format_str % (i, 1. / det_time, det_time * 1000, 1. / total_time, total_time * 1000))

        t_total.clear()
        t_det.clear()
        #print "End"
        #pool.terminate()


    def test_ontime(self,path_in='demo',path_out='./interface/tmp/wx_d',dec_flag=0, cv_im=[],da_flag=1,retrival_params=['自动',None,None,'全选','全选','全选','全选','全选','全选']):
        #Read Infomation

        #print "Test"
        t_det = Timer()
        t_total = Timer()
        # if dec_flag==1:
        #     shutil.rmtree("./result/cut/")
        #     os.mkdir("./result/cut/")
        # im_fnames = ['person.jpg']
        im_fnames = sorted((fname for fname in os.listdir(path_in) if os.path.splitext(fname)[-1] == '.jpg'))  # shuffle data
        im_fname = os.path.join(path_in, im_fnames[0])

        if cv_im==[]:
            (image, im_data, im_name) = preprocess(im_fname)
            exit()
        else:
            #print "OOOOOOOOOOOOOOOOOOOOOOJBK"
            image=cv_im
            im_name=im_fname
            im_data=get_ImData(cv_im)

        t_total.tic()
        im_data = net_utils.np_to_variable(im_data, is_cuda=True, volatile=True).permute(0, 3, 1, 2)
        im_name = os.path.split(im_name)[-1]
        # print im_name
        t_det.tic()

        if dec_flag:
            self.people_sex = None
            self.people_age = 20
            #if retrival_params[0] == '自动' or retrival_params[-1] == '自动':
            if '自动' in retrival_params[0] or '自动' in retrival_params[-1]:
                try:
                    #self.img_uploader.run(im_fname)
                    self.result = self.face.run(im_fname)
                    #print self.result

                    if len(self.result) == 1:
                        if self.result[0][u'faceAttributes'][u'gender'] == u'female':
                            self.people_sex = '2'
                        else:
                            self.people_sex = '1'
                    #print "people_sex:"
                    #print self.people_sex
                except:
                    print "can't contact face identify"
                    pass
            #print 'sex:'
            #print self.people_sex
            #print "ooooooooooooooooooooooooooooooooooooooooooo"
            #print "oooooooooooooooo1"
            #print "oook"
            bbox_pred, iou_pred, prob_pred = self.net(im_data)
            det_time = t_det.toc()
            det_time = t_det.toc()
            # to numpy
            bbox_pred = bbox_pred.data.cpu().numpy()
            iou_pred = iou_pred.data.cpu().numpy()
            prob_pred = prob_pred.data.cpu().numpy()

            # print bbox_pred.shape, iou_pred.shape, prob_pred.shape
            #print "oooooooooooooooo2"
            self.bboxes, self.scores, self.cls_inds = yolo_utils.postprocess(bbox_pred, iou_pred, prob_pred, image.shape, cfg, self.thresh)
            #print image.shape
            #print "bboxes"
            #print bboxes
            #print "HAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            cls_res=[]
            cls_score=[]
            cls_res_top5=[]
            cls_score_top5=[]
            flag=0
            for i,bbox in enumerate(self.bboxes):
                #print "bbox",bbox
                cut_image=image[bbox[1]:bbox[3],bbox[0]:bbox[2]]
                res_num, res_score=cloth_num(cut_image,self.model_res)
                cls_res.append(self.num_classes[res_num[0]])
                cls_re=[]
                for n in range(10):
                    cls_re.append(self.num_classes[res_num[n]])
                    #print "++++++++++++++++++++++++++++++"+str(n)
                    #print Cnum[0][n],res_num[0]
                    #print self.num_classes[Cnum[0][n]]
                cls_res_top5.append(cls_re)
                cls_score_top5.append(res_score)
                #print "-------------"
                #print res_score
                #If the adjacent two types of differentiation is too small,it is considered that the category that the category can not be determined
                if res_score[0]<12 and res_score[1]*1.0/res_score[0]>0.9:
                    #print res_score[1]*1.0/res_score[0]
                    cls_score.append(0)
                else:
                #If two overlapping frames of the same category exceed 0.4,only the box with the largest weight is saved
                    for j,obox in enumerate(self.bboxes[:i]):
                        # (bbox[0], bbox[1]), (bbox[2], bbox[3])
                        if obox[2]>bbox[0] and obox[3]>bbox[1] and obox[0]<bbox[2] and obox[1]<bbox[3]:
                            print "------------------------xiangjiao------------------------------"
                            box_inter=(max(obox[0],bbox[0]),max(obox[1],bbox[1]),min(obox[2],bbox[2]),min(obox[3],bbox[3]))
                            area1=(bbox[2]-bbox[0])*(bbox[3]-bbox[1])
                            area2=(obox[2]-obox[0])*(obox[3]-obox[1])
                            area_min=min((area1,area2))
                            area_inter=(box_inter[2]-box_inter[0])*(box_inter[3]-box_inter[1])
                            #print area_min,area_inter
                            if area_inter*1.0/area_min>=0.5:
                                print "====================YEEEEEES++++++++++++++++"
                                #if cls_res[i]==cls_res[j]:
                                if res_score[0]>cls_score[j]:
                                    if cls_score[j]!=0:
                                        cls_score[j]=1
                                else:
                                    res_score[0]=1
                                    break
                    cls_score.append(res_score[0])


                #print res_num
                #cls_score.append(res_score)
                #print "resnet"
                #print cls_res,cls_score

                #cut_for_intel = cv2.resize(cut_image, (800, 500))
                #cut_for_intel = cv2.resize(cut_image,(int(1000. * float(cut_image.shape[1]) / cut_image.shape[0]), 1000))
                #cv2.imwrite("./result/cut/%d_%s"%(i,im_name),cut_for_intel)
            self.cls_res        =cls_res
            self.cls_score      =cls_score
            self.cls_res_top5   =cls_res_top5
            self.cls_score_top5 =cls_score_top5
            #print "bbboxes"
            #print self.bboxes
            # im2show = yolo_utils.draw_detection_rec(image, self.bboxes, self.scores, self.cls_res,self.cls_score,f_info,f_pic,self.cls_res_top5,self.cls_score_top5,f_pic_like,f_pic_rec,f_pic_rec_like,self.cls_inds)
        else:
            # 用于显示
            #print "bbboxes"
            #print self.bboxes
            #im2show = yolo_utils.draw_detection_rec(image, self.bboxes, self.scores, self.cls_res,self.cls_score,f_info,f_pic,self.cls_res_top5,self.cls_score_top5,f_pic_like,f_pic_rec,f_pic_rec_like,self.cls_inds)
            f_info = open(InfoDir, 'w')
            f_pic = open(InfoPicPath, 'w')
            f_pic_like = open(InfoPicLikePath, 'w')
            f_pic_rec = open(InfoPicPathRec, 'w')
            f_pic_rec_like = open(InfoPicLikePathRec, 'w')
            im2show = self.draw_detection_rec(image, self.bboxes,self.cls_inds, self.scores, self.cls_res_top5, self.cls_score_top5, f_info,f_pic, f_pic_like, f_pic_rec, f_pic_rec_like,flag=1,sex_dec=self.people_sex,age_dec=self.people_age, retrival_params=retrival_params)
            if im2show.shape[0] > 1100:
                im2show = cv2.resize(im2show, (int(1000. * float(im2show.shape[1]) / im2show.shape[0]), 1000))
            cv2.imwrite(os.path.join(path_out,im_name),im2show)
            f_info.close()
            f_pic.close()
            f_pic_like.close()
            f_pic_rec.close()
            f_pic_rec_like.close()

        t_total.clear()
        t_det.clear()
    #print "End"
    #pool.terminate()


if __name__=='__main__':
     Init=NetInit()
     #while(1):
     Init.test(path_in='./demo/',path_out='./result/test/')