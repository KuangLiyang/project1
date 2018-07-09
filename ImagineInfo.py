# -*-coding:utf-8-*-
# encoding:utf-8
import wx
import threading
import qrcode
from Init import *
from sys import path
path.append('./interface/')
from camera import Get_picture,Get_picture2

Path_tmp_info= InfoPicPath
Path_tmp_pic=  './interface/tmp/wx_d/'
Path_tmp_per=  './interface/tmp/wx_per/'
Path_tmp_alarm='./interface/tmp/wx_alarm/'
Path_tmp_cloth=InfoPicPath
class InfoPanel(wx.Panel):
  def __init__(self, parent,net_init,intel_rec,app):
    wx.Panel.__init__(self, parent)
    print "你好"
    self.app=app
    #self.init = NetInit()
    #self.intel_rec=IntelRec()
    self.init = net_init
    self.intel_rec = intel_rec

    self.retrival_params = self.app.get_retrivalParams()
    self.cap_num = self.app.get_cam_num()
    self.cap = self.app.get_cap()
    self.pair_infos = self.app.get_pair_info()
    # cfg.caffemodel, cfg.net, cfg.CLASSES = self.init.getarg
    self.dec_num=0#跳转识别对象
    self.mode=self.app.get_mode()
    self.dirname=''
    self.auto_flag=self.app.get_auto()
    self.came_pic=cv2.imread('./interface/tmp/wx_alarm/clear.jpg')
    self.cam_flag=self.app.get_cam()
    #if self.cam_flag:
    #    self.cap = cv2.VideoCapture(self.cap_num)
    self.pair_flag = self.app.get_pair()
    self.get_flag=0
    # self.dec_num=0
    # self.dec_flag=1
    # self.show_flag=0
    # self.start_dec=0
    self.info_flag=self.app.get_info()
    #检测对象变化标志
    self.object_count_flag=[1,1,1]#跳转标志位
    self.object_change_flag = [1, 1, 1]#对象改变标志位
    self.object_change_count=[0,0,0]#跳转后连续对象计数器
    self.object_old=[-1,-1,-1]#过去对象 -1表示None
    self.object_per=[-1,-1,-1]#当前对象 -1表示None
    #多线程函数
    self.threads=[]
    # create some sizers
    mainSizer = wx.BoxSizer(wx.VERTICAL)
    hSizer = wx.BoxSizer(wx.HORIZONTAL)

    self.grid = wx.GridBagSizer(hgap=6, vgap=6)
    #======================================================
    #First  block
    # ======================================================
    self.info1 = wx.StaticText(self, label="服装检测")
    self.grid.Add(self.info1, pos=(0, 0))
    self.p1=wx.GridBagSizer(hgap=6, vgap=6)
    self.grid.Add(self.p1,pos=(0,1))
    self.p2 = wx.Panel(self, -1, size=(500,800))
    self.p1.Add(self.p2, pos=(1, 0))
    #self.p2.Bind(wx.EVT_LEFT_UP,self.Info_demo)
    # ======================================================
    #Second block
    # ======================================================
    self.info2 = wx.StaticText(self, label="检测结果")
    self.grid.Add(self.info2, pos=(0, 2))

    self.p=wx.GridBagSizer(hgap=3, vgap=3)
    self.grid.Add(self.p,pos=(0,3))
    #1
    self.pic_sec=wx.GridBagSizer(hgap=6, vgap=6)
    self.p.Add(self.pic_sec,pos=(0,0))

    self.logger1 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.pic_sec.Add(self.logger1, pos=(0, 0))

    self.pic1= wx.Panel(self, -1, size=(180,240))
    self.pic_sec.Add(self.pic1, pos=(1, 0))

    self.pic2= wx.Panel(self, -1, size=(180,240))
    self.pic_sec.Add(self.pic2, pos=(1, 1))

    self.pic3= wx.Panel(self, -1, size=(180,240))
    self.pic_sec.Add(self.pic3, pos=(1, 2))
    #2
    self.info_sec=wx.GridBagSizer(hgap=2, vgap=1)
    self.p.Add(self.info_sec, pos=(1, 0))
    self.logger2 = wx.TextCtrl(self, size=(550, 350), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.info_sec.Add(self.logger2, pos=(0, 0))
    #3 二维码
    self.p_ma = wx.GridBagSizer(hgap=3, vgap=3)
    self.p.Add(self.p_ma, pos=(2, 0))
    self.info_ma = wx.StaticText(self, label="商品二维码")
    self.p_ma.Add(self.info_ma,pos=(0,0))
    self.ma1=wx.Panel(self, -1, size=(180,180))
    self.p_ma.Add(self.ma1, pos=(1, 0))
    self.ma2 = wx.Panel(self, -1, size=(180, 180))
    self.p_ma.Add(self.ma2, pos=(1, 1))
    self.ma3 = wx.Panel(self, -1, size=(180, 180))
    self.p_ma.Add(self.ma3, pos=(1, 2))



    # ======================================================
    #Third block
    # ======================================================
    self.info3 = wx.StaticText(self, label="服装推荐")
    self.grid.Add(self.info3, pos=(0, 4))
    self.pr=wx.GridBagSizer(hgap=6, vgap=6)
    self.grid.Add(self.pr,pos=(0,5))
    #-----------------------1-----------------------------------------------------
    self.logger3 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.pr.Add(self.logger3, pos=(0, 0))
    self.pic4 = wx.Panel(self, -1, size=(180, 240))
    self.pr.Add(self.pic4, pos=(1, 0))

    self.logger4 = wx.TextCtrl(self, size=(340, 240), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.pr.Add(self.logger4, pos=(1, 1))

    #----------------------2-------------------------------------------------------
    self.logger5 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.pr.Add(self.logger5, pos=(2, 0))
    self.pic5 = wx.Panel(self, -1, size=(180, 240))
    self.pr.Add(self.pic5, pos=(3, 0))

    self.logger6 = wx.TextCtrl(self, size=(340, 240), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.pr.Add(self.logger6, pos=(3, 1))

    #---------------------3----------------------------------------------------------------------
    self.logger7 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.pr.Add(self.logger7, pos=(4, 0))
    self.pic6 = wx.Panel(self, -1, size=(180, 240))
    self.pr.Add(self.pic6, pos=(5, 0))

    self.logger8 = wx.TextCtrl(self, size=(340, 240), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.pr.Add(self.logger8, pos=(5, 1))
    #===================================Button=========================================================
    self.pb=wx.GridBagSizer(hgap=6, vgap=6)
    self.grid.Add(self.pb,pos=(2,1))
    self.button1 = wx.Button(self, label="手动检测")
    self.Bind(wx.EVT_BUTTON, self.OpenImg, self.button1)
    self.pb.Add(self.button1, pos=(0,0))
    # self.button1_info = wx.StaticText(self, label="(Open from Floder)")
    # self.grid.Add(self.button1_info, pos=(1, 0))

    self.button2 = wx.Button(self, label="捕获检测")
    self.Bind(wx.EVT_BUTTON, self.RecoImg, self.button2)
    self.pb.Add(self.button2, pos=(1,0))

    self.button3 = wx.Button(self, label="开启摄像头")
    self.Bind(wx.EVT_BUTTON, self.OpenCam, self.button3)
    self.pb.Add(self.button3, pos=(0, 1))

    self.button4 = wx.Button(self, label="自动检测")
    self.Bind(wx.EVT_BUTTON, self.AutoPic, self.button4)
    self.pb.Add(self.button4, pos=(1,1))

    self.button5 = wx.Button(self, label="在线检索")
    self.Bind(wx.EVT_BUTTON, self.Mode, self.button5)
    self.pb.Add(self.button5, pos=(0,2))

    self.button6 = wx.Button(self, label="模式转换")
    self.Bind(wx.EVT_BUTTON, self.Info, self.button6)
    self.pb.Add(self.button6, pos=(1,2))

    self.button7 = wx.Button(self, label="服装搭配")
    self.Bind(wx.EVT_BUTTON, self.Pair, self.button7)
    self.pb.Add(self.button7, pos=(0, 3))

    self.button8 = wx.Button(self, label="属性筛选")
    self.Bind(wx.EVT_BUTTON, self.ClothRetrival, self.button8)
    self.pb.Add(self.button8, pos=(1, 3))

    self.button9 = wx.Button(self, label="上一件")
    self.Bind(wx.EVT_BUTTON, self.U_pic, self.button9)
    self.pb.Add(self.button9, pos=(0, 4))

    self.button10 = wx.Button(self, label="下一件")
    self.Bind(wx.EVT_BUTTON, self.D_pic, self.button10)
    self.pb.Add(self.button10, pos=(1, 4))

    self.font1 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
    self.font2 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
    if self.cam_flag:
      self.button3.SetFont(self.font1)
      print "font1"
    else:
      self.button3.SetFont(self.font2)
      print "font2"

    if self.auto_flag:
      self.button4.SetFont(self.font1)
      print "font1"
    else:
      self.button4.SetFont(self.font2)
      print "font2"

    if self.mode:
      self.button5.SetFont(self.font1)
      print "font1"
    else:
      self.button5.SetFont(self.font2)
      print "font2"
    if self.pair_flag:
        self.button7.SetFont(self.font1)
        print "font1"
    else:
        self.button7.SetFont(self.font2)
        print "font2"
    self.Bind(wx.EVT_IDLE, self.AutoGet)
    #self.Bind(wx.EVT_IDLE, self.AutoDec)

    hSizer.Add(self.grid, 0, wx.ALL, 5)
    # hSizer.Add(self.logger)
    mainSizer.Add(hSizer, 0, wx.ALL, 5)
    # mainSizer.Add(self.button, 0, wx.LEFT)
    self.SetSizerAndFit(mainSizer)
    img = wx.Image(Path_tmp_alarm + 'start1.jpg', wx.BITMAP_TYPE_ANY).Scale(500, 800)
    self.sb = wx.StaticBitmap(self.p2, -1, wx.Bitmap(img), size=(500, 800))

    #sb = wx.Bitmap
    #初始化界面
    for i in range(1, 7):
      img = wx.Image(Path_tmp_alarm + 'clear' + str((i) % 7 + 1) + '.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
      wx.StaticBitmap(eval('self.pic'+str(i)), -1, wx.Bitmap(img), size=(180, 240))
    for i in range(1, 4):
      img = wx.Image(Path_tmp_alarm + 'clear' + str((i) % 7 + 1) + '.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
      wx.StaticBitmap(eval('self.ma' + str(i)), -1, wx.Bitmap(img), size=(180, 240))
    self.logger1.AppendText('None')
    info="欢迎使用Cloth Smart实体店智能导购员\n"
    self.logger2.AppendText(info)
    self.logger3.AppendText('None')
    self.logger5.AppendText('None')
    self.logger7.AppendText('None')
    # for i in range(1,19):
    #     img = wx.Image(Path_tmp_alarm + 'clear'+str((i)%7+1)+'.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    #     sb = wx.StaticBitmap(eval('self.pic'+str(i)), -1, wx.Bitmap(img), size=(180, 240))
    #
    #     if i<=12:
    #         eval('self.logger' + str(i)).Clear()
    #         eval('self.logger' + str(i)).AppendText("%s" % 'None')
  def clear_pic(self):
    for i in range(1, 7):
      img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
      wx.StaticBitmap(eval('self.pic' + str(i)), -1, wx.Bitmap(img), size=(180, 240))
    for i in range(1, 4):
      img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
      wx.StaticBitmap(eval('self.ma' + str(i)), -1, wx.Bitmap(img), size=(180, 240))
    for i in range(1,9):
      eval('self.logger' + str(i)).Clear()
      eval('self.logger' + str(i)).AppendText("%s" % 'None')

  def cap_release(self):
      self.cap.release()
  def show(self):
    #self.init.run_demo()
    # ================================Initial========================================================
    #time.sleep(0.1)
    # if self.auto_flag:
    #   self.init.test_ontime(path_in=Path_tmp_pic, path_out=Path_tmp_pic,dec_flag=self.dec_flag)
    # else:
    #   self.init.test(path_in=Path_tmp_pic,path_out=Path_tmp_pic)
    #self.init.test(path_in=Path_tmp_pic, path_out=Path_tmp_pic)

    self.clear_pic()
    #================================Read dec Info========================================================
    f_info    = open(Path_tmp_info, 'r')
    f_dir     = open(Path_tmp_cloth, 'r')
    f_like    = open(InfoPicLikePath, 'r')
    f_rec     = open(InfoPicPathRec, 'r')
    f_like_rec = open(InfoPicLikePathRec, 'r')
    lines = f_info.readlines()
    lines_dir   = f_dir.readlines()
    lines_like = f_like.readlines()
    lines_rec=f_rec.readlines()
    lines_like_rec=f_like_rec.readlines()

    # ======================First Block show=============================================================
    self.img = wx.Image(Path_tmp_pic + 'tmp.jpg', wx.BITMAP_TYPE_ANY).Scale(500, 800)
    self.sb1=wx.StaticBitmap(self.p2, -1, wx.Bitmap(self.img), size=(500, 800))
    #======================Second Block show=============================================================
    pair_list_all= []
    f_num=[]
    l_num=0
    for n1,i in enumerate(lines_dir):
      l_num=n1
      f_num.append(i[:-1])
      if self.pair_infos.has_key(i[:-1]):
        pair_list_all.append(self.pair_infos[i[:-1]])
      else:
        pair_list_all.append(None)
        print "Not Found i[:-1]'s Pairs"
    for i in lines_like:
      f_num.append(i[:-1])
      if self.pair_infos.has_key(i[:-1]):
        pair_list_all.append(self.pair_infos[i[:-1]])
      else:
        pair_list_all.append(None)
        print "Not Found i[:-1]'s Pairs"

    if l_num<=self.dec_num:
      like_flag=0
    else:
      like_flag=1
    print "f_num_len"

    self.f_num_len=len(f_num)
    print self.f_num_len
    if self.dec_num>=self.f_num_len:
      self.dec_num=0
    elif self.dec_num<0:
      self.dec_num=self.f_num_len-1
    if f_num!=[]:
      path_num = os.path.join("./num_class/ClothForClassify_train", f_num[self.dec_num])
      print path_num
      pic_path = os.listdir(path_num)
      self.logger1.Clear()
      if like_flag==0:
        self.logger1.AppendText(f_num[self.dec_num])
      else:
        self.logger1.AppendText('类似_'+f_num[self.dec_num])
      self.logger2.Clear()
      info_path_sec=os.path.join("./num_class/ClothInfo", f_num[self.dec_num] + '.txt')
      if os.path.isfile(info_path_sec):
        info_fp = open(info_path_sec, 'r')
        for info in info_fp:
          try:
            info = info.decode('utf-8')
          except:
            try:
              info = info.decode('gb18030')
            except:
              pass
          try:
            info = info.encode('utf-8')
          except:
            pass
          info = info.split('\t')
          if 'version' in info[0]:
            self.logger2.AppendText("%s:\t" % info[0])
          else:
            self.logger2.AppendText("%s:\t\t" % info[0])

          if ('other' in info[0]):
            self.logger2.AppendText('\n')
          if 'pos' in info[0] and len(info[1]) > 20:
            self.logger2.AppendText("显示位置\n")
          else:
            for i1 in info[1:]:
              try:
                self.logger2.AppendText("%s" % i1)
              except:
                pass
        info_fp.close()
      else:
        print "Not Found Cloth's Informations"
      for m, j in enumerate(pic_path):
        if m >= 3:
          break
        img = wx.Image(os.path.join(path_num, j), wx.BITMAP_TYPE_ANY).Scale(180, 240)
        wx.StaticBitmap(eval('self.pic' + str(m+1)), -1, wx.Bitmap(img), size=(180, 240))
      #显示信息

    #self.object_change_flag[count]=0
    # count+=1
    # num=count
    # for i in range(num,3):
    #   if pic_lines >= 3:
    #     break
    #   self.object_per[count] = -1
    #   if self.object_old[count] != self.object_per[count]:  # 跳转点
    #     self.object_count_flag[count] = 1  # 跳转标志位
    #     self.object_change_count[count] += 1  # 跳转后跳转计数器计数
    #   else:
    #     if self.object_change_count <= 5 and self.object_count_flag:
    #       self.object_change_count[count] += 1  # 跳转后跳转计数器计数
    #     else:
    #       self.object_change_flag[count] = 1  # 跳转后对象计数超过5次，对象变化标志位置位
    #       self.object_change_count[count] = 0  # 重启跳转计数器
    #       self.object_count_flag[count] = 0  # 重启跳转标志位
    #   if self.object_change_flag[count]:
    #     eval('self.logger' + str(pic_lines + 1)).Clear()
    #     for m in range(3):
    #       pic_num += 1
    #       img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    #       #wx.Bitmap
    #       wx.StaticBitmap(eval('self.pic' + str(pic_num)), -1, wx.Bitmap(img), size=(180, 240))
    # ======================Third Block show=============================================================
    if self.mode==0:
      # pic_num = 0
      pic_lines=0
      if self.pair_flag:
        rec_list=pair_list_all
      else:
        rec_list=lines_rec
      for i in rec_list:
        if i==None:
          pic_lines+=1
          continue
        rec_nums=i[:-1].split('\t')
        if self.dec_num == pic_lines:
            for n1,rec_num in enumerate(rec_nums[:-1]):
                if n1>=3:
                  break
                #显示图片
                path_rec=os.path.join("./num_class/ClothForClassify_train", rec_num)
                pic_rec =os.listdir(path_rec)
                #print pic_rec
                eval('self.logger' + str(n1*2+3)).Clear()
                eval('self.logger' + str(n1*2+3)).AppendText("%s" % rec_num)
                #显示服装信息
                # eval('self.logger' + str(n1*2+4)).Clear()
                # eval('self.logger' + str(n1*2+4)).AppendText("%s" % rec_num)
                img = wx.Image(os.path.join(path_rec, pic_rec[0]), wx.BITMAP_TYPE_ANY).Scale(180, 240)
                wx.StaticBitmap(eval('self.pic' + str(n1+4)), -1, wx.Bitmap(img), size=(180, 240))
                #显示详细信息
                info_path=os.path.join("./num_class/ClothInfo", rec_num+'.txt')
                if os.path.isfile(info_path):
                  try:
                    info_fp = open(info_path, 'r')
                  except:
                    print "Not Found Cloth's Informations"
                    continue
                  infos = info_fp.readlines()
                  eval('self.logger' + str(n1 * 2 + 4)).Clear()
                  for info in infos:

                    try:
                      info = info.decode('utf-8')
                    except:
                      try:
                        info = info.decode('gb18030')
                      except:
                        pass
                    try:
                      info = info.encode('utf-8')
                    except:
                      pass

                    info=info.split('\t')


                    if 'version' in info[0]:
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s:\t" % info[0])
                    else:
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s:\t\t" % info[0])
                    if ('other' in info[0]):
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText('\n')
                    if 'pos' in info[0] and len(info[1]) > 20:
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText("显示位置\n")
                    else:
                      for i1 in info[1:]:
                        print i1
                        try:
                          eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s" % str(i1))
                        except:
                          pass
                  info_fp.close()
        pic_lines += 1
      for i in lines_like_rec:
        if i==None:
          pic_lines+=1
          continue
        rec_nums=i[:-1].split('\t')
        if self.dec_num == pic_lines:
            for n1,rec_num in enumerate(rec_nums[:-1]):
                if n1>=3:
                  break
                path_rec=os.path.join("./num_class/ClothForClassify_train", rec_num)
                pic_rec =os.listdir(path_rec)
                #print pic_rec
                eval('self.logger' + str(n1*2+3)).Clear()
                eval('self.logger' + str(n1*2+3)).AppendText("%s" % rec_num)
                #显示服装信息
                # eval('self.logger' + str(n1*2+4)).Clear()
                # eval('self.logger' + str(n1*2+4)).AppendText("%s" % rec_num)
                img = wx.Image(os.path.join(path_rec, pic_rec[0]), wx.BITMAP_TYPE_ANY).Scale(180, 240)
                wx.StaticBitmap(eval('self.pic' + str(n1+4)), -1, wx.Bitmap(img), size=(180, 240))
                # 显示详细信息
                info_path = os.path.join("./num_class/ClothInfo", rec_num + '.txt')
                if os.path.isfile(info_path):
                  info_fp = open(info_path, 'r')
                  #infos = info_fp.readlines()
                  #print infos
                  eval('self.logger' + str(n1 * 2 + 4)).Clear()
                  for info in info_fp:
                    #info = info.split('\t')
                    try:
                      info = info.decode('utf-8')
                    except:
                      info = info.decode('gb18030')
                      pass
                    info=info.split('\t')
                    if 'version' in info[0]:
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s:\t" % info[0])
                    else:
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s:\t\t" % info[0])
                    if ('other' in info[0]):
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText('\n')

                    if 'pos' in info[0] and len(info[1]) > 20:
                      eval('self.logger' + str(n1 * 2 + 4)).AppendText("显示位置\n")
                    else:
                      for i1 in info[1:]:
                        eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s" % i1)
                    #eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s" % info[0]+ ':')
                    #eval('self.logger' + str(n1 * 2 + 4)).AppendText(info[1])
                  info_fp.close()
        pic_lines += 1
    f_info .close()
    f_dir  .close()
    f_like .close()
    f_rec  .close()
    f_like_rec.close()

  def show_intel(self):
      intel_path='./interface/intel/wx_d/'
      info_p ='./interface/intel/wx_info/'
      intel_files=sorted((fname for fname in os.listdir(intel_path) if os.path.splitext(fname)[-1] == '.jpg'))
      #print intel_files
      name_line_old=-1
      file_line=0


      for n1,i in enumerate(intel_files):
        file_name = os.path.splitext(i)[0]
        file_name_p = file_name.split('-', 1)[1]
        file_att = file_name_p.split('_')
        print "name+line ==================================="
        name_line = ''
        for name_word in file_att[:-1]:
          name_line += name_word
        print name_line

        if name_line != name_line_old and name_line_old != -1:
          file_line += 1
        name_line_old = name_line
        file_row = int(file_att[-1])


        if file_line==self.dec_num:
            #file_row=int(file_att[2])
            print "-----------------------------------"
            print file_line
            print file_row

            file_path=os.path.join(intel_path,i)
            info_path=os.path.join(info_p,file_name+'.txt')
            f_infos=open(info_path,'r')
            infos=f_infos.readlines()
            rec_name='None'
            eval('self.logger' + str(file_row * 2 + 4)).Clear()

            for info in infos:
              try:
                info = info.decode('utf-8')
              except:
                info = info.decode('gb18030')
                pass
              try:
                info = info.encode('utf-8')
              except:
                pass
              info = info.split('\t')
              if 'version' in info[0]:
                eval('self.logger' + str(file_row * 2 + 4)).AppendText("%s:\t" % info[0])
              else:
                eval('self.logger' + str(file_row * 2 + 4)).AppendText("%s:\t\t" % info[0])

              if ('other' in info[0]):
                eval('self.logger' + str(file_row * 2 + 4)).AppendText('\n')

              elif 'name' in info[0]:
                rec_name=info[1][:-1]
              elif 'pos' in info[0]:
                eval('self.logger' + str(file_row * 2 + 4)).AppendText("\n")
                #生成二维码
                html_item='https'+info[1].split('https')[1][:-1]
                print html_item
                qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10,
                                   border=10, )
                qr.add_data(html_item)
                qr.make(fit=True)
                img=qr.make_image()
                img.save('./interface/ma/ma.jpg')
                img = wx.Image('./interface/ma/ma.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 180)
                wx.StaticBitmap(eval('self.ma' + str(file_row + 1)), -1, wx.Bitmap(img), size=(180, 180))
              for i1 in info[1:]:
                eval('self.logger' + str(file_row * 2 + 4)).AppendText("%s" % i1)
              f_infos.close()
              # eval('self.logger' + str(n1 * 2 + 4)).AppendText("%s" % info[0]+ ':')
              # eval('self.logger' + str(n1 * 2 + 4)).AppendText(info[1])


              # eval('self.logger' + str(file_row * 2 + 4)).AppendText("%s" % info)
              # if 'name' in info:
                #rec_name=info.split('\t')[-1][:-1].encode("utf-8")
                #print type(rec_name)
            #infos.close()
            eval('self.logger' + str(file_row * 2 + 3)).Clear()
            eval('self.logger' + str(file_row * 2 + 3)).AppendText("%s" % rec_name)
            try:
              img = wx.Image(file_path, wx.BITMAP_TYPE_ANY).Scale(180, 240)
              wx.StaticBitmap(eval('self.pic' + str(file_row + 4)), -1, wx.Bitmap(img), size=(180, 240))
            except:
              print "error"


        # eval('self.logger' + str(file_line * 3 + file_row + 4)).Clear()
        # eval('self.logger' + str(file_line * 3 + file_row + 4)).AppendText("%s"%rec_name)
        # img = wx.Image(file_path, wx.BITMAP_TYPE_ANY).Scale(180, 240)
        # wx.StaticBitmap(eval('self.pic' + str(file_line*3+file_row + 10)), -1, wx.Bitmap(img), size=(180, 240))
        # if pic_num%3:
        #   pic_num=pic_num-pic_num%3+3
        #   pic_lines += 1


  #========================Object================================================
  # def AutoGet(self,e):
  #   #print "run222222222222222222222222222222222"
  #   if self.auto_flag==1:
  #     pic = Get_picture2("tmp.jpg", Path_tmp_per, self.cap)
  #     self.init.test_ontime(path_in=Path_tmp_per, path_out=Path_tmp_pic, dec_flag=0)
  #     self.show()
  #     if self.mode==1:
  #       #if self.show_flag==1:
  #       self.show_intel()
  #       self.show_flag=0
  #
  #
  #
  #
  #
  # def GetPic(self,e):
  #   Get_picture("tmp.jpg", "./interface/tmp/wx_d/")
  #   img = wx.Image('./interface/tmp/wx_d/tmp.jpg', wx.BITMAP_TYPE_ANY).Scale(500, 800)
  #   wx.StaticBitmap(self.p2, -1, wx.Bitmap(img), size=(500, 800))
  #
  #
  # def TreadDec(self,path_in, path_out, dec_flag):
  #   while(self.auto_flag):
  #     if dec_flag:
  #       self.init.test_ontime(path_in=path_in, path_out=path_out, dec_flag=dec_flag)
  #     # if self.mode:
  #     #   self.intel_rec.pics_reco()
  #     #   self.show_flag = 1
  #
  # def AutoPic(self,e):
  #   #self.auto_flag=not self.auto_flag
  #   auto_flag=self.app.get_auto()
  #   auto_flag=not auto_flag
  #   self.app.set_auto(auto_flag)
  #   self.auto_flag=auto_flag
  #   if self.auto_flag:
  #     self.cap = cv2.VideoCapture("http://192.168.123.60:8080/video")
  #     # self.cap=cv2.VideoCapture("http://192.168.123.60:8080/video")
  #     # self.cap = cv2.VideoCapture("http://192.168.123.60:8080/audio.wav")
  #     # self.t1=threading.Thread(target=self.TreadShow,args=(Path_tmp_per, Path_tmp_pic, 0,), name="show")
  #     # self.t1.start()
  #     self.t2 = threading.Thread(target=self.TreadDec, args=(Path_tmp_per, Path_tmp_pic, 1,), name="dec")
  #     self.t2.start()
  #   else:
  #     self.cap.release()
  #
  #   #self.init.test_ontime(path_in=path_in, path_out=path_out, dec_flag=1)
  # ==========================================Object================================================
  def ClothRetrival(self, e):
    self.app.retrival_frame()
    print self.retrival_params
  # ---------------------------------服装匹配-------------------------------------
  def Pair(self,e):
    pair_flag=self.app.get_pair()
    pair_flag=not pair_flag
    self.pair_flag=pair_flag
    self.app.set_pair(pair_flag)
    if self.pair_flag:
      self.show()
      if self.mode:
        self.show_intel()
    if self.pair_flag:
        self.button7.SetFont(self.font1)
        print "font1"
    else:
        self.button7.SetFont(self.font2)
        print "font2"

  def U_pic(self,e):
    self.dec_num+=1
    print "OOOOK"
    print self.dec_num

    self.show()
    if self.mode == 1:
      if self.pair_flag:
        self.intel_rec.pics_pair_online()
      else:
        self.intel_rec.pics_reco()
      self.show_intel()

  def D_pic(self, e):
    self.dec_num -= 1
    print "OOOOK"
    print self.dec_num
    self.show()
    if self.mode == 1:
      if self.pair_flag:
        self.intel_rec.pics_pair_online()
      else:
        self.intel_rec.pics_reco()
      self.show_intel()


      # --------------------------自动显示 播放视频-------------------------------------

  def AutoGet(self, e):
      # print "Run======================================"
      if self.cam_flag == 1:
          try:
              self.came_pic = self.app.get_came_pic()
              self.retrival_params = self.app.get_retrivalParams()
              self.init.test_ontime(path_in=Path_tmp_per, path_out=Path_tmp_pic, dec_flag=0, cv_im=self.came_pic,
                                    da_flag=(self.auto_flag) or (self.get_flag),retrival_params=self.retrival_params)
          except:
              pass
          self.show()
          if self.mode == 1:
              self.show_intel()
              self.show_flag = 0

      # def GetPic(self,e):
      #   Get_picture("tmp.jpg", "./interface/tmp/wx_d/")
      #   img = wx.Image('./interface/tmp/wx_d/tmp.jpg', wx.BITMAP_TYPE_ANY).Scale(500, 800)
      #   wx.StaticBitmap(self.p2, -1, wx.Bitmap(img), size=(500, 800))

      # ----------------------------多线程任务-------------------------------
      # 服装货号自动识别与检测
      # 摄像头图片捕获
      # ----------------------------自动识别服装标志----------------------------------

  def AutoPic(self, e):
      # self.auto_flag=not self.auto_flag
      self.app.set_start()
      auto_flag = self.app.get_auto()
      auto_flag = not auto_flag
      self.app.set_auto(auto_flag)
      self.auto_flag = auto_flag
      if self.auto_flag:
          self.button4.SetFont(self.font1)
          print "font1"
      else:
          self.button4.SetFont(self.font2)
          print "font2"

      # self.init.test_ontime(path_in=path_in, path_out=path_out, dec_flag=1)

      # ---------------------------------手动检测------------------------------------------

  def OpenImg(self, e):
      """ Open a file"""
      self.app.set_start()
      dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*")
      if dlg.ShowModal() == wx.ID_OK:
          self.filename = dlg.GetFilename()
          self.dirname = dlg.GetDirectory()
          path = os.path.join(self.dirname, self.filename)
          temp_dir = Path_tmp_per + "tmp.jpg"
          # os.system('sudo rm -rf /home/flyvideo_2106/david/wx_d *')
          # os.system('cp path /home/flyvideo_2106/david/wx_d'
          f = open(path, 'r')

          f_temp = open(temp_dir, 'w')
          f_temp.write(f.read())
          self.ShowPic(path)
          f.close()
          f_temp.close()
          # self.app.set_start()
      dlg.Destroy()
      self.retrival_params = self.app.get_retrivalParams()
      self.init.test(path_in=Path_tmp_per, path_out=Path_tmp_pic,retrival_params=self.retrival_params)
      self.show()
      if self.mode == 1:
          if self.pair_flag:
              self.intel_rec.pics_pair_online()
          else:
              self.intel_rec.pics_reco()
          self.show_intel()

      # --------------------------------捕获检测------------------------------------------

  def RecoImg(self, e):
      self.app.set_start()
      self.get_flag = 1
      if self.auto_flag == 0:
          self.app.reco_img()
          self.came_pic = self.app.reco_img()
          self.retrival_params = self.app.get_retrivalParams()
          self.init.test_ontime(path_in=Path_tmp_per, path_out=Path_tmp_pic, dec_flag=1, cv_im=self.came_pic,retrival_params=self.retrival_params)
          self.init.test_ontime(path_in=Path_tmp_per, path_out=Path_tmp_pic, dec_flag=0, cv_im=self.came_pic,retrival_params=self.retrival_params)
          self.show()
          if self.mode == 1:
              if self.pair_flag:
                  self.intel_rec.pics_pair_online()
              else:
                  self.intel_rec.pics_reco()
              self.show_intel()
      # elif self.auto_flag==0:
      #   self.init.test_ontime(path_in=Path_tmp_per, path_out=Path_tmp_pic, dec_flag=1, cv_im=self.came_pic)
      # --------------------------------打开摄像头------------------------------------------

  def OpenCam(self, e):
      self.app.set_start()
      cam_flag = self.app.get_cam()
      cam_flag = not cam_flag
      self.app.set_cam(cam_flag)
      self.cam_flag = cam_flag
      if self.cam_flag:
          self.button3.SetFont(self.font1)
          self.app.set_cap(1)
          # self.cap=self.app.get_cap()
          self.app.auto_show()
      else:
          self.button3.SetFont(self.font2)
          self.app.set_cap(0)

  def Mode(self, e):
    self.show_flag=0
    mode=self.app.get_mode()
    mode=(mode+1)%2
    self.app.set_mode(mode)
    self.mode=mode
    if self.mode:
      self.button5.SetFont(self.font1)
      print "font1"
    else:
      self.button5.SetFont(self.font2)
      print "font2"

  def Info(self, e):
    #self.info_flag=not self.info_flag
    info_flag=self.app.get_info()
    info_flag=not info_flag
    self.app.set_info(info_flag)
    self.info_flag=info_flag
    #if self.info_flag:
    self.app.change_frame(self.info_flag)
    print "hello========================"

  def Info_demo(self, e):
    print "hello========================"
    #self.change.change_frame(11)
    # self.info = wx.StaticText(self, label="对象")
    # self.grid.Replace(self.info2,self.info)
    # self.grid.Add(self.info, pos=(0, 2))
    # win=wx.MDIChildFrame(self,-1,"Child Window")
    # win.Show(True)

  #
  def ShowPic(self, path):
    img = wx.Image(path, wx.BITMAP_TYPE_ANY).Scale(500, 800)
    sb = wx.StaticBitmap(self.p2, -1, wx.Bitmap(img), size=(500, 800))
    # self.grid.Add(sb, pos=(0, 2))

  def clear_flag(self):
      self.auto_flag = 0

      if self.cam_flag:
          self.cap.release()
          self.cam_flag = 0

class Frame_Info(wx.MDIParentFrame):
  def __init__(self,net_init,intel_rec,change):
    wx.MDIParentFrame.__init__(self, None, -1, "Cloth Smart", size=(2000,1000),style=wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE)
    self.panel = InfoPanel(self,net_init,intel_rec,change)
  def cap_release(self):
      self.panel.clear_flag()