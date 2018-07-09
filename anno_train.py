#-*-coding: UTF-8 -*-
import os
import shutil
# path=os.path.join(os.getcwd(),'ClothForClassify_train')
path='./num_class/Expand'
trainlist_path='./num_class/trainlist.txt'
crosstrainlist_path='./num_class/crosstrainlist.txt'
trainclass_path='./num_class/trainclass.txt'

path_color='./num_class/Expand_color'
trainlist_path_color='./num_class/trainlist_color.txt'
trainclass_path_color='./num_class/trainclass_color.txt'

path_gray='./num_class/Expand_gray'
trainlist_path_gray='./num_class/trainlist_gray.txt'
trainclass_path_gray='./num_class/trainclass_gray.txt'

def get_ano():
    if os.path.isfile(trainlist_path):
        os.remove(trainlist_path)
    os.mknod(trainlist_path)

    if os.path.isfile(crosstrainlist_path):
        os.remove(crosstrainlist_path)
    os.mknod(crosstrainlist_path)

    if os.path.isfile(trainclass_path):
        os.remove(trainclass_path)
    os.mknod(trainclass_path)

    fp_train = open(trainlist_path,'w')
    fp_class = open(trainclass_path,'w')
    #print path
    doc_list=os.listdir(path)
    for n,i in enumerate(doc_list):
        pic_list=os.listdir(os.path.join(path,i))
        fp_class.write('%s\t%s\n' % (n, i))
        #print i
        for j,pic in enumerate(pic_list):
            pic_name = pic
            pic_path=os.path.join(path,i,pic_name)
            print i,pic_path,j
            fp_train.write('%s\t%s\n'%(n,pic_path))
    fp_train.close()
    fp_class.close()

def get_ano_gaa():
    #相似组 训练集
    if os.path.isfile(crosstrainlist_path):
        os.remove(crosstrainlist_path)
    os.mknod(crosstrainlist_path)
    # 颜色纹理数据集
    if os.path.isfile(trainlist_path_color):
        os.remove(trainlist_path_color)
    os.mknod(trainlist_path_color)
    #颜色纹理数据集类别
    if os.path.isfile(trainclass_path_color):
        os.remove(trainclass_path_color)
    os.mknod(trainclass_path_color)

    if os.path.isfile(trainlist_path_gray):
        os.remove(trainlist_path_gray)
    os.mknod(trainlist_path_gray)

    if os.path.isfile(trainclass_path_gray):
        os.remove(trainclass_path_gray)
    os.mknod(trainclass_path_gray)

    fp_train_color= open(trainlist_path_color,'w')
    fp_class_color= open(trainclass_path_color,'w')
    #print path
    doc_list=os.listdir(path_color)
    for n,i in enumerate(doc_list):
        pic_list=os.listdir(os.path.join(path_color,i))
        fp_class_color.write('%s\t%s\n' % (n, i))
        #print i
        for j,pic in enumerate(pic_list):
            pic_name = pic
            pic_path=os.path.join(path_color,i,pic_name)
            print i,pic_path,j
            fp_train_color.write('%s\t%s\n'%(n,pic_path))

    fp_train_gray= open(trainlist_path_gray,'w')
    fp_class_gray= open(trainclass_path_gray,'w')
    doc_list=os.listdir(path_gray)
    for n,i in enumerate(doc_list):
        pic_list=os.listdir(os.path.join(path_gray,i))
        fp_class_gray.write('%s\t%s\n' % (n, i))
        #print i
        for j,pic in enumerate(pic_list):
            pic_name = pic
            pic_path=os.path.join(path_gray,i,pic_name)
            print i,pic_path,j
            fp_train_gray.write('%s\t%s\n'%(n,pic_path))


    fp_train_color.close()
    fp_class_color.close()
    fp_train_gray.close()
    fp_class_gray.close()

if __name__ == '__main__':
   #get_ano_gaa()
   get_ano()

#if __name__ == '__main__':
    #get_ano()
