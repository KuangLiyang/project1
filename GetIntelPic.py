#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from bs4 import BeautifulSoup
import requests
import urllib2
import os
import shutil
import json
import re
from Init import *
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#头 网页浏览器
class IntelRec(object):
    def __init__(self,init_res=None):
        self.headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',}
        self.source='https://www.jd.com/'
        self.url='https://search.jd.com/image?op=upload'
        self.res=init_res
    #网络爬虫 爬取数据集
    def intel_craw(self,keyword,num,path='./craw_data/'):
        "https://search.jd.com/Search?keyword=   &enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=   &page=3&s=56&click=0"
        url_s=1
        page=0
        link_num=0
        get_flag=1
        if not os.path.isdir(path):
            os.mkdir(path)
        dcap=dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"]=('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0')
        obj=webdriver.PhantomJS(desired_capabilities=dcap)
        obj.set_page_load_timeout(10)

        while(get_flag):
            craw_url='https://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%s&page=%d'%(keyword,keyword,page*2+1)
            craw_url=craw_url.decode('utf-8')
            print craw_url
            #r=urllib2.Request(craw_url,headers=self.headers)
            #tmp=urllib2.urlopen(r).read()
            tmp=requests.get(craw_url,headers=self.headers).text
            #print tmp
            #print tmp
            data_sku=re.findall('li class="gl-item" data-sku="(.*?)"',tmp)
            print data_sku
            for n in data_sku:
                link_url='https://item.jd.com/'+n+'.html'
                print link_url
                #get_link=requests.get(link_url,headers=self.headers).text
                try:
                    obj.get(link_url)
                except Exception:
                    pass
                get_link=obj.page_source
                #print get_link

                #print get_link
                # f=open('./test.txt','w')
                # f.write(get_link)
                # f.close()
                #print get_link
                pattern=re.compile('lazyload="(.*?.jpg)"',re.X)
                pics_sr=re.findall(pattern,get_link)
                print "pics_sr============================="
                print len(pics_sr)
                pics_dir=os.path.join(path,n)
                if not os.path.isdir(pics_dir):
                    os.mkdir(pics_dir)
                #else:
                    #continue##########################################################


                for j,pic in enumerate(pics_sr):
                    pic_link="https:"+pic
                    try:
                        pic= requests.get(pic_link)
                        pic_name = n + '_' + str(j) + '.jpg'
                        pic_path = os.path.join(pics_dir, pic_name)
                        open(pic_path, 'wb').write(pic.content)
                    except Exception:
                        pass


                att = re.findall('<div class="item">.*a href=.*clstag=.*>(.*?)</a>', get_link)
                info = re.findall(r'<li title=.*>(.*?)</li>', get_link)
                # ========================price===========================
                skuids = re.findall(r'data-sku="(.*?)"', get_link)
                # print skuids
                if skuids:
                    price_json = "https://p.3.cn/prices/mgets?skuIds=J_" + skuids[0]

                    info_prince = requests.get(price_json).text
                    info_prince = json.loads(info_prince)[0]['p']
                else:
                    info_prince = None
                # ======================Files_for_items===============================
                file_info_path = os.path.join(pics_dir,n+'.txt')
                if not os.path.isfile(file_info_path):
                    os.mknod(file_info_path)
                file_info = open(file_info_path, 'w')
                name = 'name\tNone'
                version = 'version\tNone'
                style = 'style\tNone'
                age = 'age\tNone'
                other_info = "other\t"
                pos = 'pos\t京东  ' + link_url
                prince = 'prince\tNone'
                class_info = 'class_info\tNone'
                for i in info:
                    ins = i.split("：")
                    if ins[0].encode('utf-8') == '商品名称':
                        name = 'name' + '\t' + ins[1]
                    elif ins[0].encode('utf-8') == '版型':
                        version = 'version' + '\t' + ins[1]
                    elif ins[0].encode('utf-8') == '风格':
                        style = 'style' + '\t' + ins[1]
                    elif ins[0].encode('utf-8') == '适用年龄':
                        age = 'age' + '\t' + ins[1][:-2]
                    else:
                        other_info = other_info + i + '\t'
                if len(att)<=0:
                    continue
                if att[0] == '男装':
                    sex = 'sex' + '\t' + att[0]
                else:
                    sex = 'sex' + '\t' + att[0]
                if info_prince:
                    prince = 'prince\t' + str(info_prince)
                if class_info:
                    class_info = 'prince\t' + att[1]

                file_info.write(name + '\n')
                file_info.write(sex + '\n')
                file_info.write(age + '\n')
                file_info.write(class_info + '\n')
                file_info.write(version + '\n')
                file_info.write(style + '\n')
                file_info.write(prince + '\n')
                file_info.write(pos + '\n')
                file_info.write(other_info + '\n')
                file_info.close()
                link_num+=1
                print link_num
                if link_num>=num:
                    get_flag=0
                    break


            print data_sku
            page += 1
            print url_s

    # 网络服装搭配
    def get_intel_pair_online(self, pic_name='tmp.jpg', pic_path='./result/cut/',
                       infos_path='./interface/intel/wx_info/',pics_path='./interface/intel/wx_d',intel_pic_path='./interface/pair/intel_pic',
                       cut_path='./interface/pair/cut_pic/', num=5,res_num='None', time_pair=10):
        # ------------初始化程序---------------
        # 文件操作
        # if os.path.isfile(info_path):
        #     os.remove(info_path)
        # os.mkdir(info_path)
        # -----------初始化爬虫系统------------
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0')
        obj = webdriver.PhantomJS(desired_capabilities=dcap)
        obj.set_page_load_timeout(time_pair)
        # -------------京东识图------------------
        files = {'file': (pic_name, open(os.path.join(pic_path, pic_name), 'rb'), 'image/jpeg')}  # 传送待识别的图片
        r = requests.post(self.url, headers=self.headers, files=files)
        tmp = r.text
        print tmp
        p = re.findall('"(jfs.*)"', tmp)
        if len(p) == 0:
            return 0
        p = p[0].encode('utf-8').split('/')
        self.url_search = 'https://search.jd.com/image?path=jfs'
        for i in range(1, len(p)):
            self.url_search = self.url_search + "%2F" + p[i]
        self.url_search = self.url_search + '&op=search'
        # print self.url_search
        # 得到搜索结果
        r_request = urllib2.Request(self.url_search, headers=self.headers)
        r_search = urllib2.urlopen(r_request).read()
        self.pic_link = re.findall('a target="_blank" title.* href="(.*?)"', r_search)  # 搜索到的服装链接
        # information
        rec_num = 0
        # -----------------匹配服装---------------
        find_pair_flag = 0
        find_pair_num=0
        #pair_info = open(info_path, 'a')
        #pair_info.write(res_num + '\t')
        for i in range(min(num, len(self.pic_link))):  # 得到匹配列表
            if find_pair_flag:
                break
            get_pic_link = 'https:' + self.pic_link[i]
            print get_pic_link
            # pic_search=requests.get(get_pic_link,headers=self.headers).text
            try:
                obj.get(get_pic_link)
            except:
                print "Can't open pic's link"
                # continue
            get_link = obj.page_source
            # =================attribute===================================
            att = re.findall('<div class="item">.*a href=.*clstag=.*>(.*?)</a>', get_link)
            if len(att) == 0:
                continue
            res_sex = res_num.split('_')[1]
            if '1' == res_sex:
                if att[0] != '男装':
                    continue
            else:
                if att[0] != '女装':
                    continue
            # =================show_pics===================================
            pattern = re.compile('lazyload="(.*?.jpg)"', re.X)
            pics_sr = re.findall(pattern, get_link)
            print 'pics_sr:'
            print len(pics_sr)
            # ================find show_pairs==============================

            # find_pair_num=0
            for j, pic in enumerate(pics_sr):
                if j < 3:#过滤展示图片的前3张
                    continue
                if find_pair_flag:
                    break
                pic_link = "https:" + pic
                print "pic_link%d:" % j
                print pic_link
                try:
                    pic = requests.get(pic_link)
                except:
                    continue
                pic = pic.content
                pic_pn = 'pair.jpg'
                pic_path = os.path.join(intel_pic_path, pic_pn)
                # if os.path.isfile(pic_path):
                #     os.remove(pic_path)
                open(pic_path, 'wb').write(pic)
                # img=cv2.imdecode(pic,cv2.IMREAD_COLOR)
                # test
                try:
                    cls_inds, cls_res_top5, cls_score_top5, cut_dec = self.res.cloth_test(path_in=pic_path,
                                                                                          cut_out=cut_path)
                except:
                    print "get pic error"
                    continue
                pair_cut=sorted(os.listdir(cut_path))
                flag = 0
                if 'top' in res_num:
                    flag = 1
                elif 'dress' not in res_num:
                    flag = 2
                print "=++++++++++++++++++++++++++++++++++++==="
                for ind_num, ind in enumerate(cls_inds):
                    if flag == 1:
                        if ind == 0:
                            continue
                    elif flag == 2:
                        if ind != 0:
                            continue
                    else:
                        break
                    print "=====================================================!"

                    pair_pic=pair_cut[ind_num]
                    print pair_pic
                    files = {'file': (pair_pic, open(os.path.join(cut_path, pair_pic), 'rb'), 'image/jpeg')}  # 传送待识别的图片
                    #files = {'file': (pic_name, pair_pic, 'image/jpeg')}  # 传送待识别的图片
                    r = requests.post(self.url, headers=self.headers, files=files)
                    tmp = r.text
                    print "tmp------------------------------------"
                    print tmp
                    p = re.findall('"(jfs.*)"', tmp)
                    print p
                    if len(p) == 0:
                        return 0
                    p = p[0].encode('utf-8').split('/')
                    self.url_search = 'https://search.jd.com/image?path=jfs'
                    for i in range(1, len(p)):
                        self.url_search = self.url_search + "%2F" + p[i]
                    self.url_search = self.url_search + '&op=search'
                    # print self.url_search
                    # 得到搜索结果
                    r_request = urllib2.Request(self.url_search, headers=self.headers)
                    r_search = urllib2.urlopen(r_request).read()
                    self.pic_link = re.findall('a target="_blank" title.* href="(.*?)"', r_search)  # 搜索到的服装链接
                    print "self.pic_link"
                    print self.pic_link
                    # information
                    rec_num = 0
                    # -----------------匹配服装---------------
                    #find_pair_flag = 0
                    #pair_info = open(info_path, 'a')
                    #pair_info.write(res_num + '\t')
                    for i in range(min(5, len(self.pic_link))):  # 得到匹配列表
                        print "-------------------------------"
                        if find_pair_flag:
                            break
                        get_pic_link = 'https:' + self.pic_link[i]
                        print get_pic_link
                        try:
                            pic_search = requests.get(get_pic_link).text

                        except:
                            print "Can't open pic's link"
                            continue
                        # pic_search=requests.get(get_pic_link,headers=self.headers).text
                        rec_name = os.path.splitext(pic_name)[0]
                        #     print i
                        # ================pic=====================
                        pic_sr = re.findall('<img id="spec-img" width=".*?" data-origin="(.*?)"', pic_search)
                        if pic_sr == []:
                            continue
                        pic_src = 'https:' + pic_sr[0]

                        # print pic_src
                        # #save picture
                        ir = requests.get(pic_src)
                        rec_name = os.path.splitext(pic_name)[0]
                        pic_p = ir.content
                        pic_path_join = os.path.join(pics_path, rec_name + '_' + str(find_pair_num) + '.jpg')
                        open(pic_path_join, 'w').write(pic_p)


                        # =====================information=========================
                        info = re.findall(r'<li title=.*>(.*?)</li>', pic_search)
                        # for i in info:
                        #     print i
                        # ========================price===========================
                        skuids = re.findall(r'data-sku="(.*?)"', pic_search)
                        # print skuids
                        if skuids:
                            price_json = "https://p.3.cn/prices/mgets?skuIds=J_" + skuids[0]

                            info_prince = requests.get(price_json).text
                            info_prince = json.loads(info_prince)[0]['p']
                        else:
                            info_prince = None
                        # ======================Files_for_items===============================
                        file_info_path = os.path.join(infos_path, rec_name + '_' + str(find_pair_num) + '.txt')
                        if not os.path.isfile(file_info_path):
                            os.mknod(file_info_path)
                        file_info = open(file_info_path, 'w')
                        name = 'name\tNone'
                        version = 'version\tNone'
                        style = 'style\tNone'
                        age = 'age\tNone'
                        other_info = "other\t"
                        pos = 'pos\t京东  ' + get_pic_link
                        prince = 'prince\tNone'
                        class_info = 'class_info\tNone'
                        for i in info:
                            ins = i.split("：")
                            if ins[0].encode('utf-8') == '商品名称':
                                name = 'name' + '\t' + ins[1]
                            elif ins[0].encode('utf-8') == '版型':
                                version = 'version' + '\t' + ins[1]
                            elif ins[0].encode('utf-8') == '风格':
                                style = 'style' + '\t' + ins[1]
                            elif ins[0].encode('utf-8') == '适用年龄':
                                age = 'age' + '\t' + ins[1][:-2]
                            else:
                                other_info = other_info + i + '\t'
                        if att[0] == '男装':
                            sex = 'sex' + '\t' + att[0]
                        else:
                            sex = 'sex' + '\t' + att[0]
                        if info_prince:
                            prince = 'prince\t' + str(info_prince)
                        if class_info:
                            class_info = 'prince\t' + att[1]

                        file_info.write(name + '\n')
                        file_info.write(sex + '\n')
                        file_info.write(age + '\n')
                        file_info.write(class_info + '\n')
                        file_info.write(version + '\n')
                        file_info.write(style + '\n')
                        file_info.write(prince + '\n')
                        file_info.write(pos + '\n')
                        file_info.write(other_info + '\n')
                        file_info.close()
                        rec_num+=1
                        if rec_num>=1:
                            break
                    find_pair_num += 1
                    if find_pair_num >= 3:
                        find_pair_flag = 1
        return 1
    def get_intel_pair(self, pic_name='tmp.jpg', pic_path='./interface/tmp/wx_d/',info_path='./interface/pair/pair_info/pair.txt', intel_pic_path='./interface/pair/intel_pic',cut_path='./interface/pair/cut_pic/',num=5, thre=15, res_num='None',time_pair=10):
        # ------------初始化程序---------------
        # 文件操作
        # if os.path.isfile(info_path):
        #     os.remove(info_path)
        # os.mkdir(info_path)
        # -----------初始化爬虫系统------------
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0')
        obj = webdriver.PhantomJS(desired_capabilities=dcap)
        obj.set_page_load_timeout(time_pair)
        # -------------京东识图------------------
        files = {'file': (pic_name, open(os.path.join(pic_path, pic_name), 'rb'), 'image/jpeg')}  # 传送待识别的图片
        r = requests.post(self.url, headers=self.headers, files=files)
        tmp = r.text
        print tmp
        p = re.findall('"(jfs.*)"', tmp)
        if len(p)==0:
            return 0
        p=p[0].encode('utf-8').split('/')
        self.url_search = 'https://search.jd.com/image?path=jfs'
        for i in range(1, len(p)):
            self.url_search = self.url_search + "%2F" + p[i]
        self.url_search = self.url_search + '&op=search'
        # print self.url_search
        # 得到搜索结果
        r_request = urllib2.Request(self.url_search, headers=self.headers)
        r_search = urllib2.urlopen(r_request).read()
        self.pic_link = re.findall('a target="_blank" title.* href="(.*?)"', r_search)  # 搜索到的服装链接
        # information
        rec_num = 0
        # -----------------匹配服装---------------
        find_pair_flag = 0
        pair_info = open(info_path, 'a')
        pair_info.write(res_num+'\t')
        for i in range(min(num, len(self.pic_link))):  # 得到匹配列表
            if find_pair_flag:
                break
            get_pic_link = 'https:' + self.pic_link[i]
            print get_pic_link
            # pic_search=requests.get(get_pic_link,headers=self.headers).text
            try:
                obj.get(get_pic_link)
            except:
                print "Can't open pic's link"
                #continue
            get_link = obj.page_source
            # =================attribute===================================
            att = re.findall('<div class="item">.*a href=.*clstag=.*>(.*?)</a>', get_link)
            if len(att)==0:
                continue
            res_sex=res_num.split('_')[1]
            if '1'==res_sex:
                if att[0] != '男装':
                    continue
            else:
                if att[0] != '女装':
                    continue
            # =================show_pics===================================
            pattern = re.compile('lazyload="(.*?.jpg)"', re.X)
            pics_sr = re.findall(pattern, get_link)
            print 'pics_sr:'
            print len(pics_sr)
            # ================find show_pairs==============================

            # find_pair_num=0
            for j, pic in enumerate(pics_sr):
                if j<2:
                    continue
                if find_pair_flag:
                    break
                pic_link = "https:" + pic
                print "pic_link%d:"%j
                print pic_link
                try:
                    pic = requests.get(pic_link)
                except:
                    continue
                pic=pic.content
                pic_name = 'pair.jpg'
                pic_path = os.path.join(intel_pic_path, pic_name)
                # if os.path.isfile(pic_path):
                #     os.remove(pic_path)
                open(pic_path, 'wb').write(pic)
                #img=cv2.imdecode(pic,cv2.IMREAD_COLOR)
                # test
                try:
                    cls_inds, cls_res_top5, cls_score_top5, cut_dec = self.res.cloth_test(path_in=pic_path,cut_out=cut_path)
                except:
                    print "get pic error"
                    continue
                flag = 0
                if 'top' in res_num:
                    flag = 1
                elif 'dress' not in res_num:
                    flag = 2
                print flag
                pair_obj_num=[]
                pair_obj_score=[]
                for ind_num, ind in enumerate(cls_inds):
                    if flag == 1:
                        if ind == 0:
                            continue
                    elif flag == 2:
                        if ind != 0:
                            continue
                    else:
                        break

                    cloth_class, cloth_score = self.res.get_cloth_num(cut_dec[ind_num])
                    print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhaaaaaaaaa"
                    print cloth_class,cloth_score

                    for pair_num, pair_class in enumerate(cloth_class):
                        pair_class_sex=pair_class.split('_')[1]
                        if pair_class_sex!=res_sex:
                            continue
                        if 'dress' in pair_class:
                            continue
                        if flag==1 and ('top' in pair_class):
                            continue
                        elif flag==2 and ('top' not in pair_class):
                            continue
                        if cloth_score[pair_num] > thre:
                            pair_info.write(pair_class + '\t')
                            find_pair_flag = 1
        pair_info.write('\n')
        pair_info.close()
        return 1

    def get_intel_pair_d(self, pic_name='tmp.jpg', pic_path='./interface/tmp/wx_d/',info_path='./interface/pair/pair_info/pair.txt', intel_pic_path='./interface/pair/intel_pic',cut_path='./interface/pair/cut_pic/',num=5, thre=15, res_num='None',time_pair=10):
        # ------------初始化程序---------------
        # 文件操作
        # if os.path.isfile(info_path):
        #     os.remove(info_path)
        # os.mkdir(info_path)
        # -----------初始化爬虫系统------------
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0')
        obj = webdriver.PhantomJS(desired_capabilities=dcap)
        obj.set_page_load_timeout(time_pair)
        # -------------京东识图------------------
        files = {'file': (pic_name, open(os.path.join(pic_path, pic_name), 'rb'), 'image/jpeg')}  # 传送待识别的图片
        r = requests.post(self.url, headers=self.headers, files=files)
        tmp = r.text
        print tmp
        p = re.findall('"(jfs.*)"', tmp)
        if len(p)==0:
            return 0
        p=p[0].encode('utf-8').split('/')
        self.url_search = 'https://search.jd.com/image?path=jfs'
        for i in range(1, len(p)):
            self.url_search = self.url_search + "%2F" + p[i]
        self.url_search = self.url_search + '&op=search'
        # print self.url_search
        # 得到搜索结果
        r_request = urllib2.Request(self.url_search, headers=self.headers)
        r_search = urllib2.urlopen(r_request).read()
        self.pic_link = re.findall('a target="_blank" title.* href="(.*?)"', r_search)  # 搜索到的服装链接
        # information
        rec_num = 0
        # -----------------匹配服装---------------
        find_pair_num=0
        find_pair_flag = 0
        paired_flag={}
        pair_info = open(info_path, 'a')
        pair_info.write(res_num+'\t')
        for i in range(min(num, len(self.pic_link))):  # 得到匹配列表
            if find_pair_flag:
                break
            get_pic_link = 'https:' + self.pic_link[i]
            print get_pic_link
            # pic_search=requests.get(get_pic_link,headers=self.headers).text
            try:
                obj.get(get_pic_link)
            except:
                print "Can't open pic's link"
                #continue
            try:
                get_link = obj.page_source
            except:
                continue
            # =================attribute===================================
            att = re.findall('<div class="item">.*a href=.*clstag=.*>(.*?)</a>', get_link)
            if len(att)==0:
                continue
            res_sex=res_num.split('_')[1]
            if '1'==res_sex:
                if att[0] != '男装':
                    continue
            else:
                if att[0] != '女装':
                    continue
            # =================show_pics===================================
            pattern = re.compile('lazyload="(.*?.jpg)"', re.X)
            pics_sr = re.findall(pattern, get_link)
            print 'pics_sr:'
            print len(pics_sr)
            # ================find show_pairs==============================

            # find_pair_num=0
            for j, pic in enumerate(pics_sr):
                if j<2:
                    continue
                if find_pair_flag:
                    break
                pic_link = "https:" + pic
                print "pic_link%d:"%j
                print pic_link
                try:
                    pic = requests.get(pic_link)
                except:
                    continue
                pic=pic.content
                pic_name = 'pair.jpg'
                pic_path = os.path.join(intel_pic_path, pic_name)
                # if os.path.isfile(pic_path):
                #     os.remove(pic_path)
                open(pic_path, 'wb').write(pic)
                #img=cv2.imdecode(pic,cv2.IMREAD_COLOR)
                # test
                try:
                    cls_inds, cls_res_top5, cls_score_top5, cut_dec = self.res.cloth_test(path_in=pic_path,cut_out=cut_path)
                except:
                    print "get pic error"
                    continue
                flag = 0
                if 'top' in res_num:
                    flag = 1
                elif 'dress' not in res_num:
                    flag = 2
                print flag
                for ind_num, ind in enumerate(cls_inds):
                    if flag == 1:
                        if ind == 0:
                            continue
                    elif flag == 2:
                        if ind != 0:
                            continue
                    else:
                        break

                    cloth_class, cloth_score = self.res.get_cloth_num(cut_dec[ind_num])
                    print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhaaaaaaaaa"
                    print cloth_class,cloth_score

                    #for pair_num, pair_class in enumerate(cloth_class):
                    pair_class=cloth_class[0]
                    pair_class_sex=pair_class.split('_')[1]
                    if pair_class_sex!=res_sex:
                        continue
                    if 'dress' in pair_class:
                        continue
                    if flag==1 and ('top' in pair_class):
                        continue
                    elif flag==2 and ('top' not in pair_class):
                        continue
                    if cloth_score[0] > thre:
                        if paired_flag.has_key(pair_class):
                            continue
                        else:
                            pair_info.write(pair_class + '\t')
                            paired_flag[pair_class]=1
                            find_pair_num+=1
                            if find_pair_num>3:
                                find_pair_flag = 1
        pair_info.write('\n')
        pair_info.close()
        return 1

    def pics_pair(self,pics_path='./num_class/ClothForClassify_train/',info_path='./num_class/PairInfo/pair.txt',intel_pic_path='./interface/pair/intel_pic',cut_path='./interface/pair/cut_pic/',num=10, thre=15,time_pair=2):
        # if os.path.isfile(info_path):
        #     os.remove(info_path)
        # os.mknod(info_path)
        flag_continue=0
        for pic_name in sorted(os.listdir(pics_path)):
            print pic_name
            if 'dress' in pic_name:
                continue
            #if pic_name=''
            if flag_continue==0:
                if 'top_2_0068-t' in pic_name:
                    flag_continue=1
                continue

            pic_path=os.path.join(pics_path,pic_name)
            pics_files = sorted((pic_file for pic_file in os.listdir(pic_path) if os.path.splitext(pic_file)[-1] == '.jpg'))
            #for n,pic in enumerate(pics_files):
            pic=pics_files[0]
            #self.get_intel_pair(pic_name=pic, pic_path=pic_path, info_path=info_path, intel_pic_path=intel_pic_path, cut_path=cut_path,num=num, thre=thre,res_num=pic_name,time_pair=time_pair)
            self.get_intel_pair_d(pic_name=pic, pic_path=pic_path, info_path=info_path, intel_pic_path=intel_pic_path,
                                cut_path=cut_path, num=num, thre=thre, res_num=pic_name, time_pair=time_pair)

            #self.get_intel_pair(pic, pic_path, info_path, intel_pic_path, num=num, thre=thre,res_num=self.res.get_dec_inds()[n])
    def pics_pair_online(self,pics_path='./result/cut/',
                       infos_pair_path='./interface/intel/wx_info/',pics_pair_path='./interface/intel/wx_d/',intel_pic_path='./interface/pair/intel_pic',
                       cut_path='./interface/pair/cut_pic/', num=5,time_pair=1):
        if os.path.isdir(infos_pair_path):
            shutil.rmtree(infos_pair_path)
        os.mkdir(infos_pair_path)

        if os.path.isdir(pics_pair_path):
            shutil.rmtree(pics_pair_path)
        os.mkdir(pics_pair_path)

        for n,pic_path in enumerate(sorted((pic_file for pic_file in os.listdir(pics_path) if os.path.splitext(pic_file)[-1] == '.jpg'))):
            dec_num=os.path.splitext(pic_path)[0].split('-')[1]
            print "oooooooooooooooooook"
            print dec_num
            # if n<98:
            #     continue
            self.get_intel_pair_online(pic_name=pic_path, pic_path=pics_path, infos_path=infos_pair_path, pics_path=pics_pair_path, intel_pic_path=intel_pic_path,cut_path=cut_path,
                                       num=num, res_num=dec_num,time_pair=time_pair)
    #网络服装推荐
    def get_intel_reco(self,pic_name='tmp.jpg',pic_path='./interface/tmp/wx_d/',pic_att=None,reco_path='./interface/intel/wx_d/',info_path='./interface/intel/wx_info/',num=5):

        files={'file':(pic_name,open(os.path.join(pic_path,pic_name),'rb'),'image/jpeg')}
        r=requests.post(self.url,headers=self.headers,files=files)
        tmp=r.text
        print tmp
        p=re.findall('"(jfs.*)"',tmp)[0].encode('utf-8').split('/')
        self.url_search = 'https://search.jd.com/image?path=jfs'
        for i in range(1, len(p)):
            self.url_search = self.url_search + "%2F" + p[i]
        self.url_search = self.url_search + '&op=search'
        #print self.url_search
        r_request = urllib2.Request(self.url_search, headers=self.headers)
        r_search = urllib2.urlopen(r_request).read()

        #picture
        #self.pic_src = re.findall(r'img class=.*? src="(.*?)"', r_search)
        #url
        self.pic_link=re.findall('a target="_blank" title.* href="(.*?)"',r_search)
        #print self.pic_link,min(len(self.pic_link),num)

        pic_paths=[]
        names = []
        versions = []
        styles = []
        class_infos=[]
        ages = []
        sexs = []
        other_infos = []
        poss = []
        #name
        #self.pic_title = re.findall('a target="_blank" title="(.*?)"', r_search)

        #information
        rec_num=0
        for i in range(min(num,len(self.pic_link))):
            if rec_num>=3:
                break

            #print "=========================================="
            # ir = requests.get('https:' + self.pic_src[i])
            # open(os.path.join(reco_path,'intel_reco'+str(i)+'.jpg'), 'wb').write(ir.content)
            get_pic_link='https:'+self.pic_link[i]
            print get_pic_link
            #pic_request=urllib2.Request(get_pic_link, headers=self.headers)
            #pic_search= urllib2.urlopen(pic_request).read()
            pic_search=requests.get(get_pic_link,headers=self.headers).text

            #print pic_search
            # file = open('./test.txt', 'w')
            # file.write(pic_search)
            # file.close()
            #=================attribute=========================
            att = re.findall('<div class="item">.*a href=.*clstag=.*>(.*?)</a>', pic_search)
            if len(att)==0:
                continue
            if pic_att:
                if pic_att=='1' or pic_att=='男装':
                    if att[0]!='男装':
                        continue
                elif pic_att=='0' or pic_att=='女装':
                    if att[0]!='女装':
                        continue
            # for i in att:
            #     print i
            #================pic=====================
            pic_sr=re.findall('<img id="spec-img" width=".*?" data-origin="(.*?)"', pic_search)
            if pic_sr==[]:
                continue
            pic_src='https:' + pic_sr[0]

            #print pic_src
            # #save picture
            ir=requests.get(pic_src)
            rec_name=os.path.splitext(pic_name)[0]
            pic_path_join=os.path.join(reco_path, rec_name + '_' + str(rec_num) + '.jpg')
            open(pic_path_join, 'wb').write(ir.content)
            pic_paths.append(pic_path_join)


            #=====================information=========================
            info=re.findall(r'<li title=.*>(.*?)</li>', pic_search)
            # for i in info:
            #     print i
            #========================price===========================
            skuids=re.findall(r'data-sku="(.*?)"',pic_search)
            #print skuids
            if skuids:
                price_json =  "https://p.3.cn/prices/mgets?skuIds=J_"+skuids[0]

                info_prince= requests.get(price_json).text
                info_prince=json.loads(info_prince)[0]['p']
            else:
                info_prince=None
            #======================Files_for_items===============================
            file_info_path=os.path.join(info_path,rec_name + '_' + str(rec_num) + '.txt')
            if not os.path.isfile(file_info_path):
                os.mknod(file_info_path)
            file_info=open(file_info_path,'w')
            name = 'name\tNone'
            version = 'version\tNone'
            style = 'style\tNone'
            age = 'age\tNone'
            other_info="other\t"
            pos='pos\t京东  '+get_pic_link
            prince='prince\tNone'
            class_info='class_info\tNone'
            for i in info:
                ins=i.split("：")
                if ins[0].encode('utf-8')=='商品名称':
                    name='name'+'\t'+ins[1]
                elif ins[0].encode('utf-8')=='版型':
                    version='version'+'\t'+ins[1]
                elif ins[0].encode('utf-8') == '风格':
                    style ='style'+'\t'+ins[1]
                elif ins[0].encode('utf-8')=='适用年龄':
                    age='age'+'\t'+ins[1][:-2]
                else:
                    other_info=other_info+i+'\t'
            if att[0]=='男装':
                sex='sex'+'\t'+att[0]
            else:
                sex='sex'+'\t'+att[0]
            if info_prince:
                prince='prince\t'+str(info_prince)
            if class_info:
                class_info='class\t'+att[1]

            file_info.write(name+'\n')
            file_info.write(sex + '\n')
            file_info.write(age + '\n')
            file_info.write(class_info + '\n')
            file_info.write(version + '\n')
            file_info.write(style + '\n')
            file_info.write(prince + '\n')
            file_info.write(pos + '\n')
            file_info.write(other_info + '\n')
            file_info.close()
            names.append(name)
            versions.append(version)
            styles.append(style)
            class_infos.append(class_info)
            ages.append(age)
            sexs.append(sexs)
            other_infos.append(other_info)
            poss.append(pos)
            rec_num += 1
        self.pic_paths=pic_paths
        self.names=names
        self.versions = versions
        self.styles = styles
        self.class_infos = class_infos
        self.ages = ages
        self.sexs = sexs
        self.other_infos = other_infos
        self.poss = poss
        #print self.poss
    def pics_reco(self,pics_path='./result/cut/',rec_path='./',pic_att=None,reco_path='./interface/intel/wx_d/',info_path='./interface/intel/wx_info/',num=5):
        if os.path.isdir(reco_path):
            shutil.rmtree(reco_path)
        os.mkdir(reco_path)

        if os.path.isdir(info_path):

            #print "shutillllllllllllllllllllllllllll"
            shutil.rmtree(info_path)
        os.mkdir(info_path)

        pics_files=sorted((pic_file for pic_file in os.listdir(pics_path) if os.path.splitext(pic_file)[-1] == '.jpg') )

        for i in pics_files:
            if pic_att == None:
                pic_att =os.path.splitext(i)[0].split('-',1)[1].split('_')[1]
                print pic_att
            self.get_intel_reco(i,pics_path,pic_att, reco_path, info_path,num=10)
if __name__=='__main__':
     init_res = NetInit()
     GetIntelReco=IntelRec(init_res)
     print "ok"
     #GetIntelReco.pics_pair_online()
     #GetIntelReco.pics_pair_online(thre=10)
     GetIntelReco.pics_pair(info_path='./num_class/PairInfo/pair_d.txt',time_pair=10)
     print "ok"
     #GetIntelReco.get_intel_pair(pic_name='pair.jpg',pic_path='./test/dec_cut/',info_path='./test/info/info.txt',intel_pic_path='./test/intel/',cut_path='./test/cut/',num=10,thre=15,res_num='pants_1')
     #GetIntelReco.pics_reco()
     #GetIntelReco.intel_craw('男装裤子', 100,'./jingdong/pants_man/')
     #GetIntelReco.intel_craw('男装上衣', 50, './jingdong/top_man/')
     #GetIntelReco.intel_craw('女装上衣', 50, './jingdong/top_nv/')
     #GetIntelReco.intel_craw('半身裙', 50, './jingdong/skirt/')
# file=open('./study/test.txt','w')
# for i in range(5):
#     file.write(pic_link[i]+'\t'+pic_title[i]+'\n')
#     ir=requests.get('https:'+pic_src[i])
#     print ir
#     open('./%d.jpg'%i,'wb').write(ir.content)
# file.close()