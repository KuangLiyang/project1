# -*-coding:utf-8-*-
# encoding:utf-8
import os
import ImagineCup
import torch
import cv2
import resnet
def GetClass(path_in='./num_class/ClothInfo/',path_out_info='./num_class/ClothRetrival/ClassLists/class_num.txt',path_out_cloth='./num_class/ClothRetrival/ClassLists/class_cloth.txt'):
    class_cloth = {}
    class_info = []
    files=os.listdir(path_in)
    if os.path.isfile(path_out_info)==0:
        os.mknod(path_out_info)
    fp_out_info=open(path_out_info,'w')
    if os.path.isfile(path_out_cloth) == 0:
        os.mknod(path_out_cloth)
    fp_out_cloth = open(path_out_cloth, 'w')
    for file in files:
        file_path=os.path.join(path_in,file)
        infos_fp=open(file_path,'r')
        for infos in infos_fp:
            try:
                infos= infos.decode('utf-8')
            except:
                infos = infos.decode('gb18030')
                pass
            infos=infos.encode('utf-8')
            info=infos[:-1].split('\t')
            if info[0]=='class':
                print "-----------------"
                class_si=info[1]
                print class_si
                if '衬衫' in class_si:
                    class_si='衬衫'
                elif '衫' in class_si:
                    class_si='打底衫'
                elif 'T恤' in class_si:
                    class_si='T恤'
                elif '毛衣' in class_si:
                    class_si='毛衣'
                elif '卫衣' in class_si:
                    class_si='卫衣'
                elif '裤' not in class_si and '裙' not in class_si:
                    class_si='外套'
                elif '休闲裤' in class_si:
                    class_si='休闲裤'
                cl_info=os.path.splitext(file)[0]
                if class_cloth.has_key(class_si):
                    class_cloth[class_si].append(cl_info)
                    #class_cloth[class_si]+=cl_info+'\t'
                else:
                    #print class_si
                    class_info.append(class_si)
                    class_cloth[class_si] =[]
                    class_cloth[class_si].append(cl_info)
                    #class_cloth[class_si]=cl_info+'\t'
                break
    for i in class_info:
        fp_out_info.write(str(i)+'\n')
    for i in class_cloth:
        fp_out_cloth.write(i + ':')
        for j in sorted(class_cloth[i]):
            fp_out_cloth.write(j + '\t')
        fp_out_cloth.write('\n')
        #fp_out_cloth.write(i+':'+class_cloth[i]+'\n')
    fp_out_info.close()
    fp_out_cloth.close()
def GetVersion(path_in='./num_class/ClothInfo/',path_out_info='./num_class/ClothRetrival/AttributeLists/version_num.txt',path_out_cloth='./num_class/ClothRetrival/AttributeLists/version_cloth.txt'):
    class_cloth = {}
    class_info = []
    files=os.listdir(path_in)
    if os.path.isfile(path_out_info)==0:
        os.mknod(path_out_info)
    fp_out_info=open(path_out_info,'w')
    if os.path.isfile(path_out_cloth) == 0:
        os.mknod(path_out_cloth)
    fp_out_cloth = open(path_out_cloth, 'w')
    for file in files:
        file_path=os.path.join(path_in,file)
        infos_fp=open(file_path,'r')
        for infos in infos_fp:
            try:
                infos= infos.decode('utf-8')
            except:
                try:
                    infos = infos.decode('gb18030')
                except:
                    pass
            try:
                infos=infos.encode('utf-8')
            except:
                pass
            info=infos[:-1].split('\t')
            if info[0]=='version':
                for versions in info[1].split(','):
                    for version in versions.split('，'):
                        print "-----------------"
                        class_si=version
                        print class_si
                        if 'None' in class_si or '其他' in class_si or '两件套' in class_si:
                            class_si='其他'
                        elif 'A型' in class_si:
                            class_si='A型'
                        elif '标准' in class_si:
                            class_si='标准'
                        elif '修身' in class_si:
                            class_si='修身'
                        elif '直筒' in class_si:
                            class_si='直筒'
                        elif '宽松' in class_si:
                            class_si='宽松'
                        elif 'H型' in class_si:
                            class_si='H型'
                        elif '休闲' in class_si:
                            class_si='休闲'
                        cl_info=os.path.splitext(file)[0]
                        if class_cloth.has_key(class_si):
                            class_cloth[class_si].append(cl_info)
                            #class_cloth[class_si]+=cl_info+'\t'
                        else:
                            #print class_si
                            class_info.append(class_si)
                            class_cloth[class_si] =[]
                            class_cloth[class_si].append(cl_info)
                            #class_cloth[class_si]=cl_info+'\t'
                        break
    for i in class_info:
        fp_out_info.write(str(i)+'\n')
    for i in class_cloth:
        fp_out_cloth.write(i + ':')
        for j in sorted(class_cloth[i]):
            fp_out_cloth.write(j + '\t')
        fp_out_cloth.write('\n')
        #fp_out_cloth.write(i+':'+class_cloth[i]+'\n')
    fp_out_info.close()
    fp_out_cloth.close()
def GetStyle(path_in='./num_class/ClothInfo/',path_out_info='./num_class/ClothRetrival/AttributeLists/style_num.txt',path_out_cloth='./num_class/ClothRetrival/AttributeLists/style_cloth.txt'):
    class_cloth = {}
    class_info = []
    files=os.listdir(path_in)
    if os.path.isfile(path_out_info)==0:
        os.mknod(path_out_info)
    fp_out_info=open(path_out_info,'w')
    if os.path.isfile(path_out_cloth) == 0:
        os.mknod(path_out_cloth)
    fp_out_cloth = open(path_out_cloth, 'w')
    for file in files:
        file_path=os.path.join(path_in,file)
        infos_fp=open(file_path,'r')
        for infos in infos_fp:
            try:
                infos= infos.decode('utf-8')
            except:
                try:
                    infos = infos.decode('gb18030')
                except:
                    pass
            try:
                infos=infos.encode('utf-8')
            except:
                pass
            info=infos[:-1].split('\t')
            if info[0]=='style':
                for versions in info[1].split(','):
                    for version in versions.split('，'):
                        print "-----------------"
                        class_si=version
                        print class_si
                        if 'None' in class_si or '其他' in class_si or '大众' in class_si or'森女'in class_si or '其它' in class_si:
                            class_si='其他'
                        elif '休闲' in class_si or '运动' in class_si:
                            class_si='休闲'
                        elif '通勤' in class_si:
                            class_si='通勤'
                        elif '韩' in class_si or '日' in class_si:
                            class_si='日韩'
                        elif '名媛淑女' in class_si or '优雅' in class_si:
                            class_si='优雅淑女'
                        elif '欧美' in class_si:
                            class_si='欧美'
                        elif '民族' in class_si or '维多利亚'in class_si or '波普'in class_si or '波西米亚'in class_si or '英伦'in class_si:
                            class_si='民族'
                        elif '正装' in class_si:
                            class_si='正装'
                        elif '文艺' in class_si or '清新' in class_si:
                            class_si='清新文艺'
                        elif '街拍' in class_si or '流行' in class_si:
                            class_si='流行街拍'
                        elif '甜美' in class_si:
                            class_si='甜美'
                        elif '百搭' in class_si or '嘻哈' in class_si:
                            class_si='百搭'
                        elif '复古' in class_si or '简约' in class_si:
                            class_si='简约复古'
                        cl_info=os.path.splitext(file)[0]
                        if class_cloth.has_key(class_si):
                            class_cloth[class_si].append(cl_info)
                            #class_cloth[class_si]+=cl_info+'\t'
                        else:
                            #print class_si
                            class_info.append(class_si)
                            class_cloth[class_si] =[]
                            class_cloth[class_si].append(cl_info)
                            #class_cloth[class_si]=cl_info+'\t'
                        break
    for i in class_info:
        fp_out_info.write(str(i)+'\n')
    for i in class_cloth:
        fp_out_cloth.write(i + ':')
        for j in sorted(class_cloth[i]):
            fp_out_cloth.write(j + '\t')
        fp_out_cloth.write('\n')
        #fp_out_cloth.write(i+':'+class_cloth[i]+'\n')
    fp_out_info.close()
    fp_out_cloth.close()

def GetAge(path_in='./num_class/ClothInfo/',path_out_info='./num_class/ClothRetrival/AgeLists/age_num.txt',path_out_cloth='./num_class/ClothRetrival/AgeLists/age_cloth.txt'):
    class_cloth = {}
    class_info = []
    files=os.listdir(path_in)
    if os.path.isfile(path_out_info)==0:
        os.mknod(path_out_info)
    fp_out_info=open(path_out_info,'w')
    if os.path.isfile(path_out_cloth) == 0:
        os.mknod(path_out_cloth)
    fp_out_cloth = open(path_out_cloth, 'w')
    for file in files:
        file_path=os.path.join(path_in,file)
        infos_fp=open(file_path,'r')
        for infos in infos_fp:
            try:
                infos= infos.decode('utf-8')
            except:
                infos = infos.decode('gb18030')
                pass
            infos=infos.encode('utf-8')
            info=infos[:-1].split('\t')
            if info[0]=='age':
                print "-----------------"
                class_si=info[1]
                print class_si
                if 'None' in class_si or class_si==None or class_si=='其他':
                    class_si='未定义'
                elif '18-24' in class_si or '18-29' in class_si or '20-30' in class_si or '20-34'in class_si or '25-29' in class_si:
                    class_si='18-30'
                elif '30-34' in class_si or '35-39' in class_si:
                    class_si = '30-40'
                else:
                    class_si = '40以上'
                cl_info=os.path.splitext(file)[0]
                if class_cloth.has_key(class_si):
                    class_cloth[class_si].append(cl_info)
                    #class_cloth[class_si]+=cl_info+'\t'
                else:
                    #print class_si
                    class_info.append(class_si)
                    class_cloth[class_si] =[]
                    class_cloth[class_si].append(cl_info)
                    #class_cloth[class_si]=cl_info+'\t'
                break
    for i in sorted(class_info):
        fp_out_info.write(str(i)+'\n')
    for i in sorted(class_cloth):
        fp_out_cloth.write(i + ':')
        for j in sorted(class_cloth[i]):
            fp_out_cloth.write(j + '\t')
        fp_out_cloth.write('\n')
        #fp_out_cloth.write(i+':'+class_cloth[i]+'\n')
    fp_out_info.close()
    fp_out_cloth.close()
def GetPrince(path_in='./num_class/ClothInfo/',path_out_info='./num_class/ClothRetrival/PrincesLists/cloth_prince.txt'):
    class_cloth = {}
    files=os.listdir(path_in)
    if os.path.isfile(path_out_info)==0:
        os.mknod(path_out_info)
    fp_out_info=open(path_out_info,'w')

    for file in files:
        file_path=os.path.join(path_in,file)
        infos_fp=open(file_path,'r')
        for infos in infos_fp:
            try:
                infos= infos.decode('utf-8')
            except:
                infos = infos.decode('gb18030')
                pass
            infos=infos.encode('utf-8')
            info=infos[:-1].split('\t')
            if info[0]=='prince':
                info[1]=info[1].split()[0]
                try:
                    prince=float(info[1])
                except:
                    prince=None
                cl_info=os.path.splitext(file)[0]
                class_cloth[cl_info]=prince
                break
    class_cloth=sorted(class_cloth.items(), key=lambda d: d[1], reverse=True)
    print class_cloth
    for i in class_cloth:
        fp_out_info.write(str(i[0])+'\t'+str(i[1])+'\n')

    fp_out_info.close()
def get_flag(cloth):
    if 'dress' in cloth:
        flag=1
    elif 'top' in cloth:
        flag=2
    elif 'pants' in cloth:
        flag=3
    elif 'skirt' in cloth:
        flag=4
    else:
        flag=0
    sex=cloth.split('_')[1]
    return (flag,sex)
def GetClothReco(path_in='./num_class/ClothForClassify_train/',path_out_info='./num_class/ClothRetrival/ClothLists/cloth_rec.txt',res_model=None):
    class_cloth = {}
    cloth_lists=os.listdir(path_in)
    with open('./num_class/trainclass.txt', 'r') as file:
        num_classes = []
        for eachline in file:
            numclass = eachline.split('\t')[-1][:-1]
            num_classes.append(numclass)
    num_classes = num_classes
    if os.path.isfile(path_out_info)==0:
        os.mknod(path_out_info)
    fp_info=open(path_out_info,'w')
    for cloth_num in sorted(cloth_lists):
        print cloth_num
        cloth_flag=get_flag(cloth_num)
        cloth_path=os.path.join(path_in,cloth_num)
        pics_lists=os.listdir(cloth_path)
        cloth_score_lists={}
        for num,pic in enumerate(pics_lists):
           if num>=3:
               break
           #pic_name=os.path.splitext(pic)[0]
           pic_path=os.path.join(cloth_path,pic)
           pic_cv=cv2.imread(pic_path)
           #pic_cv=cv2.resize(())
           dec_index,dec_score= resnet.cloth_num(pic_cv,res_model)
           for n,i in enumerate(dec_index):
               dec_flag=get_flag(num_classes[i])
               if cloth_flag!=dec_flag:
                   continue
               if cloth_score_lists.has_key(num_classes[i]):
                   if cloth_score_lists[num_classes[i]] < dec_score[n]:
                       cloth_score_lists[num_classes[i]]=dec_score[n]
               else:
                   cloth_score_lists[num_classes[i]]=dec_score[n]
        class_cloth[cloth_num]=sorted(cloth_score_lists.items(), key=lambda d: d[1], reverse=True)
    print class_cloth
    for cloth in sorted(class_cloth):
        fp_info.write(cloth+'\t')
        for rec in class_cloth[cloth]:
            fp_info.write(rec[0]+'\t')
        fp_info.write('\n')
    fp_info.close()


if __name__=='__main__':
    GetClass()
    GetStyle()
    #res_model=resnet.getmodel(restore=1)
    #torch.nn.DataParallel(res_model).cuda()
    #GetClothReco(res_model=res_model)
    GetVersion()
    GetAge()
    GetPrince()
