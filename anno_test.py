#-*-coding: UTF-8 -*-
import os
import shutil
path='./num_clas/ClothForClassify_test/'
path_cross='./num_class/ClothForClassify_train/'
valist_path='./num_class/vallist.txt'
crossvallist_path='./num_class/crossvallist.txt'

path_color='./num_class/ClothForClassify_test/'
valist_path_color='./num_class/vallist_color.txt'
path_gray='./num_class/ClothForClassifyGray_test/'
valist_path_gray='./num_class/vallist_gray.txt'
def get_ano():
    if os.path.isfile(valist_path):
        os.remove(valist_path)
    os.mknod(valist_path)

    if os.path.isfile(crossvallist_path):
        os.remove(crossvallist_path)
    os.mknod(crossvallist_path)

    fp_test =open(valist_path,'w')
    fp_test_cross = open(crossvallist_path, 'w')

    #print path
    doc_list=os.listdir(path)
    doc_list_cross=os.listdir(path_cross)
    for n,i in enumerate(doc_list):
        pic_list=os.listdir(os.path.join(path,i))
        #print i
        for j,pic in enumerate(pic_list):
            pic_name = pic
            pic_path=os.path.join(path,i,pic_name)

            #==================rename pictures==========
            #if os.path.isfile(pic_path_old):
               #os.rename(pic_path_old,pic_path)
            #else:
               #print "ERROR"
               #print pic_path_old
               #print pic_path
            print i,pic_path,j
            fp_test.write('%s\t%s\n'%(n,pic_path))
    for n, i in enumerate(doc_list_cross):
        pic_list_cross=os.listdir(os.path.join(path_cross,i))
        for j, pic in enumerate(pic_list_cross):
            pic_name = pic
            pic_path = os.path.join(path_cross, i, pic_name)

            # ==================rename pictures==========
            # if os.path.isfile(pic_path_old):
            # os.rename(pic_path_old,pic_path)
            # else:
            # print "ERROR"
            # print pic_path_old
            # print pic_path
            print i, pic_path, j
            fp_test_cross.write('%s\t%s\n' % (n, pic_path))
    fp_test.close()
    fp_test_cross.close()
def get_ano_gaa():
    if os.path.isfile(valist_path_color):
        os.remove(valist_path_color)
    os.mknod(valist_path_color)

    if os.path.isfile(valist_path_gray):
        os.remove(valist_path_gray)
    os.mknod(valist_path_gray)

    if os.path.isfile(crossvallist_path):
        os.remove(crossvallist_path)
    os.mknod(crossvallist_path)

    fp_test_color=open(valist_path_color,'w')
    fp_test_gray=open(valist_path_gray, 'w')
    fp_test_cross = open(crossvallist_path, 'w')

    #print path
    doc_list=os.listdir(path_color)

    for n,i in enumerate(doc_list):
        pic_list_color=os.listdir(os.path.join(path_color,i))
        #print i
        for j,pic in enumerate(pic_list_color):
            pic_name = pic
            pic_path=os.path.join(path_color,i,pic_name)

            #==================rename pictures==========
            #if os.path.isfile(pic_path_old):
               #os.rename(pic_path_old,pic_path)
            #else:
               #print "ERROR"
               #print pic_path_old
               #print pic_path
            print i,pic_path,j
            fp_test_color.write('%s\t%s\n'%(n,pic_path))

    doc_list = os.listdir(path_gray)

    for n, i in enumerate(doc_list):
        pic_list_gray = os.listdir(os.path.join(path_gray, i))
        # print i
        for j, pic in enumerate(pic_list_gray):
            pic_name = pic
            pic_path = os.path.join(path_gray, i, pic_name)

            # ==================rename pictures==========
            # if os.path.isfile(pic_path_old):
            # os.rename(pic_path_old,pic_path)
            # else:
            # print "ERROR"
            # print pic_path_old
            # print pic_path
            print i, pic_path, j
            fp_test_gray.write('%s\t%s\n' % (n, pic_path))

    doc_list_cross = os.listdir(path_cross)
    for n, i in enumerate(doc_list_cross):
        pic_list_cross=os.listdir(os.path.join(path_cross,i))
        for j, pic in enumerate(pic_list_cross):
            pic_name = pic
            pic_path = os.path.join(path_cross, i, pic_name)

            # ==================rename pictures==========
            # if os.path.isfile(pic_path_old):
            # os.rename(pic_path_old,pic_path)
            # else:
            # print "ERROR"
            # print pic_path_old
            # print pic_path
            print i, pic_path, j
            fp_test_cross.write('%s\t%s\n' % (n, pic_path))
    fp_test_color.close()
    fp_test_gray.close()
    fp_test_cross.close()
if __name__ == '__main__':
   #get_ano_gaa()
   get_ano()

#if __name__ == '__main__':
    #get_ano()
