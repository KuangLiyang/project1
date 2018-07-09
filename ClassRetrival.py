# -*-coding:utf-8-*-

import wx
class ReWin(wx.Panel):
    def __init__(self, parent,app):
        wx.Panel.__init__(self, parent)
        self.app=app
        self.retrival_flag=0
        self.prince1,self.prince2=self.app.get_prince()
        if  self.prince2==None:
            self.p_top_flag = 0
        else:
            self.p_top_flag = 1

        if self.prince1==None:
            self.p_bottom_flag = 0
        else:
            self.p_bottom_flag = 1


        self.age1,self.age2 = self.app.get_age_num()
        self.sex_num=self.app.get_sex()
        self.dress_label,self.top_label,self.bottom_label=self.app.get_class()

        # self.dress_label = '全部'
        # self.top_label = '全部'
        # self.bottom_label = '全部'
        self.version_label,self.style_label=self.app.get_attribute()
        # self.version_label = '全部'
        # self.style_label = '全部'
        self.age_label=self.app.get_age()
        #self.age_label = '全部'
        #self.age_auto_flag = 1

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.hSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.grid = wx.GridBagSizer(hgap=6, vgap=6)
        self.font1 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.font2 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        #=============================================prince================================================
        self.grid1=wx.GridBagSizer(hgap=2, vgap=6)
        self.grid.Add(self.grid1,pos=(0,0))
        self.title1=wx.StaticText(self,label= "价格:")
        self.title1.SetFont(self.font1)
        self.t1= wx.TextCtrl(self, size=(90, 25),style=wx.TE_PROCESS_ENTER)
        self.t1.Bind(wx.EVT_TEXT_ENTER, self.Prince1)
        self.si1=wx.StaticText(self,label= "至")
        self.t2= wx.TextCtrl(self, size=(90, 25),style=wx.TE_PROCESS_ENTER)
        self.t2.Bind(wx.EVT_TEXT_ENTER, self.Prince2)
        self.t3=wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.grid1.Add(self.title1, pos=(0, 0))
        self.grid1.Add(self.t1, pos=(0, 1))
        self.grid1.Add(self.si1,pos=(0, 2))
        self.grid1.Add(self.t2, pos=(0, 3))
        self.grid1.Add(self.t3, pos=(0, 4))
        self.t3.Clear()
        self.t3.AppendText('价格范围为：不限制')
        # age
        # self.title10 = wx.StaticText(self, label="年龄:")
        # self.title10.SetFont(self.font1)
        # self.t3 = wx.TextCtrl(self, size=(90, 25), style=wx.TE_PROCESS_ENTER)
        # self.t3.Bind(wx.EVT_TEXT_ENTER, self.Age1)
        # self.si2 = wx.StaticText(self, label="至")
        # self.t4 = wx.TextCtrl(self, size=(90, 25), style=wx.TE_PROCESS_ENTER)
        # self.t4.Bind(wx.EVT_TEXT_ENTER, self.Age2)
        # self.t5 = wx.TextCtrl(self, size=(180, 25), style=wx.TE_MULTILINE | wx.TE_READONLY)
        # self.grid1.Add(self.title10, pos=(1, 0))
        # self.grid1.Add(self.t3,  pos=(1, 1))
        # self.grid1.Add(self.si2, pos=(1, 2))
        # self.grid1.Add(self.t4,  pos=(1, 3))
        # self.grid1.Add(self.t5,  pos=(1, 4))
        # self.t5.Clear()
        # self.t5.AppendText('年龄范围为：不限制')
        # self.button1 = wx.Button(self, label="自动")
        # self.Bind(wx.EVT_BUTTON, self.Auto_Age, self.button1)
        # self.grid1.Add(self.button1, pos=(1, 5))
        #==============================================sex========================================================
        self.grid2 = wx.GridBagSizer(hgap=1, vgap=6)
        self.grid.Add(self.grid2, pos=(1, 0))
        self.title2 = wx.StaticText(self, label= "性别:")
        self.title2.SetFont(self.font1)
        self.grid2.Add(self.title2, pos=(0, 0))
        self.radio1 = wx.RadioButton(self, label="自动")
        self.radio2 = wx.RadioButton(self, label="全选")
        self.radio3 = wx.RadioButton(self, label="女装")
        self.radio4 = wx.RadioButton(self, label="男装")
        # radioList=['自动',"全部","女装","男装"]
        # self.rbox=wx.RadioBox(self,choices=radioList)

        self.grid2.Add(self.radio1, pos=(0, 1))
        self.grid2.Add(self.radio2, pos=(0, 2))
        self.grid2.Add(self.radio3, pos=(0, 3))
        self.grid2.Add(self.radio4, pos=(0, 4))
        for eachRadio in [self.radio1, self.radio2, self.radio3,self.radio4]:  # 绑定事件
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, eachRadio)
        #=========================================================class==========================================================
        self.grid3 = wx.GridBagSizer(hgap=8, vgap=8)
        self.grid.Add(self.grid3, pos=(2, 0))
        self.title3 = wx.StaticText(self, label="类别:")
        self.title3.SetFont(self.font1)
        self.grid3.Add(self.title3, pos=(0, 0))

        self.title4 = wx.StaticText(self, label="连衣裙")
        self.grid3.Add(self.title4, pos=(0, 1))
        sampleList1 = ['不选','全选','连衣裙']
        self.combo1=wx.ComboBox(self,-1,choices=sampleList1,value='全选')
        self.grid3.Add(self.combo1,pos=(0,2))
        self.combo1.Bind(wx.EVT_COMBOBOX, self.OnCombo1)

        self.title5 = wx.StaticText(self, label="上装")
        self.grid3.Add(self.title5, pos=(0, 3))
        sampleList2 = ['不选', '全选', '衬衫','T恤','外套','打底衫','卫衣','毛衣']
        self.combo2 = wx.ComboBox(self, -1, choices=sampleList2,value='全选')
        self.grid3.Add(self.combo2, pos=(0, 4))
        self.combo2.Bind(wx.EVT_COMBOBOX, self.OnCombo2)

        self.title6 = wx.StaticText(self, label="下装")
        self.grid3.Add(self.title6, pos=(0, 5))
        sampleList3 = ['不选', '全选', '半身裙','休闲裤','牛仔裤','西裤','阔腿裤','打底裤']
        self.combo3 = wx.ComboBox(self, -1, choices=sampleList3,value='全选')
        self.grid3.Add(self.combo3, pos=(0, 6))
        self.combo3.Bind(wx.EVT_COMBOBOX, self.OnCombo3)


        #===============================================attribute============================================================
        # self.grid4 = wx.GridBagSizer(hgap=1, vgap=8)
        # self.grid.Add(self.grid4, pos=(3, 0))
        self.title7 = wx.StaticText(self, label="属性:")
        self.title7.SetFont(self.font1)
        self.grid3.Add(self.title7, pos=(1, 0))
        # self.grid4.Add(self.title7, pos=(0, 0))

        self.title8 = wx.StaticText(self, label="款式")
        self.grid3.Add(self.title8, pos=(1, 1))
        sampleList4 = ['全选', '休闲','修身','宽松','标准','直筒','A型','H型','其他']
        self.combo4 = wx.ComboBox(self, -1, choices=sampleList4, value='全选')
        self.grid3.Add(self.combo4, pos=(1, 2))
        self.combo4.Bind(wx.EVT_COMBOBOX, self.OnCombo4)

        self.title9 = wx.StaticText(self, label="款式")
        self.grid3.Add(self.title9, pos=(1, 3))
        sampleList5 = ['全选', '休闲', '通勤', '简约复古', '优雅淑女', '清新文艺','流行街拍','百搭' ,'正装','甜美','民族','日韩', '欧美', '其他']
        self.combo5 = wx.ComboBox(self, -1, choices=sampleList5, value='全选')
        self.grid3.Add(self.combo5, pos=(1, 4))
        self.combo5.Bind(wx.EVT_COMBOBOX, self.OnCombo5)
        #=====================================================age========================================================
        self.title10 = wx.StaticText(self, label="年龄:")
        self.title10.SetFont(self.font1)
        self.grid3.Add(self.title10, pos=(2, 0))
        # self.grid4.Add(self.title7, pos=(0, 0))

        self.title11 = wx.StaticText(self, label="范围")
        self.grid3.Add(self.title11, pos=(2, 1))
        sampleList6 = ['全选', '自动','18-30', '30-40', '40以上', '未定义']
        self.combo6 = wx.ComboBox(self, -1, choices=sampleList6, value='全选')
        self.grid3.Add(self.combo6, pos=(2, 2))
        self.combo6.Bind(wx.EVT_COMBOBOX, self.OnCombo6)

        # self.button1 = wx.Button(self, label="自动")
        # self.Bind(wx.EVT_BUTTON, self.Auto_Age, self.button1)
        # self.grid3.Add(self.button1, pos=(2, 4))

        self.button2 = wx.Button(self, label="恢复默认")
        self.Bind(wx.EVT_BUTTON, self.Return_Default, self.button2)
        self.grid3.Add(self.button2, pos=(3, 0))
        self.hSizer.Add(self.grid, 0, wx.ALL, 5)
        # hSizer.Add(self.logger)
        #===================================================初始化=========================================================
        self.combo1.SetValue(self.dress_label)
        self.combo2.SetValue(self.top_label)
        self.combo3.SetValue(self.bottom_label)
        self.combo4.SetValue(self.version_label)
        self.combo5.SetValue(self.style_label)
        self.combo6.SetValue(self.age_label)
        if self.sex_num=='自动':
            self.radio1.SetValue(True)
        elif self.sex_num=='全选':
            self.radio2.SetValue(True)
        elif self.sex_num=='女装':
            self.radio3.SetValue(True)
        elif self.sex_num=='男装':
            self.radio4.SetValue(True)

        self.t1.Clear()
        self.t2.Clear()
        self.t3.Clear()
        self.t1.AppendText(str(self.prince1))
        self.t2.AppendText(str(self.prince2))
        self.show_prince()
        self.mainSizer.Add(self.hSizer, 0, wx.ALL, 5)
        # mainSizer.Add(self.button, 0, wx.LEFT)
        self.SetSizerAndFit(self.mainSizer)
    # def GetRetrivalParams(self,value='sex'):
    #     if value=='sex':
    #         return self.sex_num
    #     elif value=='prince':
    #         return self.prince1,self.prince2
    #     elif value=='class':
    #         return (self.dress_label,self.top_label,self.bottom_label)
    #     elif value=='age':
    #         return (self.age1,self.age2,self.age_auto_flag)
    #     elif value=='attribute':
    #         return (self.version_label,self.style_label)
    #     else:
    #         print "Error"
    #         return None

    def Class_Default(self):
        self.combo1.SetValue('全选')
        self.combo2.SetValue('全选')
        self.combo3.SetValue('全选')
        self.combo4.SetValue('全选')
        self.combo5.SetValue('全选')
        self.combo6.SetValue('全选')
        self.radio1.SetValue(True)
        self.t1.Clear()
        self.t2.Clear()
        self.t3.Clear()
        self.t3.AppendText('价格范围为：不限制')
        self.sex='自动'
        self.app.set_sex(self.sex)
        self.dress_label = '全选'
        self.top_label   = '全选'
        self.bottom_label = '全选'
        self.app.set_class(self.dress_label,self.top_label,self.bottom_label)
        self.version_label= '全选'
        self.style_label= '全选'
        self.app.set_attribute(self.version_label,self.style_label)
        self.age_label= '全选'
        self.app.set_age(self.age_label)

        self.prince1 = None
        self.prince2 = None
        self.app.set_prince(self.prince1,self.prince2)
    # def Auto_Age(self,event):
    #     self.age_auto_flag=not self.age_auto_flag
    def Return_Default(self,event):
        self.Class_Default()
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
    def OnCombo1(self, event):
        self.dress_label=self.combo1.GetValue()
        self.app.set_class(self.dress_label, self.top_label, self.bottom_label)
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.dress_label

    def OnCombo2(self, event):
        self.top_label = self.combo2.GetValue()
        self.app.set_class(self.dress_label, self.top_label, self.bottom_label)
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.top_label

    def OnCombo3(self, event):
        self.bottom_label = self.combo3.GetValue()
        self.app.set_class(self.dress_label, self.top_label, self.bottom_label)
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.bottom_label

    def OnCombo4(self, event):
        self.version_label = self.combo4.GetValue()
        self.app.set_attribute(self.version_label, self.style_label)
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.version_label

    def OnCombo5(self, event):
        self.style_label = self.combo5.GetValue()
        self.app.set_attribute(self.version_label, self.style_label)
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.style_label
    def OnCombo6(self, event):
        self.age_label = self.combo6.GetValue()
        self.app.set_age(self.age_label)
        if self.age_label=='40以上':
            self.age1=40
            self.age2=None
        elif self.age_label != '未定义':
            ages=self.age_label.split('-')
            self.age1=int(ages[0])
            self.age2=int(ages[1])
        else:
            self.age1 = None
            self.age2 = None
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.age_label
    def OnRadio(self,event):
        self.sex_num = event.GetEventObject().GetLabel()
        self.app.set_sex(self.sex_num)
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.sex_num
    def show_prince(self):
        self.t3.Clear()
        if self.p_top_flag and self.p_bottom_flag:
            self.t3.AppendText('价格范围为：%d至%d元' % (self.prince1, self.prince2))
        elif self.p_top_flag==0 and self.p_bottom_flag:
            self.t3.AppendText('价格范围为：%d元以上' % (self.prince1))
        elif self.p_top_flag and self.p_bottom_flag==0:
            self.t3.AppendText('价格范围为：%d元以下' % (self.prince2))
        else:
            self.t3.AppendText('价格范围为：不限制')

    def Prince1(self,event):
        prince1=event.GetString()
        try:
            self.prince1=int(prince1)
            self.p_bottom_flag=1
        except:
            self.prince1=None
            self.p_bottom_flag=0
        self.app.set_prince(self.prince1, self.prince2)
        self.show_prince()
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.prince1
    def Prince2(self,event):
        prince2 = event.GetString()
        try:
            self.prince2 = int(prince2)
            self.p_top_flag = 1
        except:
            self.prince2 = None
            self.p_top_flag = 0
        self.app.set_prince(self.prince1, self.prince2)
        self.show_prince()
        self.retrival_flag = 1
        self.app.set_retrival_flag(self.retrival_flag)
        print self.prince2

    # def show_age(self):
    #     self.t5.Clear()
    #     if self.a_top_flag and self.a_bottom_flag:
    #         self.t5.AppendText('年龄范围为：%d至%d岁' % (self.age1, self.age2))
    #     elif self.p_top_flag==0 and self.p_bottom_flag:
    #         self.t5.AppendText('年龄范围为：%d岁以上' % (self.age1))
    #     elif self.p_top_flag and self.p_bottom_flag==0:
    #         self.t5.AppendText('年龄范围为：%d岁以下' % (self.age2))
    #     else:
    #         self.t5.AppendText('年龄范围为：不限制')
    # def Age1(self,event):
    #     age1=event.GetString()
    #     try:
    #         self.age1=int(age1)
    #         self.a_bottom_flag=1
    #     except:
    #         self.age1=None
    #         self.a_bottom_flag=0
    #     self.show_age()
    #
    #     print self.prince1
    # def Age2(self,event):
    #     age2 = event.GetString()
    #     try:
    #         self.prince2 = int(age2)
    #         self.a_top_flag = 1
    #     except:
    #         self.age2 = None
    #         self.a_top_flag = 0
    #     self.show_age()

class ClothRe(wx.Frame):
  def __init__(self,app):
    wx.Frame.__init__(self, None, -1, '服装类别', size=(500,250),style=wx.DEFAULT_FRAME_STYLE)
    self.panel = ReWin(self,app)
    self.Show()
    print 'ok'


#if __name__=='__main__':
    # app=wx.App()
    # cs=ClothRe()
    # app.MainLoop()
# app = wx.App()
# Mywin(None, 'TextCtrl实例-www.yiibai.com')
# app.MainLoop()