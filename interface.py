#encoding:utf-8
from resnet import ResTrain
import wx
import threading
import os
import time

from Init import NetInit
from sys import path
path.append('./interface/')
from timer import Timer
#import torch
from camera import Get_picture

# from demo_d import Run_Demo

Path_tmp_info= './interface/tmp/wx_info/tmp.txt'
Path_tmp_pic=  './interface/tmp/wx_d/'
Path_tmp_alarm='./interface/tmp/wx_alarm/'
Path_tmp_cloth='./interface/tmp/wx_info/tmp_pic.txt'
class ExamplePanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)
    print "你好"
    self.init = NetInit()
    # cfg.caffemodel, cfg.net, cfg.CLASSES = self.init.getarg
    self.dirname=''
    self.auto_flag=0
    # create some sizers
    mainSizer = wx.BoxSizer(wx.VERTICAL)
    self.grid = wx.GridBagSizer(hgap=6, vgap=6)
    # fgs = wx.FlexGridSizer(cols=10, rows=10, hgap=50, vgap=10)
    hSizer = wx.BoxSizer(wx.HORIZONTAL)
    #block[0][1] display the clothes' detected informations
    self.p=wx.GridBagSizer(hgap=6, vgap=6)
    self.grid.Add(self.p,pos=(0,3))

    self.p2 = wx.Panel(self, -1, size=(600,800))
    self.grid.Add(self.p2, pos=(0, 1))

    #self.p3 = wx.Panel(self, -1, size=(180,240))
    #self.p.Add(self.p3, pos=(0, 0))

    self.logger3 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.p.Add(self.logger3, pos=(0, 0))
    self.pic1= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic1, pos=(1, 0))

    self.pic2= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic2, pos=(1, 1))

    self.pic3= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic3, pos=(1, 2))


    self.logger4 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.p.Add(self.logger4, pos=(2, 0))
    self.pic4= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic4, pos=(3, 0))

    self.pic5= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic5, pos=(3, 1))

    self.pic6= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic6, pos=(3, 2))


    self.logger5 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.p.Add(self.logger5, pos=(4, 0))
    self.pic7= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic7, pos=(5, 0))

    self.pic8= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic8, pos=(5, 1))

    self.pic9= wx.Panel(self, -1, size=(180,240))
    self.p.Add(self.pic9, pos=(5, 2))


    #block[0][3]


    #self.info1 = wx.StaticText(self, label="衣物检测： ")
    self.info1 = wx.StaticText(self, label="Cloth")
    self.grid.Add(self.info1, pos=(0, 0))
    self.info2 = wx.StaticText(self, label="object")
    self.grid.Add(self.info2, pos=(0, 2))
    # self.logger = wx.TextCtrl(self, size=(300, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)
    #img = wx.Image('3030.jpg', wx.BITMAP_TYPE_ANY).Scale(300, 400)
    #sb = wx.StaticBitmap(self, -1, wx.NullBitmap, size=(300, 400))
    # self.grid.Add(self.logger, pos=(0, 1))
    # self.grid.Add(sb, pos=(0, 1))

    self.info3 = wx.StaticText(self, label="Info: ")
    self.grid.Add(self.info3, pos=(0, 4))

    #
    self.logger2 = wx.TextCtrl(self, size=(400, 800), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.grid.Add(self.logger2, pos=(0, 5))


    #Open Button
    self.button1 = wx.Button(self, label="Open")
    self.Bind(wx.EVT_BUTTON, self.OpenImg, self.button1)
    self.grid.Add(self.button1, pos=(1,1))
    # self.button1_info = wx.StaticText(self, label="(Open from Floder)")
    # self.grid.Add(self.button1_info, pos=(1, 0))
    self.button2 = wx.Button(self, label="Detect")
    self.Bind(wx.EVT_BUTTON, self.RecoImg, self.button2)
    self.grid.Add(self.button2, pos=(1,3))

    self.button3 = wx.Button(self, label="Take")
    self.Bind(wx.EVT_BUTTON, self.TakePic, self.button3)
    self.grid.Add(self.button3, pos=(2,1))

    self.button4 = wx.Button(self, label="Add")
    self.Bind(wx.EVT_BUTTON, self.NewAdd, self.button4)
    self.grid.Add(self.button4, pos=(2,3))

    self.button5 = wx.Button(self, label="Photo")
    self.Bind(wx.EVT_BUTTON, self.GetPic, self.button5)
    self.grid.Add(self.button5, pos=(3,1))

    self.button6 = wx.Button(self, label="Auto")
    self.Bind(wx.EVT_BUTTON, self.AutoPic, self.button6)
    self.grid.Add(self.button6, pos=(2,2))

    self.Bind(wx.EVT_IDLE, self.AutoGet)

    hSizer.Add(self.grid, 0, wx.ALL, 5)
    # hSizer.Add(self.logger)
    mainSizer.Add(hSizer, 0, wx.ALL, 5)
    # mainSizer.Add(self.button, 0, wx.LEFT)
    self.SetSizerAndFit(mainSizer)

    #初始化界面

    img = wx.Image(Path_tmp_alarm + 'start.jpg', wx.BITMAP_TYPE_ANY).Scale(600, 800)
    sb = wx.StaticBitmap(self.p2, -1, wx.BitmapFromImage(img), size=(600, 800))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic1, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic2, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic3, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic4, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic5, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic6, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic7, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic8, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic9, -1, wx.BitmapFromImage(img), size=(180, 240))
    self.logger3.Clear()
    self.logger4.Clear()
    self.logger5.Clear()
    self.logger3.AppendText("%s" % 'None')
    self.logger4.AppendText("%s" % 'None')
    self.logger5.AppendText("%s" % 'None')

  def clear_pic(self):
    self.logger3.Clear()
    self.logger4.Clear()
    self.logger5.Clear()
    self.logger3.AppendText("%s" % 'None')
    self.logger4.AppendText("%s" % 'None')
    self.logger5.AppendText("%s" % 'None')
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic1, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic2, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic3, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic4, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic5, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic6, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic7, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic8, -1, wx.BitmapFromImage(img), size=(180, 240))
    img = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    sb = wx.StaticBitmap(self.pic9, -1, wx.BitmapFromImage(img), size=(180, 240))
  def show(self):
    #self.init.run_demo()
    self.init.test(path_in=Path_tmp_pic,path_out=Path_tmp_pic)
    self.clear_pic()
    # os.system('python /home/kuang/py-faster-rcnn-master/tools/demo_d.py')
    # os.system('python /home/kuang/py-faster-rcnn-master/tools/wxpython/demo_d.py')
    #time.sleep(0.2)

    #img_clear = wx.Image(Path_tmp_alarm + 'clear.jpg', wx.BITMAP_TYPE_ANY).Scale(180, 240)
    img = wx.Image(Path_tmp_pic + 'tmp.jpg', wx.BITMAP_TYPE_ANY).Scale(600, 800)
    sb = wx.StaticBitmap(self.p2, -1, wx.BitmapFromImage(img), size=(600, 800))
    f_info = open(Path_tmp_info, 'r')
    f_dir = open(Path_tmp_cloth, 'r')
    lines = f_info.readlines()
    lines_dir = f_dir.readlines()
    pic_num = 0
    for n, i in enumerate(lines_dir):
      if n >= 3:
        break#
      path_num = os.path.join("./num_class/ClothForClassify_train", i[:-1])
      pic_path = os.listdir(path_num)
      #print "List Pic PATH"
      #print pic_path
      eval('self.logger' + str(n + 3)).Clear()
      eval('self.logger' + str(n + 3)).AppendText("%s" % i[:-1])
      for m, j in enumerate(pic_path):
        if m >= 3:
          break
        pic_num += 1
        img = wx.Image(os.path.join(path_num, j), wx.BITMAP_TYPE_ANY).Scale(180, 240)
        sb = wx.StaticBitmap(eval('self.pic' + str(pic_num)), -1, wx.BitmapFromImage(img), size=(180, 240))

      if pic_num%3:
        pic_num=pic_num-pic_num%3+3
      #img = wx.Image(os.path.join(i[:-1],pic_path[0]), wx.BITMAP_TYPE_ANY).Scale(180, 240)
      #sb = wx.StaticBitmap(self.pic1, -1, wx.BitmapFromImage(img), size=(180, 240))
      #break

    for i in lines:
      self.logger2.AppendText("%s" % i)

  def AutoGet(self,e):
    if self.auto_flag==1:

      Get_picture("tmp.jpg", Path_tmp_pic)
      timer = Timer()
      #print "start"
      #time.sleep(0.1)
      timer.tic()
      self.show()
      #self.init.run_demo()
      timer.toc()
      print "demo times:%3f"%timer.total_time
      #print "end"
      #print time.time()
      # os.system('python /home/kuang/py-faster-rcnn-master/tools/demo_d.py')
      # os.system('python /home/kuang/py-faster-rcnn-master/tools/wxpython/demo_d.py')
      #time.sleep(0.2)

      #self.auto_flag=0
      #time.sleep(0.2)
        # self.logger2.AppendText("%s" % lines[-1])

  def GetPic(self,e):
    Get_picture("tmp.jpg", "./interface/tmp/wx_d/")
    #time.sleep(0.1)
    img = wx.Image('./interface/tmp/wx_d/tmp.jpg', wx.BITMAP_TYPE_ANY).Scale(600, 800)
    # os.system("cp -f ccTest.jpg /home/kuang/py-faster-rcnn-master/tmp/wx_d/tmp.jpg")
    sb = wx.StaticBitmap(self.p2, -1, wx.BitmapFromImage(img), size=(600, 800))

    #img = wx.Image(Path_tmp_pic + 'tmp.jpg', wx.BITMAP_TYPE_ANY).Scale(600, 800)
    #sb = wx.StaticBitmap(self.p3, -1, wx.BitmapFromImage(img), size=(600, 800))

  def AutoPic(self,e):
    self.auto_flag=not self.auto_flag

  def OpenImg(self,e):
    """ Open a file"""
    dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:
      self.filename = dlg.GetFilename()
      self.dirname = dlg.GetDirectory()
      path = os.path.join(self.dirname, self.filename)
      temp_dir = Path_tmp_pic+"tmp.jpg"
      # os.system('sudo rm -rf /home/flyvideo_2106/david/wx_d *')
      # os.system('cp path /home/flyvideo_2106/david/wx_d'
      f = open(path , 'r')

      f_temp = open(temp_dir, 'w')
      f_temp.write(f.read())
      self.ShowPic(path)
      f.close()
      f_temp.close()
    dlg.Destroy()

  def NewAdd(self,e):
    frame2 = AddNewFrame()
    frame2.Show()
    app.MainLoop()

  def RecoImg(self,e):
    self.show()
    #self.logger2.AppendText("%s" % lines[-1])

  #
  def ShowPic(self, path):
    img = wx.Image(path, wx.BITMAP_TYPE_ANY).Scale(600, 800)
    sb = wx.StaticBitmap(self.p2, -1, wx.BitmapFromImage(img), size=(600, 800))
    # self.grid.Add(sb, pos=(0, 2))

  def TakePic(self,e):
    os.system('./main')
    #time.sleep(0.1)
    img = wx.Image('ccTest.jpg', wx.BITMAP_TYPE_ANY).Scale(600, 800)
    os.system("cp -f ccTest.jpg ./interface/tmp/wx_d/tmp.jpg")
    sb = wx.StaticBitmap(self.p2, -1, wx.BitmapFromImage(img), size=(600, 800))

class AddNewPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)

    self.dirname = ''


    main_2_Sizer = wx.BoxSizer(wx.VERTICAL)
    self.grid = wx.GridBagSizer(hgap=5, vgap=5)
    self.Button_grid = wx.GridBagSizer(hgap=5, vgap=5)

    # fgs = wx.FlexGridSizer(cols=10, rows=10, hgap=50, vgap=10)
    hSizer = wx.BoxSizer(wx.HORIZONTAL)

    self.info1 = wx.StaticText(self, label="Detail: ")
    self.grid.Add(self.info1, pos=(0, 0))

    self.logger2 = wx.TextCtrl(self, size=(800, 600), style=wx.TE_MULTILINE | wx.TE_READONLY)
    self.grid.Add(self.logger2, pos=(1, 0))

    self.button1 = wx.Button(self, label="Open")
    self.Bind(wx.EVT_BUTTON, self.OpenTrainFile, self.button1)
    self.Button_grid.Add(self.button1, pos=(0,0))

    self.button2 = wx.Button(self, label="PreData")
    self.Bind(wx.EVT_BUTTON, self.DataPreprocess, self.button2)
    self.Button_grid.Add(self.button2, pos=(0,1))

    self.button3 = wx.Button(self, label="Train")
    self.Bind(wx.EVT_BUTTON, self.TrainNew, self.button3)
    self.Button_grid.Add(self.button3, pos=(0,2))

    self.grid.Add(self.Button_grid, pos=(2, 0))




    hSizer.Add(self.grid, 0, wx.ALL, 5)
    # hSizer.Add(self.logger)
    main_2_Sizer.Add(hSizer, 0, wx.ALL, 5)
    # mainSizer.Add(self.button, 0, wx.LEFT)
    self.SetSizerAndFit(main_2_Sizer)

  def OpenTrainFile(self, e):
    """ Open a Directory"""
    Train_Set_Dir =    './num_class/ClothForClassify_train/'
    Train_Config_Dir = './num_class/'
    # dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
    dlg = wx.DirDialog(self, "Choose a Directory", style=wx.DD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
      Train_config_path = dlg.GetPath() + '/Train_config.txt'
      # os.system('cp -f %s %s'%(Train_Config_Dir, Train_config_path))

      # Train_info = f_Train_config.readlines()
      # test = Train_info[0].split(':')[1]
      DirName = dlg.GetPath().split('/')[-1]

      New_Set_Path = Train_Set_Dir +'/' +DirName
      New_Train_config_Path = New_Set_Path +'/Train_config.txt'

      os.system('cp -rf %s %s' % (dlg.GetPath(),Train_Set_Dir))  #将新增类数据复制到训练集中
      os.system('mv -f %s %s'% (New_Train_config_Path,Train_Config_Dir) ) #复制配置文件
      os.system('rm -f %s' % (New_Train_config_Path+'~'))
      New_Train_config_Path = Train_Config_Dir + '/Train_config.txt'
      f_Train_config = open(New_Train_config_Path, 'a+')
      tmp = 'New_Set_Name:%s'% DirName
      f_Train_config.write(tmp)
      f_Train_config.close()
      self.logger2.AppendText("Get Train Set Done!\n")

  def DataPreprocess_thread(self,Train_DIR):
    os.system('python ./demo_client.py')
    e = ExpandTrainData()
    e.runExpand()
    # self.logger2.AppendText(info)
    os.system('python %s/anno_train.py' % Train_DIR)
    os.system('python %s/anno_test.py' % Train_DIR)

    self.logger2.AppendText("Data Preprocess Completed!\n")

  def DataPreprocess(self,e):
    self.logger2.AppendText("Data Proprocessing...\nPlease Wait...\n")
    Train_DIR = './num_class'
    t_train = threading.Thread(target=self.DataPreprocess_thread, args=(Train_DIR,))
    t_train.start()
    # pass

    # self.logger2.AppendText("Data Proprocessing Completed!\n")


  def TrainNet_thread(self,Train_DIR):
    print "start training"
    trainNet = ResTrain()
    tic = time.time()
    trainNet.main()
    toc = time.time()
    spend_time = "%.3f" % ((toc - tic)/60.0)
    self.logger2.AppendText("100%\n")
    self.logger2.AppendText("Train Complete!\n")
    self.logger2.AppendText("This train spends %s min\n" % (spend_time))
    # os.system('python %s/resnet.py' % Train_DIR)
  def TrainRecord(self):
    record_info = '0'
    first = True
    # while True:
    #   epoch = cfr.train_epoch
    #   # train_accuracy = cfr.train_accuracy
    #   info = epoch
    #   if first:
    #     record_info = info
    #     info = info / 20.0 * 100
    #     self.logger2.AppendText(str(info) + '%\n')
    #     first = False
    #   if not info == record_info:
    #     record_info = info
    #     info = info / 20.0 * 100
    #     self.logger2.AppendText(str(info) + '%\n')
    #   if info == 20:
    #     # self.logger2.AppendText("Train Accuracy: %s\n" % train_accuracy)
    #     self.logger2.AppendText("Train Complete!\n")
    #
    #     break
    #   time.sleep(5)
    record_path = "./num_class/Train_record_tmp.txt"

    rinfo = ''
    while True:
      # info = 'a'
      # self.logger2.AppendText(str(cfr.flag))
      if cfr.flag == False:
        f_record = open(record_path, 'r')
        rinfo = f_record.read()
        if first:
          record_info = rinfo
          self.logger2.AppendText(rinfo + '.0%\n')
          first = False
        cfr.flag = True
        f_record.close()
        if not (record_info == rinfo):
          record_info = rinfo
          tmp = rinfo
          tmp = int(tmp)/20.0 * 100
          tmp = str(tmp)
          self.logger2.AppendText(tmp + '%\n')
        if int(record_info) == 19:
          break
      time.sleep(4)

  def TrainNew(self, e):
    Train_DIR = './num_class'
    self.logger2.AppendText("Start Training ...\n" + time.ctime() + '\n')

    t_train = threading.Thread(target=self.TrainNet_thread,args=(Train_DIR,))
    t_train.start()
    # time.sleep(5)
    t_record = threading.Thread(target=self.TrainRecord)
    t_record.start()



class MyFrame(wx.Frame):
  def __init__(self):
    wx.Frame.__init__(self, None, -1, 'Clothes Smart', size=(2000,1000))
    panel = ExamplePanel(self)

class AddNewFrame(wx.Frame):
  def __init__(self):
    wx.Frame.__init__(self, None, -1, 'AddNew', size=(420, 400))
    panel = AddNewPanel(self)

if __name__=='__main__':
  # os.system('python /home/kuang/py-faster-rcnn-master/tools/init.py')
  # init = NetInit()
  # cfg.caffemodel, cfg.net, cfg.CLASSES = init.getargs()
  app = wx.App(False)
  frame = MyFrame()
  frame.Show()
  app.MainLoop()