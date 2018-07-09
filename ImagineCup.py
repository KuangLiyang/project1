# -*-coding:utf-8-*-
# encoding:utf-8
import torch
# from resnet import ResTrain
import wx
import time
import threading
import os
from Imaginepic import Frame_pic
# from multiprocessing import Pool
# import threading
# import os
from sys import path
path.append('./interface/')
from camera import Get_picture,Get_picture2
from ImagineInfo import Frame_Info
from ClothSmart import ClothSmart
from ClassRetrival import ClothRe
from GetIntelPic import *
from Init import *

path.append('./Voice/')
import Voice_Sys
import voice_test
import record_voice
# from timer import Timer
# from camera import Get_picture,Get_picture2

#摄像头ID 本地摄像头值为： 1 ，2 ，3
#       IP摄像头值为：Ip摄像头IP+/video（例如http://192.168.123.60:8080/video）
Cap_num=0
try:
    cn_fp=open('./cam_num.txt','r')
    Cap_num=cn_fp.readline()
    if 'http' not in Cap_num:
        try:
            Cap_num=int(Cap_num)
        except:
            pass
except:
    pass


Path_tmp_info= InfoPicPath
#'./interface/tmp/wx_info/tmp.txt'
Path_tmp_pic=  './interface/tmp/wx_d/'
Path_tmp_per=  './interface/tmp/wx_per/'
Path_tmp_alarm='./interface/tmp/wx_alarm/'
Path_Cloth_Pair='./num_class/PairInfo/pair.txt'
#Path_tmp_cloth='./interface/tmp/wx_info/tmp_pic.txt'
Path_tmp_cloth=InfoPicPath
def pr():
  print "demo"

class MainApp(wx.App):
  def __init__(self,init,intel_rec,re=None):
    wx.App.__init__(self, False)
    self.net_init=init
    self.intel_rec=intel_rec
    self.re=re
    self.Pair_info = {}
    pair_infos=open(Path_Cloth_Pair,'r')
    for info in pair_infos:
        info=info.split('\t',1)
        if len(info)!=0:
            #pair_num=[]
            #for i in info[1:]:
            #    pair_num.append(i)
            self.Pair_info[info[0]]=info[1]
    #=============语音模块======================#

    #print "OK"
    #标志位
    self.start=0
    self.auto_flag=0
    self.mode_flag=0
    self.info_flag=0
    self.cam_flag=0
    self.pair_flag=0
    self.cam_num=0
    self.cam = None

    self.came_pic=None
    #-------------------------商品展览-------------------------------------------------------#
    self.cloth_show_flag=0
    #--------------------------检索参数-----------------------------------------------------#
    self.retrival_flag=0
    self.prince1 = None
    self.prince2 = None

    self.age1 = None
    self.age2 = None
    self.sex_num = '自动'
    self.dress_label =  '全选'
    self.top_label =    '全选'
    self.bottom_label = '全选'
    self.version_label ='全选'
    self.style_label =  '全选'
    self.age_label =    '全选'
    #self.age_auto_flag = 1
    #----------------------------------商品展示列表-----------------------------------------#
    self.Clothlists={}
    fp_cloth=open('./num_class/ClothRetrival/ClothLists/cloth_rec.txt','r')
    for infos in fp_cloth:
        info=infos[:-1].split('\t')
        cloth_name=info[0]
        cloth_lists=info[1:-1]
        self.Clothlists[cloth_name]=cloth_lists
    print self.Clothlists
    self.ClothPages=0
    # =================================检索列表===============================
    # 年龄列表'
    self.ageLists = {}
    fp_ages = open(AgeInfoDir, 'r')
    for ages_lists in fp_ages:
        age_num, age_lists = ages_lists[:-1].split(':')
        self.ageLists[age_num.encode('utf-8')] = age_lists
    fp_ages.close()
    # 类别列表
    self.classLists = {}
    fp_classes = open(ClassInfoDir, 'r')
    for classes_lists in fp_classes:
        class_num, class_lists = classes_lists[:-1].split(':')
        # print class_num
        self.classLists[class_num.encode('utf-8')] = class_lists
    fp_classes.close()
    print self.classLists
    # 款式列表
    self.versionLists = {}
    fp_versions = open(VerInfoDir, 'r')
    for versions_lists in fp_versions:
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
    print self.princeLists
    self.frame= Frame_pic(self.net_init, self.intel_rec, self,re=self.re)
    self.frame.Show()
  #获取系统命令标志位
  def set_retrival_flag(self,flag):
      self.retrival_flag=flag
  def set_cloth_pages(self,pages):
      self.ClothPages=pages
  def set_cap(self,flag):
      if flag:
          self.cam=cv2.VideoCapture(Cap_num)
      else:
          if self.cam !=None:
                self.cam.release()
                self.cam=None
  def set_sex(self,sex):
      self.sex_num=sex
  def set_prince(self,prince1,prince2):
      self.prince1=prince1
      self.prince2=prince2
  def set_age(self,age):
      self.age_label=age
      if self.age_label == '40以上':
          self.age1 = 40
          self.age2 = None
      elif '未定义' not in self.age_label and self.age_label!='全选':
          ages = self.age_label.split('-')
          print "aaaaaaaaaaaaaaaaaaaaaaaages"
          print ages
          self.age1 = int(ages[0])
          self.age2 = int(ages[1])
      else:
          self.age1 = None
          self.age2 = None
  def set_cloth_show(self,cloth_flag):
      self.cloth_show_flag=cloth_flag
  def set_class(self,dress,top,bottom):
      self.dress_label=dress
      self.top_label=top
      self.bottom_label=bottom
  def set_attribute(self,version,style):
      self.version_label=version
      self.style_label=style

  def set_auto(self,flag):
      self.auto_flag=flag
  def set_mode(self,flag):
      self.mode_flag=flag
  def set_info(self,flag):
      self.info_flag=flag
  def set_start(self):
      self.start=1
  def set_cam(self,flag):
      self.cam_flag=flag
  def set_pair(self,flag):
      self.pair_flag=flag

  def get_retrival_flag(self):
      return self.retrival_flag
  #获取服装展示标志
  def get_cloth_pages(self):
      return self.ClothPages
  def get_cloth_show(self):
      return self.cloth_show_flag
  #获取店家服装列表
  def get_cloth_lists(self):
      return self.Clothlists
  #设置系统标志位
  def get_retrivalParams(self):
      #params---->sex，prince1,prince2,dress,top,bottom,version,style,age_value
      return (
      self.sex_num, self.prince1, self.prince2, self.dress_label, self.top_label, self.bottom_label, self.version_label,
      self.style_label, self.age_label)
  def get_sex(self):
      return self.sex_num
  def get_prince(self):
      return (self.prince1,self.prince2)
  def get_age(self):
      return self.age_label
  def get_age_num(self):
      return (self.age1,self.age2)
  def get_class(self):
      return (self.dress_label,self.top_label,self.bottom_label)
  def get_attribute(self):
      return (self.version_label,self.style_label)

  def get_cam_num(self):
      return self.cam_num
  def get_auto(self):
      return self.auto_flag
  def get_mode(self):
      return self.mode_flag
  def  get_info(self):
      return self.info_flag
  def  get_cam(self):
      return self.cam_flag
  def get_pair(self):
      return self.pair_flag
  def get_pair_info(self):
      return self.Pair_info

  def get_cap(self):
      return self.cam
  def get_came_pic(self):
      return self.came_pic
  def demo_control(self):
      self.frame.panel.show()
      #img = wx.Image('./test.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
      #wx.StaticBitmap(self.frame_pic.panel.p2, -1, wx.Bitmap(img), size=(180, 240))
  def retrival_frame(self):
      try:
          self.retrival.Destroy()
      except:
          pass
      self.retrival=ClothRe(self)
      self.retrival.Show(True)
  def change_frame(self,a):
      print "hahaha"
      print a
      try:
          self.retrival.Destroy()
      except:
          pass
      if a==2:
          #frame_info=Frame_Info(self.net_init,self.intel_rec,self)
          frame_info = Frame_Info(self.net_init, self.intel_rec, self)
          if self.start:
              frame_info.panel.show()
              if self.mode_flag==1:
                  #self.intel_rec.pics_reco()
                  print "show_intel"
                  frame_info.panel.show_intel()
          #self.frame_info.Enable()
          time.sleep(0.2)
          #self.cloth_smart.cap_release()
          self.frame.Destroy()
          #time.sleep(0.2)
          #self.frame_pic.Destroy()
          frame_info.Show(True)
          self.frame=frame_info

      elif a==0:
          frame_pic = Frame_pic(self.net_init, self.intel_rec, self)
          if self.start:
              frame_pic.panel.show()
              if self.mode_flag==1:
                  #self.intel_rec.pics_reco()
                  print "show_intel2"
                  frame_pic.panel.show_intel()
          #self.frame_pic.Enable()
          time.sleep(0.2)
          #self.cloth_smart.Destroy()
          #self.frame_info.cap_release()
          self.frame.Destroy()
          #time.sleep(0.2)
          frame_pic.Show(True)
          self.frame=frame_pic
          #self.frame_info.Show(False)
      else:
          cloth_smart = ClothSmart(self.net_init, self.intel_rec, self)

          if self.start:
              cloth_smart.panel.show(True)
              if self.mode_flag==1:
                  #self.intel_rec.pics_reco()
                  print "show_intel2"
                  cloth_smart.panel.show_intel()
          #self.frame_pic.Enable()
          time.sleep(0.2)
          #self.frame_pic.cap_release()
          self.frame.Destroy()
          #time.sleep(0.2)
          #self.frame_info.Destroy()
          cloth_smart.Show(True)
          self.frame=cloth_smart
          #self.frame_info.Show(False)

  def retrival_filter(self, cloth_num, retrival_params, sex_dec=None, age_dec=None):
      # params---->sex，prince1,prince2,dress,top,bottom,version,style,age_value
      # ------------------------------sex-------------------------------------------
      sex_cloth = str(cloth_num.split('_')[1])

      sex = None
      if '自动' in retrival_params[0].encode('utf-8'):
          sex = sex_dec
      elif '全选' in retrival_params[0].encode('utf-8'):
          sex = None
      elif '女装' in retrival_params[0].encode('utf-8'):
          sex = '2'
      elif '男装' in retrival_params[0].encode('utf-8'):
          sex = '1'
      #print "----------------ssssssssssssssssssssex----------------"
      #print cloth_num, sex_cloth, sex
      if sex != None and str(sex) not in sex_cloth:
          return 0
      # else:
      #     print "sex-------------------------ok------------------"

      # -----------------------------prince----------------------------------------------
      #print self.princeLists
      print cloth_num
      print self.princeLists[cloth_num]
      prince_cloth = float(self.princeLists[cloth_num])
      # print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
      # print prince_cloth,retrival_params[1],retrival_params[2]
      if retrival_params[1] != None and prince_cloth < float(retrival_params[1]):
          #print "oooooooooooooooooooook1"
          return 0
      if retrival_params[2] != None and prince_cloth > float(retrival_params[2]):
          #print "oooooooooooooooooooook2"
          return 0

      #print "prince-------------------------ok------------------"
      # -----------------------------------class-------------------------------------------------
      dress_flag = 1
      if 'dress' not in cloth_num:
          dress_flag = 0
      else:
          if retrival_params[3] != None and retrival_params[3] != '全选':
              if retrival_params[3] == '不选':
                  if 'dress' in cloth_num:
                      dress_flag = 0
              else:
                  dress_cloth = self.classLists[retrival_params[3].encode('utf-8')].split('\t')
                  if cloth_num not in dress_cloth:
                      dress_flag = 0

      # print "==+++++++++++++++++++++++++++++++++++"
      # print retrival_params[4],cloth_num
      top_flag = 1
      if 'top' not in cloth_num:
          top_flag = 0
      else:
          if retrival_params[4] != None and retrival_params[4] != '全选':
              if retrival_params[4] == '不选':
                  if 'top' in cloth_num:
                      top_flag = 0
              else:
                  top_cloth = self.classLists[retrival_params[4].encode('utf-8')].split('\t')
                  if cloth_num not in top_cloth:
                      top_flag = 0
      bottom_flag = 1
      if 'top' in cloth_num or 'dress' in cloth_num:
          bottom_flag = 0
      else:
          if retrival_params[5] != None and retrival_params[5] != '全选':
              if retrival_params[5] == '不选':
                  if 'dress' not in cloth_num and 'top' not in cloth_num:
                      bottom_flag = 0
              else:
                  bottom_cloth = self.classLists[retrival_params[5].encode('utf-8')].split('\t')
                  if cloth_num not in bottom_cloth:
                      bottom_flag = 0
      if dress_flag == 0 and top_flag == 0 and bottom_flag == 0:
          return 0
     # print "class-------------------------ok------------------"
      # ------------------------------------------------attribute---------------------------------------------------------------
      version_flag = 1
      if retrival_params[6] != None and '全选' not in retrival_params[6]:
          version_cloth = self.versionLists[retrival_params[6].encode('utf-8')].split('\t')
          if cloth_num not in version_cloth:
              version_flag = 0
      style_flag = 1
      if retrival_params[7] != None and '全选' not in retrival_params[7]:
          style_cloth = self.styleLists[retrival_params[7].encode('utf-8')].split('\t')
          if cloth_num not in style_cloth:
              style_flag = 0
      if version_flag == 0 or style_flag == 0:
          return 0
      #print "attribute-------------------------ok------------------"
      # age
      if retrival_params[8] != None and retrival_params[8] != '全选':

          if retrival_params[8] == '自动':
              if age_dec < 30:
                  age_cloth = self.ageLists['18-30'].split('\t')
              elif age_dec < 60:
                  age_cloth = self.ageLists['30-40'].split('\t')
              else:
                  age_cloth = self.ageLists['40以上'].split('\t')
              age_cloth_other = self.ageLists['其他'].split('\t')
              if cloth_num not in age_cloth and cloth_num not in age_cloth_other:
                  return 0
          else:
              age_cloth = self.ageLists[retrival_params[8].encode('utf-8')].split('\t')
              if cloth_num not in age_cloth:
                  return 0
      #print 'allllllll_____ok'
      return 1
  def TreadCam(self, name='tmp.jpg', path=Path_tmp_per, cap=None):
    while (self.cam_flag):
      self.came_pic = Get_picture2(name=name, path=path, cap=cap, flag=0)
      if self.auto_flag:
        # print "ooooooook"
        try:
          self.net_init.test_ontime(path_in=Path_tmp_per, path_out=Path_tmp_pic, dec_flag=1, cv_im=self.came_pic)
        except:
          print "error"
          continue
        if self.mode_flag == 1:
          if self.pair_flag:
            self.intel_rec.pics_pair_online()
          else:
            self.intel_rec.pics_reco()

  def auto_show(self):
      self.t1 = threading.Thread(target=self.TreadCam, args=('tmp.jpg', Path_tmp_per, self.cam), name="cam")
      self.t1.start()
  def reco_img(self):
      if self.cam==None:
        self.cam = cv2.VideoCapture(Cap_num)
        self.came_pic = Get_picture2(name='tmp.jpg', path=Path_tmp_per, cap=self.cam, flag=1)
        self.cam.release()
        self.cam=None
      else:
        self.came_pic = Get_picture2(name='tmp.jpg', path=Path_tmp_per, cap=self.cam, flag=1)
      return self.came_pic
if __name__=='__main__':
  # def ThreadVoice():
  #   voice_t = voice_test.Voice()
  #   client_t = voice_t.client()
  #   # res = voice_t.run(client_t, "auto_detect.wav")
  #   # print res['result'][0]
  #   voice = Voice_Sys.Voice_Sys(voice_t, client_t)
  #   voice.run()
  #
  #
  # t0 = threading.Thread(target=ThreadVoice, args=(), name="cam")
  # t0.start()
  # voice_t = voice_test.Voice()
  # client_t = voice_t.client()
  # # res = voice_t.run(client_t, "auto_detect.wav")
  # # print res['result'][0]
  # voice = Voice_Sys.Voice_Sys(voice_t, client_t)
  # voice.run()
  #os.popen('./VoiceDec.py')
  voice_t = voice_test.Voice()
  client_t = voice_t.client()

  init_res = NetInit()
  intel_rec = IntelRec(init_res)
  app = MainApp(init_res, intel_rec)
  re = record_voice.Record_voice(voice=voice_t, client=client_t, frame=app.frame.panel)
  def ThreadMain(app):
      app.MainLoop()
  t0 = threading.Thread(target=ThreadMain, args=(app,), name="main")
  t0.start()


  # res = voice_t.run(client_t, "auto_detect.wav")
  # print res['result'][0]
  voice = Voice_Sys.Voice_Sys(re=re)
  voice.run()