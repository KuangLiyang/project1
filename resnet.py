#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 15:27:17 2017

@author: flyvideo
"""
import torch
import random

import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim
import torch.utils.data
import torchvision.transforms as transforms
import torchvision.models as models
import torch.utils.data as data
import resnet_pattern

import numpy as np
import cv2 as cv
import PIL
import time
import os
import shutil
import gc
from PIL import Image
import anno_test
import anno_train
import expand
import Init
import GetIntelPic


CutImgPath=   './result/cut/'
TrainImgPath= './num_class/ClothForClassify_train/'
OutModelPath ='./num_class/out_models/'
OutModelPathGray ='./num_class/out_models_gray/'
OutModelPathColor ='./num_class/out_models_color/'
GetModelPath ='./num_class/model_for_test/resnet_cloth.pth'
GetModelPath_Gray='./num_class/model_for_test/resnet_cloth_gray.pth'

GetModelPathForTrain='./num_class/model_for_test/resnet_cloth_for_train.pth'
GetModel='./num_class/model_for_test/resnet_cloth_combine_train.pth'
TestModel='./num_class/model_for_test/resnet_cloth.pth'
AnnoPath=     './num_class/'

imgSize = 224
Train_num=118

if os.path.isdir(TrainImgPath):
    TrainList = os.listdir(TrainImgPath)
    Train_num = len(TrainList)
    print Train_num
else:
    print "%s Not exist" % TrainImgPath

labelimg = []
for i in range(Train_num):
    labelimg.append('0')
#print labelimg
with open('./num_class/trainclass.txt', 'r') as f:
    for line in f:
        label, img = line.split('\t')
        labelimg[int(label)] = img[:-1]
    f.close()

class DogDataSet(data.Dataset):
    def __init__(self, root, annFile, batchsize=32,transform=None,faster = False):
        self.root = root
        self.ann = annFile  
        self.transform = transform
        self.batchsize = batchsize
        self.getImg_and_Label()
        self.faster = faster
        #self.shuffle()
        if(len(self.imglist) % self.batchsize ==0):
            self.minibatch_num = len(self.imglist) // self.batchsize
        else:
            if len(self.imglist)%self.batchsize!=0:
                self.minibatch_num = len(self.imglist) // self.batchsize + 1
            else:
                self.minibatch_num = len(self.imglist) // self.batchsize

    def cross_change(self,annFile):
        del self.imglist
        gc.collect()

        self.ann = annFile
        self.getImg_and_Label()

        if(len(self.imglist) % self.batchsize ==0):
            self.minibatch_num = len(self.imglist) // self.batchsize
        else:
            if len(self.imglist)%self.batchsize!=0:
                self.minibatch_num = len(self.imglist) // self.batchsize + 1
            else:
                self.minibatch_num = len(self.imglist) // self.batchsize

    def getImg_and_Label(self):
        self.imglist = []
        self.labellist = []
        with open(self.ann,'r') as f:
            lines = f.readlines()
            for line in lines:
                label,img = line.split('\t')
                #print label
                self.imglist.append(img[:-1])
                self.labellist.append(int(label))

    def shuffle(self):
        count  = len(self.imglist)
        random_index = range(count)
        random.shuffle(random_index)
        self.imglist = np.array(self.imglist)[random_index].tolist()
        self.labellist = np.array(self.labellist)[random_index].tolist()
        
    def transform_PIL_to_torch(self,img_PIL,transform):
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
        if self.faster:
            if transform == 'train:':
                transform = transforms.Compose([                       
                        #transforms.Scale((224,224)),
                        transforms.RandomHorizontalFlip(),
                        transforms.ToTensor(),
                        normalize,])
            else:
                transform = transforms.Compose([
                        #transforms.Scale(224),
                        #transforms.CenterCrop(imgSize),
                        transforms.ToTensor(),
                        normalize,])     
        else:
            if transform == 'train:':
                transform = transforms.Compose([
                        #transforms.RandomSizedCrop(imgSize),
                        #transforms.Scale((224,224)),
                        #transforms.RandomHorizontalFlip(),
                        transforms.ToTensor(),
                        normalize,])
            else:
                transform = transforms.Compose([
                        transforms.Scale(imgSize+200),
                        transforms.CenterCrop(imgSize),
                        transforms.ToTensor(),
                        normalize,])     
        return  transform(img_PIL) 
           
    def __getitem__(self, index):
        if (index+1 == self.minibatch_num):
            imgs = self.imglist[index*self.batchsize:]
            labels = self.labellist[index*self.batchsize:]
        else:
            imgs = self.imglist[index*self.batchsize:(index+1)*self.batchsize]
            labels = self.labellist[index*self.batchsize:(index+1)*self.batchsize]
                
        if (self.transform == None):
            imgs_np = np.zeros((len(imgs),3,imgSize,imgSize))
            labels_np = np.zeros(len(imgs))  
            for index in range(len(imgs)):
                img_np = cv.imread(self.root+'/'+imgs[index])
                imgs_np[index] = cv.resize(img_np,(imgSize,imgSize)).transpose([2,0,1])                
                labels_np[index] = labels[index]      
                
                imgs_np =  imgs_np/255 - 0.5  
            imgs_torch = torch.from_numpy(imgs_np).float().cuda()
            labels_torch = torch.from_numpy(labels_np).long().cuda()
            
        else:  
            imgs_torch = torch.zeros((len(imgs),3,imgSize,imgSize))
            labels_np = np.zeros(len(imgs))
            for index in range(len(imgs)):
                if self.faster:
                    #img_PIL = PIL.Image.open(self.root+'/'+imgs[index]).convert('RGB').resize((224,224))
                    img_PIL = PIL.Image.open( imgs[index]).convert('RGB').resize((imgSize, imgSize))
                else:
                    #img_PIL = PIL.Image.open(self.root+'/'+imgs[index]).convert('RGB').resize((256,256))
                    img_PIL = PIL.Image.open( imgs[index]).convert('RGB').resize((imgSize,imgSize))
                img_torch = self.transform_PIL_to_torch(img_PIL,self.transform)
                imgs_torch[index] = img_torch
                labels_np[index] = labels[index]      
            labels_torch = torch.from_numpy(labels_np).long().cuda()    
        return imgs_torch.cuda(),labels_torch           
    
    def __len__(self):
        return self.minibatch_num

class DogDataSet_class(data.Dataset):
    def __init__(self, root,annFile=None, batchsize=32, transform=None, faster=False):
        self.root = root
        #self.ann = annFile
        self.transform = transform
        self.batchsize = batchsize
        self.faster = faster

        self.imglist = []
        self.labellist = []
        self.imglist.append(self.root+annFile)
        self.labellist.append(0)
        # self.shuffle()
        if (len(self.imglist) % self.batchsize == 0):
            self.minibatch_num = len(self.imglist) // self.batchsize
        else:
            if len(self.imglist)%self.batchsize!=0:
                self.minibatch_num = len(self.imglist) // self.batchsize + 1
            else:
                self.minibatch_num = len(self.imglist) // self.batchsize

    def shuffle(self):
        count = len(self.imglist)
        random_index = range(count)
        random.shuffle(random_index)
        self.imglist = np.array(self.imglist)[random_index].tolist()
        self.labellist = np.array(self.labellist)[random_index].tolist()

    def transform_PIL_to_torch(self, img_PIL, transform):
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])
        if self.faster:
            if transform == 'train:':
                transform = transforms.Compose([
                    # transforms.Scale((224,224)),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    normalize, ])
            else:
                transform = transforms.Compose([
                    # transforms.Scale(224),
                    # transforms.CenterCrop(imgSize),
                    transforms.ToTensor(),
                    normalize, ])
        else:
            if transform == 'train:':
                transform = transforms.Compose([
                    transforms.RandomSizedCrop(imgSize),
                    # transforms.Scale((224,224)),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    normalize, ])
            else:
                transform = transforms.Compose([
                    transforms.Scale(256),
                    transforms.CenterCrop(imgSize),
                    transforms.ToTensor(),
                    normalize, ])
        return transform(img_PIL)

    def __getitem__(self, index):
        if (index + 1 == self.minibatch_num):
            imgs = self.imglist[index * self.batchsize:]
            labels = self.labellist[index * self.batchsize:]
        else:
            imgs = self.imglist[index * self.batchsize:(index + 1) * self.batchsize]
            labels = self.labellist[index * self.batchsize:(index + 1) * self.batchsize]

        if (self.transform == None):
            imgs_np = np.zeros((len(imgs), 3, imgSize, imgSize))
            labels_np = np.zeros(len(imgs))
            for index in range(len(imgs)):
                img_np = cv.imread(self.root + '/' + imgs[index])
                imgs_np[index] = cv.resize(img_np, (imgSize, imgSize)).transpose([2, 0, 1])
                labels_np[index] = labels[index]

                imgs_np = imgs_np / 255 - 0.5
            imgs_torch = torch.from_numpy(imgs_np).float().cuda()
            labels_torch = torch.from_numpy(labels_np).long().cuda()

        else:
            imgs_torch = torch.zeros((len(imgs), 3, imgSize, imgSize))
            labels_np = np.zeros(len(imgs))
            for index in range(len(imgs)):
                if self.faster:
                    # img_PIL = PIL.Image.open(self.root+'/'+imgs[index]).convert('RGB').resize((224,224))
                    img_PIL = PIL.Image.open(imgs[index]).convert('RGB').resize((imgSize, imgSize))
                else:
                    # img_PIL = PIL.Image.open(self.root+'/'+imgs[index]).convert('RGB').resize((256,256))
                    img_PIL = PIL.Image.open(imgs[index]).convert('RGB')
                img_torch = self.transform_PIL_to_torch(img_PIL, self.transform)
                imgs_torch[index] = img_torch
                labels_np[index] = labels[index]
            labels_torch = torch.from_numpy(labels_np).long().cuda()
        return imgs_torch.cuda(), labels_torch

    def __len__(self):
        return self.minibatch_num
def getmodel(restore):
    resnet = models.resnet101(pretrained=True)
    #resnet = resnet_pattern.resnet_new(pretrained=False)
    #resnet = models.resnet_combine(pretrained=True)
    #print resnet
    #Train_num=71
        #exit()
    #Train_num = 119
    #resnet.add_module(name='drop',module=nn.Dropout(0.2))
    print Train_num
    resnet.fc = torch.nn.Linear(2048, Train_num)

    def weight_init(m):
    	if isinstance(m, nn.Linear):
    		size = m.weight.size()
    		fan_out = size[0] # number of rows
    		fan_in = size[1] # number of columns
    		variance = np.sqrt(2.0/(fan_in + fan_out))
    		m.weight.data.normal_(0.0, variance)
#==============================================================================
#     resnet = models.inception_v3(pretrained=True)
#     resnet.fc = torch.nn.Linear(2048, 100)
#==============================================================================
    
    if restore==1:
        print "restore==1"
        print "66666666666666666666666666666666666666666"
    #======================================
	#加载模型，此处修改模型名称
	#=====================================

        #weight_name = '/home/flyvideo_2016/py-faster-rcnn-master/tools/resnet_cloth_25 Fri Sep 15 15:51:20 2017.pth'#resnet_cloth_35 Wed Aug 30 23:30:45 2017.pth'
        weight_name = GetModelPath
        pretrained_model = torch.load(weight_name)
        resnet.load_state_dict(pretrained_model)
    elif restore==2:
        weight_name = GetModelPath_Gray
        pretrained_model = torch.load(weight_name)
        resnet.load_state_dict(pretrained_model)
    elif restore==3:
        weight_name = GetModelPathForTrain
        pretrained_model = torch.load(weight_name)
        resnet.load_state_dict(pretrained_model)
    elif restore==4:
        pretrained_model = torch.load(GetModel)
        resnet.load_state_dict(pretrained_model)

    return resnet
def train(train_loader, model, criterion, optimizer,Cross_flag,accuracy, epoch):
    #model.train()
    #valve_model=models.valve(2)
    #valve_num=valve_model().data()
    #valve_num=[0,1]#valve_model()

    all_loss = 0
    right_count = 0
    train_count = 0
    shuffle = True
    avg_trainAccuracy=0

    # print model.w
    # valve_loss=model.w[0]*(1-avg_trainAccuracy)+model.w[1]*(avg_trainAccuracy)

    ''' 
    num= model.com.w1.out_channels**2
    #penalty
    print "penalty::::"
    w1_sum=torch.sum(model.com.w1.weight.data**2)/num
    print w1_sum
    w2_sum=torch.sum(model.com.w2.weight.data**2)/num
    print w2_sum
    w3_sum = torch.sum(model.com.w3.weight.data**2)/num

    print w3_sum
    def lu(x):
        if x<0:
            x=0
        return x
    ac_num=lu(accuracy-0.9)
    w_sum=(w1_sum)*(0.07-ac_num)+(w2_sum)*(0.03-ac_num)+(w3_sum)*ac_num
    
    print "W_SUM::::"
    print w_sum
    '''
    #model.acc_num(accuracy)
    if shuffle:
        train_loader.shuffle()
    #for i, objects in enumerate(train_loader):  #523
    #    if i == len(train_loader) - 1: break
    #trainAccuracy=0
    #model.acc_num(trainAccuracy)
    #print "WWWWWWWWWWWWWWWWWWWWWWWWWW"
    #print model.w1, model.w2
    #print "WWWW    LOSSSSSSSSSSSS"
    #print ((1 - avg_trainAccuracy) * (model.w1 ** 2) + (avg_trainAccuracy)) / 100
    for i in range(len(train_loader)):  # 523
        #print model.valve_line.w1[0],model.valve_line.w2[0]
        #print model.w1, model.w2
        # print "WWWW    LOSSSSSSSSSSSS"
        #print ((1 - avg_trainAccuracy) * (model.valve_line.w1[0] ) + (avg_trainAccuracy)) *(model.valve_line.w2[0])/ 100
        #print ((1 - avg_trainAccuracy) * (model.w1 ** 2) + (avg_trainAccuracy)) / 100
        inputs_torch,target_torch = train_loader[i]
        inputs = torch.autograd.Variable(inputs_torch)
        target = torch.autograd.Variable(target_torch)
        #print inputs,target
        #print model.w

        optimizer.zero_grad()
        #outputs = model(inputs,valve_num)
        outputs = model(inputs)
        #valve_loss.backward()
        loss = criterion(outputs, target)#+valve_loss#+((1 - avg_trainAccuracy) *0.1*(model.valve_line.w1[0]) + (avg_trainAccuracy)) *0.9*(model.valve_line.w2[0])/ 10
        #print loss
        all_loss += loss.data.cpu().numpy()[0]
        loss.backward()

        #print "grad:::::::"
        #print model.valve_line.valve_line.weight.grad
        optimizer.step()
        pred_results = outputs.data.cpu().numpy().argmax(1)

        target_np = target.data.cpu().numpy()
        x = (pred_results==target_np).tolist()
        rightInMINI = 0
        for each in x:
            if(each):
                rightInMINI +=1
        right_count += rightInMINI
        train_count +=  inputs_torch.size()[0]
        trainAccuracy = right_count*1.0/train_count
        if (i + 1) % 10 == 0:
            print("Epoch [%d/%d], Iter [%d/%d], Loss: %f , RightCount: [%d/%d], trainAccuracy: %f" %
                  (epoch + 1, 30, i + 1, len(train_loader), loss.data[0], rightInMINI,inputs_torch.size()[0], trainAccuracy))
            #print"Weight"
            #print model.valve_line.valve_line.weight
        # For valve
        valve_w1_grad=0
        valve_w2_grad=0
        # if trainAccuracy>0.8:
        #     valve_w1_grad = (trainAccuracy - 0.99) * 0.0001
        #     valve_w2_grad = (0.99 - trainAccuracy) * 0.0001


        # model.valve_line.valve_line.weight.data[0] = model.valve_line.valve_line.weight.data[0] + valve_w1_grad
        # model.valve_line.valve_line.weight.data[1] = model.valve_line.valve_line.weight.data[1] + valve_w2_grad

    avg_loss = all_loss/len(train_loader.imglist)
    avg_trainAccuracy = right_count*1.0/len(train_loader.imglist)
    # #For valve
    # valve_w1_grad = (avg_trainAccuracy - 0.9) * 0.1
    # valve_w2_grad = (0.9 - avg_trainAccuracy) * 0.1
    # print"Weight"
    # model.valve_line.valve_line.weight.data[0] = model.valve_line.valve_line.weight.data[0] + valve_w1_grad
    # model.valve_line.valve_line.weight.data[1] = model.valve_line.valve_line.weight.data[1] + valve_w2_grad

    print("Epoch [%d/%d] AVG_LOSS: %f , RightCount [%d/%d], trainAccuracy: %f" % (epoch + 1, 80,avg_loss,right_count,len(train_loader.imglist),avg_trainAccuracy))
    with open('train_log.txt','a') as f:
        f.write( "Epoch [%d/%d] AVG_LOSS: %f, RightCount: [%d/%d], trainAccuracy: %f" % (epoch + 1, 80,avg_loss,right_count,len(train_loader.imglist),avg_trainAccuracy) + ' '+ time.ctime() + '\n')

def validate(val_loader, model,epoch):
    model.eval()
    top1_count = 0
    top5_count = 0
    #print val_loader
    #for i, objects in enumerate(val_loader):  #523
    #    if i == len(val_loader)-1: break
    for i in range(len(val_loader)):  # 523
        inputs_torch, target_torch = val_loader[i]
        #inputs_torch,target_torch = objects
        inputs = torch.autograd.Variable(inputs_torch, volatile=True)
        target = target_torch.cpu().numpy()

        outputs = model(inputs)
        top5_index = outputs.sort(None, True)[1][:, :5].data.cpu().numpy()
        print "Top5----------------:"
        print top5_index
        #print top5_index.shape[0]
        top1_count_MINI = 0
        top5_count_MINI = 0
        for batch in range(top5_index.shape[0]):
            the_img_top5_index = top5_index[batch]  #[36, 85, 87, 59, 68],

            pre = the_img_top5_index[0]  #36
            top1_gt  = target[batch]     #36
            print "Test=============================="
            print pre,top1_gt
            if pre == top1_gt:
                top1_count += 1
                top1_count_MINI +=1
                top5_count += 1
                top5_count_MINI +=1
            else:
                if top1_gt in the_img_top5_index:
                       top5_count +=1 
                       top5_count_MINI +=1
                       
        print 'this MINIBatch top1 count:[%d/%d] ,top5 count:[%d/%d]' % (top1_count_MINI,inputs_torch.size()[0],top5_count_MINI,inputs_torch.size()[0])
    #print len(val_loader.imglist)
    top1_accuracy = top1_count*1.0/len(val_loader.imglist)
    top5_accuracy = top5_count*1.0/len(val_loader.imglist)
    print 'top1 accurary: '+ str(top1_accuracy)+'top5 accurary: '+ str(top5_accuracy)
    with open('./num_class/val_log.txt','a') as f:
        f.write( "Epoch [%d/%d] top1: %f,top5: %f" % (epoch + 1, 80, top1_accuracy,top5_accuracy)  + ' '+ time.ctime() + '\n' )
        f.close()
    return top1_accuracy

def validate_cross(val_loader, model,epoch):
    model.eval()
    Cross_class = []
    likeflag = [0] * Train_num
    #print val_loader
    #for i, objects in enumerate(val_loader):  # 523
    #    if i == len(val_loader): break
    for i in range(len(val_loader)):  # 523
        inputs_torch, target_torch = val_loader[i]
        #inputs_torch, target_torch = objects
        inputs = torch.autograd.Variable(inputs_torch, volatile=True)
        target = target_torch.cpu().numpy()

        outputs = model(inputs)
        top5_value = outputs.sort(None, True)[0][:, :5].data.cpu().numpy()
        top5_index = outputs.sort(None, True)[1][:, :5].data.cpu().numpy()
        print "Top5----------------:"
        print top5_index
        print top5_value
        # print top5_index.shape[0]
        top1_count_MINI = 0
        top5_count_MINI = 0
        for batch in range(top5_index.shape[0]):
            the_img_top5_index = top5_index[batch]  # [36, 85, 87, 59, 68],
            the_img_top5_value = top5_value[batch]

            pre = the_img_top5_index[0]  # 36
            top1_gt = target[batch]  # 36
            print "VALUE FOR CROSS"
            print the_img_top5_value[1] / the_img_top5_value[0]
            if the_img_top5_value[1] / the_img_top5_value[0] > 0.55:

                if likeflag[the_img_top5_index[1]] == 0:
                    Cross_class.append([the_img_top5_index[1], labelimg[the_img_top5_index[1]], labelimg[the_img_top5_index[0]]])
                    likeflag[the_img_top5_index[1]]=1
                if likeflag[the_img_top5_index[0]] == 0:
                    Cross_class.append([the_img_top5_index[0], labelimg[the_img_top5_index[0]], labelimg[the_img_top5_index[1]]])
                    likeflag[the_img_top5_index[0]]=1
            print "Cross=============================="
            print pre, top1_gt
    print "crossval_loader num:      "
    print len(val_loader.imglist)
    return Cross_class

def validate2(val_loader, model):
    model.eval()
    for i in range(len(val_loader)):  # 523
        inputs_torch, target_torch = val_loader[i]
        inputs = torch.autograd.Variable(inputs_torch, volatile=True)
        outputs = model(inputs)
        top5_value = outputs.sort(None, True)[0][:, :5].data.cpu().numpy()
        top5_index = outputs.sort(None, True)[1][:, :5].data.cpu().numpy()
        print top5_value
        print top5_index
    return (top5_index[0],top5_value[0])
def cloth_num(input, model):
    input=input
    input=(input//10)*10
    model.eval()
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])
    transform = transforms.Compose([
        transforms.Scale(256),
        transforms.CenterCrop(imgSize),
        transforms.ToTensor(),
        normalize, ])
    #input=cv.resize(input, (imgSize, imgSize))
    #input=input.transpose([2, 0, 1])
    input=Image.fromarray(cv.cvtColor(input,cv.COLOR_BGR2RGB))
    input=input.convert('RGB')
    input=transform(input)
    #

    #input=input/255-0.5
    #print "---------------------"
    #input_shape=input.shape
    #print input.shape
    input=input[np.newaxis,:]
    #print input.shape
    #input=input.transpose(0,3,1,2)
    #print input.shape
    #input=torch.from_numpy(input).float().cuda()
    input=input.cuda()
    inputs = torch.autograd.Variable(input, volatile=True)
    outputs = model(inputs)
    #print "00000000000000000000000000000000000"
    top5_value = outputs.sort(1,True)[0][:, :10].data.cpu().numpy()
    #print top5_value
    top5_index = outputs.sort(1,True)[1][:, :10].data.cpu().numpy()
    #print top5_index
    #print top5_value
    #print top5_index
    return (top5_index[0],top5_value[0])
    #return (top5_index, top5_value)
def read_class_cross(val_loader1,val_loader2, model1,model2,rate=0):
    model1.eval()

    inputs_torch1 = val_loader1[0][0]
    inputs1 = torch.autograd.Variable(inputs_torch1, volatile=True)
    outputs1 = model1(inputs1)

    model2.eval()
    inputs_torch2= val_loader2[0][0]
    inputs2 = torch.autograd.Variable(inputs_torch2, volatile=True)
    outputs2 = model2(inputs2)
    outputs=outputs1*rate+outputs2*(1-rate)
    top5_value = outputs.sort()[0][:, :5].data.cpu().numpy()
    top5_index = outputs.sort()[1][:, :5].data.cpu().numpy()
    print top5_value
    print top5_index
    return (top5_index[0], top5_value[0])

def CrossTrainAnno(Cross_class):
    if os.path.isfile('./num_class/crosstrainlog.txt')==0:
        os.mknod('./num_class/crosstrainlog.txt')

    if os.path.isfile('./num_class/crosstrainclass.txt')==0:
        os.mknod('./num_class/crosstrainclass.txt')

    fp_train    = open('./num_class/crosstrainlist.txt','w')
    fp_val      = open('./num_class/crossvallist.txt','w')
    fp_class    = open('./num_class/crosstrainclass.txt','a')
    path_train  = './num_class/Expand/'
    path_val    = './num_class/ClothForClassify_train/'
    for i in Cross_class:
        train_pic_list=os.listdir(os.path.join(path_train,i[1]))
        val_pic_list  =os.listdir(os.path.join(path_val,  i[1]))
        fp_class.write('%d\t%s\t\tlike_num:%s\n' % (i[0], i[1], i[2]))
        #print i
        for j,pic in enumerate(train_pic_list):
            pic_name = pic
            pic_path_train=os.path.join(path_train,i[1],pic_name)

            fp_train.write('%s\t%s\n'%(i[0],pic_path_train))

        for j,pic in enumerate(val_pic_list):
            pic_name = pic
            pic_path_val = os.path.join(path_val, i[1], pic_name)

            fp_val.write('%s\t%s\n'%(i[0],pic_path_val))
    fp_train.close()
    fp_val.close()
    fp_class.close()

def num_class(model,im_cut_name):
    # ==============================================================================
    cutclass = DogDataSet_class(
        root=CutImgPath,
        annFile=im_cut_name,
        batchsize=32,
        transform='val')
    # ==============================================================================
    return validate2(cutclass,model)
    #Classify(cutclass, model)
def num_class_cross(model1,model2,im1,im2):
    # ==============================================================================
    cutclass1 = DogDataSet_class(
        root=CutImgPath,
        annFile=im1,
        batchsize=32,
        transform='val')

    cutclass2 = DogDataSet_class(
        root=CutImgPath,
        annFile=im2,
        batchsize=32,
        transform='val')
    # ==============================================================================
    return read_class_cross(cutclass1,cutclass2,model1,model2)

def ResTrain(fileID='',lr=5e-4,restore=0,faster=False):
    model = getmodel(restore=1)
    #model.cuda()
    torch.nn.DataParallel(model).cuda()
    cudnn.benchmark = True
    rootfile = ''
    train_loader = DogDataSet(root = rootfile,
                    annFile = AnnoPath+'trainlist.txt',
                    batchsize = 32,
                    transform='train',
                    faster = faster)
#===============================================================================
    crosstrain_loader = DogDataSet(root = rootfile,
                    annFile = AnnoPath+'crosstrainlist.txt',
                    batchsize = 32,
                    transform='train',
                    faster = faster)
#==============================================================================
    val_loader = DogDataSet(root = rootfile,
                    #annFile = 'label/vallist'+str(fileID)+'.txt',
		    annFile =AnnoPath+'vallist.txt',
                    batchsize = 32,
                    transform='val',
                    faster = faster)
# ==============================================================================
    crossval_loader = DogDataSet(root=rootfile,
                            # annFile = 'label/vallist'+str(fileID)+'.txt',
                            annFile=AnnoPath + 'crossvallist.txt',
                            batchsize=32,
                            transform='val',
                            faster=faster)
#==============================================================================
    accuracy=0



    criterion = nn.CrossEntropyLoss().cuda()#+model.com.w1.weight.data
    #print criterion
    #optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    ignored_params = list(map(id, model.fc.parameters()))
    base_params = filter(lambda p: id(p) not in ignored_params,
                     model.parameters())
    #print "MDOEDEDEE"
    #print model.valve_line.parameters()
    # for name in model.state_dict():
    #     print name
    optimizer = torch.optim.SGD([
            {'params': base_params},
            {'params': model.fc.parameters(), 'lr': lr},
            ], lr=0.001, momentum=0.9)
    '''
    optimizer = torch.optim.Adam([
        {'params': base_params},
        {'params': model.fc.parameters(), 'lr': lr}
    ], lr=0.1)
    '''
    cross_flag=0

    for epoch in range(20):
        if cross_flag==0:
            train(train_loader,model, criterion, optimizer,cross_flag,accuracy,epoch)
        else:
            train(crosstrain_loader, model, criterion, optimizer, cross_flag,accuracy,epoch)
        if ((epoch + 1) % 5 == 0):
            torch.save(model.state_dict(),OutModelPath + 'resnet_cloth' + str(cross_flag) + '_' + str(epoch + 1) + ' ' + '.pth')
        #torch.save(model,OutModelPath + 'resnet_cloth' + str(cross_flag) + '_' + str(epoch + 1) + ' ' + time.ctime() + '.pth')

#==============================================================================
        if ((epoch+1) % 1 == 0):
            accuracy=validate(val_loader,model,epoch)
#==============================================================================
        #if ((epoch+1) % 5 == 0):
        '''
        if ((epoch+1) % 5 == 2):
            #adjust_learning_rate(optimizer)
            cross_flag=1
            Cross_class=validate_cross(crossval_loader, model, epoch)
           
            print "Cros_class***************************************"
            print Cross_class
            if len(Cross_class)==0:
                cross_flag=0
                print "Cross_Class is None"
            else:
                print "Cross_Class is not None"
                CrossTrainAnno(Cross_class)
                crosstrain_loader.cross_change(AnnoPath+'crosstrainlist.txt')
                crossval_loader.cross_change(AnnoPath + 'crossvallist.txt')
        else:
            cross_flag = 0
            #torch.save(model.state_dict(), OutModelPath + 'resnet_cloth' + str(cross_flag)+'_'+str(epoch + 1) + ' ' + time.ctime() + '.pth')
        '''
        if accuracy<0.80:
            adjust_learning_rate(optimizer,lr=0.001)
        elif accuracy<0.90:
            adjust_learning_rate(optimizer, lr=0.001)
        else:
            if ((epoch + 1) % 2 == 0):
                adjust_learning_rate(optimizer)

        #if ((epoch + 1) % 10 == 0):
        #    adjust_learning_rate(optimizer)
    print 'save OK!'

def ResTrain_gaa(fileID='', lr=5e-4, restore=0, faster=False):
    model = getmodel(restore)
    # model.cuda()
    torch.nn.DataParallel(model).cuda()
    cudnn.benchmark = True
    rootfile = ''
    train_loader_color = DogDataSet(root=rootfile,
                              annFile=AnnoPath + 'trainlist_color.txt',
                              batchsize=64,
                              transform='train',
                              faster=faster)
    train_loader_gray =  DogDataSet(root=rootfile,
                              annFile=AnnoPath + 'trainlist_gray.txt',
                              batchsize=64,
                              transform='train',
                              faster=faster)
    # ===============================================================================
    crosstrain_loader = DogDataSet(root=rootfile,
                                   annFile=AnnoPath + 'crosstrainlist.txt',
                                   batchsize=64,
                                   transform='train',
                                   faster=faster)
    # ==============================================================================
    val_loader_color = DogDataSet(root=rootfile,
                            # annFile = 'label/vallist'+str(fileID)+'.txt',
                            annFile=AnnoPath + 'vallist_color.txt',
                            batchsize=64,
                            transform='val',
                            faster=faster)
    val_loader_gray = DogDataSet(root=rootfile,
                            # annFile = 'label/vallist'+str(fileID)+'.txt',
                            annFile=AnnoPath + 'vallist_gray.txt',
                            batchsize=64,
                            transform='val',
                            faster=faster)
    # ==============================================================================
    crossval_loader = DogDataSet(root=rootfile,
                                 # annFile = 'label/vallist'+str(fileID)+'.txt',
                                 annFile=AnnoPath + 'crossvallist.txt',
                                 batchsize=64,
                                 transform='val',
                                 faster=faster)
    # ==============================================================================

    criterion = nn.CrossEntropyLoss().cuda()
    # optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    ignored_params = list(map(id, model.fc.parameters()))
    valve_params=list(map(id,model.valve_line.parameters()))
    base_params = filter(lambda p: (id(p) not in ignored_params) and (id(p) not in valve_params),
                         model.parameters())
    optimizer = torch.optim.Adam([

        #{'params': base_params},
        {'params': model.fc.parameters(), 'lr': lr}
    ], lr=0.0001)
    cross_flag = 0

    for epoch in range(10):
        if cross_flag == 0:
            train(train_loader_color, model, criterion, optimizer, cross_flag, epoch)
        else:
            train(crosstrain_loader, model, criterion, optimizer, cross_flag, epoch)

        torch.save(model.state_dict(),
                   OutModelPathColor + 'resnet_cloth_color' + str(cross_flag) + '_' + str(epoch + 1) + ' ' + time.ctime() + '.pth')

        # ==============================================================================
        if ((epoch + 1) % 1 == 0):
            validate(val_loader_color, model, epoch)
        # ==============================================================================
        # if ((epoch+1) % 5 == 0):
        if ((epoch + 1) % 5 == 2):
            # adjust_learning_rate(optimizer)
            cross_flag = 1
            Cross_class = validate_cross(crossval_loader, model, epoch)

            print "Cros_class***************************************"
            print Cross_class
            if len(Cross_class) == 0:
                cross_flag = 0
                print "Cross_Class is None"
            else:
                print "Cross_Class is not None"
                CrossTrainAnno(Cross_class)
                crosstrain_loader.cross_change(AnnoPath + 'crosstrainlist.txt')
                crossval_loader.cross_change(AnnoPath + 'crossvallist.txt')
        else:
            cross_flag = 0
            # torch.save(model.state_dict(), OutModelPath + 'resnet_cloth' + str(cross_flag)+'_'+str(epoch + 1) + ' ' + time.ctime() + '.pth')
        if ((epoch + 1) % 5 == 0):
            adjust_learning_rate(optimizer)
    print 'save OK!'
def adjust_learning_rate(optimizer, lr = None):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    
    for param_group in optimizer.param_groups:
        if lr == None:
            param_group['lr'] = param_group['lr']/10
        else:
            param_group['lr'] = lr

def auto_training():
    if os.path.isdir(OutModelPath):
        shutil.rmtree(OutModelPath)
    os.mkdir(OutModelPath)

    e = expand.ExpandTrainData()
    e.runExpand()
    anno_test.get_ano()
    anno_train.get_ano()
    ResTrain(restore=1)
    model=sorted(os.listdir(OutModelPath))[-1]
    if os.path.isfile(TestModel):
        os.remove(TestModel)
    shutil.copyfile(model,TestModel)
    init_res = Init.NetInit()
    GetIntelReco = GetIntelPic.IntelRec(init_res)
    GetIntelReco.pics_pair(info_path='./num_class/PairInfo/pair_d.txt', time_pair=3)
if __name__ == '__main__':
    auto_training()
    #ResTrain_gaa(restore=3)
    #mod=models.valve(2)
    #print mod()
    # e = ExpandTrainData()
    # e.runExpand()
    # anno_test.get_ano()
    # anno_train.get_ano()
    # ResTrain(restore=1)
