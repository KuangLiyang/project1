import os
def changeInfo(path_in='./num_class/ClothInfo',path_out='./num_class/ClothInfo_change'):
    in_lists=os.listdir(path_in)

    for file in in_lists:
        flag = 0
        file_path=os.path.join(path_in,file)
        file_path_out=os.path.join(path_out,file)
        if os.path.isfile(file_path_out)==0:
            os.mknod(file_path_out)
        fp_info=open(file_path,'r')
        fp_info_out=open(file_path_out,'w')
        for infos in fp_info:
            print infos
            info = infos[:-1].split('\t',1)
            try:
                info[1]= info[1].decode('utf-8')
            except:
                try:
                    info[1] = info[1].decode('gb18030')
                except:
                    info[1]='None'
            info[1]=info[1].encode('utf-8')
            print infos


            if flag==1:
                info[0] = 'class'
                flag=2
            if info[0]=='age':
                if flag==0:
                    print "age okkkkkkkkkkkkkkkkkkk"
                    flag=1
            # print info[0]
            # print info[1]
            fp_info_out.write(str(info[0])+'\t'+str(info[1])+'\n')
        fp_info.close()
        fp_info_out.close()

if __name__=='__main__':
    changeInfo()