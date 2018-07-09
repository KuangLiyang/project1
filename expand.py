#-*-coding: UTF-8 -*-
import os
from math import pi,sin,cos,atan,sqrt,pow
import sys
import shutil
import random
from PIL import Image,ImageFilter
from PIL import ImageEnhance as enhance
from skimage import data,exposure,img_as_float
import matplotlib.pyplot as plt
import cv2
#Affine 图像变形函数 进行图像变形
#img 图片地址
#k1 k2 变换参数
#mode 变换模式
#mode=0,1,2,3为变形模式  k1,k2分别代表x、y轴变形程度 一般设定在（-1,1)之间 超过会过都变形到其他模式
#mode==0 正向变形
#mode==1 旋转90度
#mode==2 旋转180度
#mode==3 旋转270度
#mode>3  压缩模式    k1,k2分别代表x、y轴压缩程度 k1 k2>0 为正向压缩 k1 k2<0时为对折后压缩
#dir 变形后 图像的保存地址

class ExpandTrainData(object):
    def __init__(self):
        self.expand_path = './num_class/ClothForClassify_train/'

        # ====================================================================================================
        # 数据集扩充模块
        # ====================================================================================================
        # 路径和参数设置
        # path_affine1='./Affine1/'
        #self.param_affine1 = [-0.35,-0.3, -0.25, -0.2,-0.1, 0,0.1, 0.2, 0.25, 0.3,0.35]
        self.param_affine1 = [-0.35, 0, 0.35]
        # path_affine2='./Affine2/'
        #self.param_affine2 = [0.8, 1, 1.25, -0.8, -1, -1.25]
        self.param_affine2 = [0.8, 1.25, -0.8, -1, -1.25]
        # path_rotate='./Rotate/'
        #self.param_rotate = [30,60,90,120,150,180,210,240,270,300,330]
        self.param_rotate = [ 60, 90 , 300, 330]
        # path_occ='./OCC/'
        # self.param_occ = 10
        # self.param_cut = 10
        self.param_occ = 5
        self.param_cut = 5
        # path_fuzzi='./Fuzzi/'
        #self.param_fuzzi = [0.5,1.5,2]
        self.param_fuzzi = [0.5, 1.5, 2]
        # path_twist='./Twist/'
        #self.param_twist = [(-0.001, 0.8), (-0.0005, 0.9) ,(-0.0002, 1) ,(0.0002, 1),(0.0005, 0.9), (0.0013, 0.8)]
        self.param_twist = [(-0.001, 0.8),  (0.0013, 0.8)]
        # path_Stitching='./Twist/'
        # self.param_stitch = [(1,1,1),(0.9,1,1),(0.8,1,1),(0.7,1,1),(0.6,1,1),(0.5,1,1),(1.1,1,1),(1.25,1,1),(1.42,1,1),(1.67,1,1),(1.8,1,1),
        #                     (1, 2, 1), (1, 3, 1),(1, 4, 1),(1, 5, 1),(1, 6, 1),
        #                     (1, 1, 1.1), (1, 1, 1.2), (1, 1, 1.3), (1, 1, 1.4), (1, 1, 1.5),(1, 1, 0.9), (1, 1, 0.83), (1, 1, 0.77), (1, 1, 0.71), (1, 1, 0.67),
        #                     (0.9, 3, 1.1), (0.8, 3, 1.1), (0.7, 3, 1.1), (0.6, 3, 1.1), (0.5, 3, 1.1), (1.1, 2, 1.2),(1.25, 2, 1.2), (1.42, 2, 1.2), (1.67, 2, 1.2), (1.8, 2, 1.2)
        #                     ]
        self.param_stitch = [ (0.8, 3, 1.1), (0.6, 3, 1.1), (1.25, 2, 1.2),  (1.67, 2, 1.2)]
        self.Affine1_path = './num_class/Affine1/'
        self.Affine2_path = './num_class/Affine2/'
        self.Rotate_path =  './num_class/Rotate/'
        self.OCC_path =     './num_class/OCC/'
        self.Fuzzi_path =   './num_class/Fuzzi/'
        self.Twist_path =   './num_class/Twist/'
        self.Cut_path=      './num_class/Cut/'
        self.Stitch_path = './num_class/Stitch/'
        # 对数据集进行扩充，形参为地址
    def runExpand(self):
        info = self.expand(self.expand_path)
        '''
        info = self.SingleExpand("dress_lv")
        info = self.SingleExpand("shirt_lv")
        info = self.SingleExpand("top_kuang_blue")
        info = self.SingleExpand("top_kuang_white")
        info = self.SingleExpand("top_lv_flower")
        info = self.SingleExpand("top_lv_orange")
        info = self.SingleExpand("top_lv_pink")
        info = self.SingleExpand("top_yao_coat")
        '''
        return info

    def Stitching(self,im,a,b,c,img_name=' ',dir='./'):
        img=Image.open(im)
        brightness = enhance.Brightness(img)
        image = brightness.enhance(a)  ##亮度增强
        #image.show()
        #bright_img.save(self.save_file)
        sharpness = enhance.Sharpness(image)
        image = sharpness.enhance(b)  # 锐度增强
        #sharp_img.show()
        #sharp_img.save(self.save_file)
        contrast = enhance.Contrast(image)  # 对比度增强
        image = contrast.enhance(c)
        #image.show()
        #contrast_img.save(self.save_file)

        if img_name!=None:
            if img_name==' ':
                img_twist_name='twist_'+im.split('/')[-1]
            else:
                img_twist_name=img_name
            out=os.path.join(dir,img_twist_name)
            print out
            image.save(out)

    def Affine(self,img,k1=0,k2=0,mode=0,img_name=' ',dir='./'):
        if mode==0:
            n1=1
            n4=1
            n2=k1*n1
            n3=k2*n1
        elif mode==1:
            n2=1
            n3=-1
            n1=n2*k1
            n4=n3*k2
        elif mode==2:
            n1=1
            n4=-1
            n2=k1*n1
            n3=k2*n1
        elif mode==3:
            n2=1
            n3=1
            n1=n2*k1
            n4=n3*k2
        else:
            n1=k1
            n4=k2
            n2=0
            n3=0
        try:
            im=Image.open(img)
        except IOError:
            print "Error:No File"
            return None
        else:
            print "Read File Successfully"
            im_re=im.convert('RGBA')
            base=Image.new('RGBA',im_re.size,(255,)*4)
            img_size=im_re.size
            #print img_size
            x=img_size[0]*1.0
            y=img_size[1]*1.0
            #print x,y
            '''
            #提取边缘像素
            edge=[]
            for i in range(4):
                edge.append([])
            print edge
            for i in range(y):
                pixel=(255,255,255)
                #pixel=im.getpixel((0, i))
                edge[0].append(pixel)
                #pixel=im.getpixel((x-1, i))
                edge[1].append(pixel)
            for i in range(x):
                pixel=(255,255,255)
                #pixel=im.getpixel((i, 0))
                edge[2].append(pixel)
                #pixel=im.getpixel((i, y-1))
                edge[3].append(pixel)
            print edge
            '''
            #转换变换后图像大小为设定尺寸(有且仅当可以变换大小时）
            if (n1*n4-n3*n2):
                x_ordinary = lambda xx, yy: (n4 * xx - n2 * yy) / (n1 * n4 - n3 * n2)  # 将原图的顶点坐标转换至变换图的坐标
                y_ordinary = lambda xx, yy: (n3 * xx - n1 * yy) / (n3 * n2 - n1 * n4)
                xa = []
                ya = []
                xa=[x_ordinary(0,0),x_ordinary(0,y),x_ordinary(x,0),x_ordinary(x,y)]
                ya=[y_ordinary(0,0),y_ordinary(0,y),y_ordinary(x,0),y_ordinary(x,y)]
                #print xa,ya
                len_x=abs(max(xa)-min(xa))
                len_y=abs(max(ya)-min(ya))
                len_k1=len_x/x
                len_k2=len_y/y
                if len_k1>len_k2:
                    n1 = n1 * len_k1
                    n2 = n2 * len_k1
                    n3 = n3 * len_k1
                    n4 = n4 * len_k1
                else:
                    n1 = n1 * len_k2
                    n2 = n2 * len_k2
                    n3 = n3 * len_k2
                    n4 = n4 * len_k2
                #print "============"
                #print n1,n2,n3,n4
            c1=( (1-n1)*x-n2*y)/2
            c2=(-n3*x+(1-n4)*y)/2
            #print c1,c2

            im1=im_re.transform(img_size,Image.AFFINE,(n1,n2,c1,n3,n4,c2))
            '''
            #手动填充
            for i in range(x):
                for j in range(y):
                    if (n1*i+n2*j+c1)>=x-1 or (n3*i+n4*j+c2)>=y-1 or (n1*i+n2*j+c1)<=0 or (n3*i+n4*j+c2)<=0:
                        im1.putpixel((i,j),(255,255,255))
            '''
            #im1.show()
            im_affine=Image.composite(im1,base,im1)
            #im_affine.show()
            im_affine.convert(im.mode)
            #im_affine=im_affine.filter(ImageFilter.DETAIL)
            #im_affine = im_affine.filter(ImageFilter.GaussianBlur(radius=-1))
            #im_affine.show()
            if img_name!=None:
                if img_name==' ':
                    img_name=img.split('/')[-1]
                    out=os.path.join(dir+'affine_'+img_name)
                else:
                    out = os.path.join(dir + img_name)
                    print out
                #if os.path.isdir(dir):
                im_affine.save(out)
            return im_affine

    def twist(self,imge, mode=0, k=0, l=1, img_name=' ', dir='./'):
        img = Image.open(imge)
        img_size = img.size
        '''
        if mode==0:
            img_x=img_size[0]
            if k!=0:
                img_y=int(sqrt(1+4*abs(k)*img_size[1])-1.0/(2*abs(k)))+1
            else:
                img_y=img_size[1]
    
        img_twist = Image.new('RGB', (img_x,img_y), (255, 255, 255))
        '''
        img_twist = Image.new('RGB', (img_size[0], img_size[1]), (255, 255, 255))
        img_x = 0
        img_y = 0
        l = abs(l)
        for i in range(img_size[0]):
            for j in range(img_size[1]):
                if mode == 0:
                    a = i
                    b = int(abs(k) * j * j + l * j)
                else:
                    a = int(abs(k) * i * i + l * i)
                    b = j
                #print a, b
                #print i, j

                if a >= img_size[0] or b >= img_size[1]:
                    break
                else:
                    img_x = i
                    img_y = j
                    if (k >= 0):
                        color = img.getpixel((a, b))
                        img_twist.putpixel((i, j), color)
                    else:
                        color = img.getpixel((img_size[0] - 1 - a, img_size[1] - 1 - b))
                        # img_twist.putpixel((img_x-1-i,img_y-1-j),color)
                        img_twist.putpixel((img_size[0] - 1 - i, img_size[1] - 1 - j), color)
        #print img_x, img_y
        '''
        if k>=0:
            box=(0,0,img_x,img_y)
        else:
            box=(img_size[0]-1-img_x,img_size[1]-1-img_y,img_size[0]-1,img_size[1]-1)
        img_twist=img_twist.crop(box)
        '''

        if img_name!=None:
            if img_name==' ':
                img_twist_name='twist_'+imge.split('/')[-1]
            else:
                img_twist_name=img_name
            out=os.path.join(dir,img_twist_name)
            print out
            img_twist.save(out)
        ''' 
        '''
        return img_twist
    #用于图像旋转
    def rotates(self,imge,angle,img_name=' ',dir='./'):#w为角度制（顺时针旋转）
        w=angle*pi/180
        img=Image.open(imge)#打开图片
        #img.show()
        im_re=img.convert('RGBA')
        bl = Image.new('RGBA', im_re.size, (255,) * 4)
        img_size=im_re.size#读取图片尺寸
        x=img_size[0]*1.0#图片行数
        y=img_size[1]*1.0#图片列数
        #print x,y
        diagonal_len=sqrt(pow(x,2)+pow(y,2))#图片对角线长度
        #print diagonal_len
        at=atan(y/x)
        #print at
        diagonal_w1=at-w#旋转后图片对角线相对于水平轴的夹角（初始夹角-顺时针旋转角度w）
        diagonal_w2=pi-at-w#对角线2相对于水平轴的夹角
        if diagonal_w1>pi and diagonal_w1<0:#旋转后度数不在[0,pi]范围，调整到该范围
            diagonal_w1=diagonal_w1%(pi)
        if diagonal_w2>pi and diagonal_w2<0:#旋转后度数不在[0,pi]范围，调整到该范围
            diagonal_w2=diagonal_w2%(pi)
        #各个对角线夹角的三角函数值
        a1=sin(diagonal_w1)
        a2=cos(diagonal_w1)
        b1=sin(diagonal_w2)
        b2=cos(diagonal_w2)
       # print diagonal_w1,diagonal_w2,a1,a2,b1,b2
        #以相邻上面的两个顶点进行计算（其他顶点关于原点对称，性质相同），旋转后的图片经resize应在规定尺寸内
        if diagonal_w1<=(pi-at) and diagonal_w1>=at:
            dia1=abs(y/a1)
        else:
            dia1=abs(x/a2)

        if diagonal_w2<=(pi-at) and diagonal_w2>=at:
            dia2=abs(y/b1)
        else:
            dia2=abs(x/b2)
        #print "---------------"
        #print dia1,dia2
        if dia1<dia2:
            diagonal_relen=dia1
        else:
            diagonal_relen = dia2
        k=diagonal_relen/diagonal_len
        x_re=int(x*k)
        y_re=int(y*k)
        #print x_re,y_re
        im_re=im_re.resize((x_re,y_re))
        bl.paste(im_re,(int(x-x_re)/2,int(y-y_re)/2,int(x+x_re)/2,int(y+y_re)/2))
        bl.convert('RGBA')
        #bl.show()
        base = Image.new('RGBA', bl.size, (255,) * 4)
        im1=bl.rotate(-angle)
        #im1.show()
        im_rotate = Image.composite(im1, base, im1)
        im_rotate.convert(img.mode)
        #im_rotate.show()
        if img_name!=None:
            if img_name==' ':
                img_name=imge.split('/')[-1]
                out=os.path.join(dir+'rotate_'+img_name)
            else:
                out=os.path.join(dir+img_name)
            im_rotate.save(out)
        return im_rotate

    #遮挡噪声图片
    def occlusion(self,imge,num=1,img_name=' ',dir='./'):
        img=Image.open(imge)
        img_size=img.size
        limit=int(min(img_size)/5)
        if limit==0:
            print "picture is too small"
        else:
            for i in range(num):
                rand_x = random.randint(limit/2+1, limit)
                rand_y = random.randint(limit/2+1, limit)
                or_x = random.randint(0, img_size[0]-limit)
                or_y = random.randint(0, img_size[1]-limit)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                oc=Image.new('RGB',(rand_x,rand_y),color)
                img.paste(oc, (or_x, or_y, or_x+rand_x, or_y+rand_y))
            #img.show()
            if img_name!=None:
                if img_name == ' ':
                    img_name = imge.split('/')[-1]
                    out = os.path.join(dir + 'oc_' + img_name)
                else:
                    out = os.path.join(dir + img_name)
                img.save(out)
        print limit
        return img

    def cutimge(self,imge, img_name=' ', dir='./'):
        img = Image.open(imge)
        img_size = img.size
        # limit=int(min(img_size)/4)
        limit_x = int(img_size[0] *0.8)
        limit_y = int(img_size[1] *0.8)
        #img.show()
        if limit_x == 0 or limit_y == 0:
            print "picture is too small"
        else:
            rand_x = random.randint(int(limit_x *0.88) + 1, int(limit_x))
            rand_y = random.randint(int(limit_y *0.88) + 1, int(limit_y))
            or_x = random.randint(0, img_size[0] - rand_x)
            or_y = random.randint(0, img_size[1] - rand_y)
            box = (or_x, or_y, or_x + rand_x, or_y + rand_y)
            img_cut = img.crop(box)
            #img_cut.show()
            if img_name!=None:
                if img_name == ' ':
                    img_name = imge.split('/')[-1]
                    out = os.path.join(dir + 'cut_' + img_name)
                else:
                    out = os.path.join(dir + img_name)
                img_cut.save(out)
        return img

    def Fuzzi(self,imge,k=0,img_name=' ',dir='./'):
        img=Image.open(imge)
        im_fuzzi= img.filter(ImageFilter.GaussianBlur(radius=k))
        #im_fuzzi.show()
        #print im_fuzzi.size
        if img_name != None:
            if img_name == ' ':
                img_name = imge.split('/')[-1]
                out = os.path.join(dir + 'fuz_' + img_name)
            else:
                out = os.path.join(dir + img_name)
            im_fuzzi.save(out)
        return im_fuzzi



    def img_expand(self,img,path_affine1,path_affine2,path_rotate,
                   path_occ,path_fuzzi,path_twist,path_cut,path_stitch):

        img_name=img.split('/')[-1]
        print img_name
        im=img_name.split('.')[0]
        print im
        if(os.path.isdir(path_stitch)==0):
            os.mkdir(path_stitch)
        for i,j in enumerate(self.param_stitch):
            stitch_img_name='Stitch_'+str(i)+'_'+img_name
            #aff_img_path=os.path.join(img_affine,aff_img_name)
            #print aff_img_path
            self.Stitching(img,j[0],j[1],j[2],stitch_img_name,path_stitch)

        if(os.path.isdir(path_affine1)==0):
            os.mkdir(path_affine1)
        '''
        img_affine1=os.path.join(path_affine1,im)+'/'
        print "++++++++++++++++++++++"
        print img_affine1
    
        if(os.path.isdir(img_affine1)==0):
            os.mkdir(img_affine1)
        '''
        for i,j in enumerate(self.param_affine1):
            aff1_img_name='Aff1_'+str(i)+'_'+img_name
            #aff_img_path=os.path.join(img_affine,aff_img_name)
            #print aff_img_path
            self.Affine(img,j,j,0,aff1_img_name,path_affine1)

        if(os.path.isdir(path_affine2)==0):
            os.mkdir(path_affine2)
        for i,j in enumerate(self.param_affine2):
            aff2_img_name_x='Aff2x_'+str(i)+'_'+img_name
            aff2_img_name_y='Aff2y_' + str(i) + '_' + img_name
            #aff_img_path=os.path.join(img_affine,aff_img_name)
            #print aff_img_path
            self.Affine(img,j,1,4,aff2_img_name_x,path_affine2)
            self.Affine(img, 1, j, 4, aff2_img_name_y, path_affine2)

        if(os.path.isdir(path_rotate)==0):
            os.mkdir(path_rotate)
        for i,j in enumerate(self.param_rotate):
            torate_img_name='Rotate_'+str(i)+'_'+img_name
            #aff_img_path=os.path.join(img_affine,aff_img_name)
            #print aff_img_path
            self.rotates(img,j,torate_img_name,path_rotate)

        if(os.path.isdir(path_occ)==0):
            os.mkdir(path_occ)
        for i in range(self.param_occ):
            occ_img_name='Occ_'+str(i)+'_'+img_name
            #aff_img_path=os.path.join(img_affine,aff_img_name)
            #print aff_img_path
            self.occlusion(img,5,occ_img_name,path_occ)

        if(os.path.isdir(path_cut)==0):
            os.mkdir(path_cut)
        for i in range(self.param_cut):
            cut_img_name='Cut_'+str(i)+'_'+img_name
            #aff_img_path=os.path.join(img_affine,aff_img_name)
            #print aff_img_path
            self.cutimge(img,cut_img_name,path_cut)

        if(os.path.isdir(path_fuzzi)==0):
            os.mkdir(path_fuzzi)
        for i,j in enumerate(self.param_fuzzi):
            fuzzi_img_name='Fuzzi_'+str(i)+'_'+img_name
            #aff_img_path=os.path.join(img_affine,aff_img_name)
            #print aff_img_path
            self.Fuzzi(img,j,fuzzi_img_name,path_fuzzi)

        if(os.path.isdir(path_twist)==0):
            os.mkdir(path_twist)
        for i,j in enumerate(self.param_twist):
            fuzzi_img_name_x ='TwistX_'+str(i)+'_'+img_name
            fuzzi_img_name_y ='TwistY_'+str(i)+'_'+img_name
            self.twist(img,0,j[0],j[1], fuzzi_img_name_x, path_twist)
            self.twist(img,1,j[0],j[1], fuzzi_img_name_y, path_twist)
        print "Down"


        '''
        '''
    def SingleExpand(self,name):
        path_in=os.path.join('./num_class/ClothForClassify_train/',name)
        path_out=os.path.join('./num_class/Expand/',name)+'/'
        if os.path.isdir(path_out):
            shutil.rmtree(path_out)
        os.mkdir(path_out)
        imgfiles=os.listdir(path_in)
        for i in imgfiles:
            path_img=os.path.join(path_in,i)

            self.img_expand(path_img, path_out, path_out, path_out,path_out,path_out, path_out, path_out)
        return "Data Preprocess Completed!\n"

    def expand(self,path_in):
        if os.path.isdir(path_in):
            print "GET Data Dir"
            FileList=os.listdir(path_in)
            print FileList
            for i,dir in enumerate(FileList):
                img_dir=os.path.join(path_in,dir)+'/'
                #print img_dir
                if os.path.isdir(img_dir):
                    print "Get image dir"
                    if os.path.isdir('./num_class/Expand/')==0:
                        os.mkdir('./num_class/Expand/')
                    expand_dir='./num_class/Expand/'+dir+'/'
                    print expand_dir
                    ImageList=os.listdir(img_dir)
                    #print ImageList
                    for img in ImageList:
                        imge=os.path.join(img_dir,img)
                        print imge
                        self.img_expand(imge,expand_dir,expand_dir,expand_dir,expand_dir,expand_dir,expand_dir,expand_dir,expand_dir)
        return "Data Preprocess Completed!\n"

if __name__ == '__main__':
    e = ExpandTrainData()
    #e.Stitching('1.jpg',1,1,2)
    e.runExpand()
    #im1 = Image.open('./imge/Sheer_Pleated-Front_Blouseimg_00000001.jpg')
    #im2 = Image.open('./imge/Sheer_Pleated-Front_Blouseimg_00000002.jpg')
    #print im1.size[0]
    #print im2.size
    #box = (100, 100, 200, 200)
    #region = im1.crop(box)
    #im=im1.rotate(45)
    #im.show()
    # region.show()
    #box = (50, 50, 150, 150)
    #im2.paste(region, box)
    #im = im1.transform((300, 300), Image.AFFINE, (3, 1, -300 / 2, 0.5, 1.5, -150 / 2))
    #im.show()
    # f_Train_config = open('/home/flyvideo_2016/kuang/num_classify/Train_config.txt')
    # content = f_Train_config.readlines()
    # expand_path = '/home/flyvideo_2016/kuang/num_classify/test/'
    # #对数据集进行扩充，形参为地址
    # expand(expand_path)


    #print im.getpixel((0, 0))
    #im.show()
    #k=1
    #Affine('./te.jpg',k,1,4)
    #expand('./te.jpg')

    #twist('./imge/Sheer_Pleated-Front_Blouseimg_00000002.jpg',0,0,0,300,300,0,200,200)
    #Fuzzi('./te.jpg',k)
    #rotates('./imge/Sheer_Pleated-Front_Blouseimg_00000002.jpg', 400)
    #occlusion('./imge/Sheer_Pleated-Front_Blouseimg_00000002.jpg',20)
