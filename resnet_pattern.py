import torch.nn as nn
import math
import torch.utils.model_zoo as model_zoo
import torch

__all__ = ['ResNet', 'resnet_combine', 'resnet18', 'resnet34', 'resnet50', 'resnet101', 'valve',
           'resnet152', 'resnet_new']

model_urls = {
    'resnet18': 'https://download.pytorch.org/models/resnet18-5c106cde.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-333f7ec4.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
}


def conv3x3(in_planes, out_planes, stride=1):
    "3x3 convolution with padding"
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class ResNet(nn.Module):

    def __init__(self, block, layers, num_classes=1000):
        self.inplanes = 64
        super(ResNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        self.avgpool = nn.AvgPool2d(7)
        self.fc = nn.Linear(512 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x


class ResNet_new(nn.Module):

    def __init__(self, block, layers, num_classes=1000):
        self.inplanes = 64
        super(ResNet_new, self).__init__()
        self.conv0 = nn.Conv2d(3, 3, kernel_size=7, stride=2, padding=3,
                               bias=True)
        self.bn0 = nn.BatchNorm2d(3)
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        self.avgpool = nn.AvgPool2d(7)
        # self.fc_down=nn.Linear(512 * block.expansion, 512)
        self.fc = nn.Linear(512 * block.expansion, num_classes)
        # self.fc = nn.Linear(512, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))

            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
        # print "mmmmmmmmmmmmmmmmmmmmmmmmmmm"
        # for i in self.fc.weight.data:
        #     for j in i:
        # print "enddddddddddddddddd"

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv0(x)
        x = self.bn0(x)
        x = self.relu(x)
        # x = self.maxpool(x)

        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        # print "avg"
        # print x
        x = x.view(x.size(0), -1)
        # print "view"
        # print x
        # x = self.fc_down(x)
        # print "xxxxxxxxxx"
        # print x
        # x = self.fc(x)
        x = self.fc(x)
        # x = self.relu(x)
        return x


class combine_layer(nn.Module):
    def __init__(self):
        super(combine_layer, self).__init__()

        self.w1 = nn.Conv2d(512 * 4, 512 * 4, kernel_size=1)
        self.w2 = nn.Conv2d(512 * 4, 512 * 4, kernel_size=1)
        self.w3 = nn.Conv2d(512 * 4, 512 * 4, kernel_size=1)
        self.b1 = nn.BatchNorm2d(512 * 4)
        self.b2 = nn.BatchNorm2d(512 * 4)
        self.b3 = nn.BatchNorm2d(512 * 4)
        # self.w1=0.1
        # self.w2=0.2
        # self.w3=0.7
        # self.w_sum=(self.w1+self.w2+self.w3)+1e-10
        self.n1 = 0.01
        self.n2 = 0.04
        self.n3 = 0.95

    def get_acc(self, accuracy):
        def lu(x):
            if x < 0:
                x = 0
            return x

        ac_num = lu(accuracy - 0.9)
        self.n1 = accuracy * 0.1
        self.n2 = accuracy * 0.2
        self.n3 = (1 - accuracy * 0.3)

    def forward(self, x1, x2, x3):
        # self.w1=self.w1/self.w_sum
        # self.w2=self.w2/self.w_sum

        out = self.b1(self.w1(x1)) * self.n1 + self.b2(self.w2(x2)) * self.n2 + self.b3(self.w3(x3)) * self.n3
        return out


class valve(nn.Module):
    def __init__(self, outnum):
        super(valve, self).__init__()
        self.valve_line = nn.Linear(1, outnum)
        self.sig = nn.Sigmoid()
        for i in range(outnum - 1):
            self.valve_line.weight[i].data.fill_(0.05)
        self.valve_line.weight[outnum - 1].data.fill_(0.95)
        self.valve_line.bias.data.zero_()
        self.outnum = outnum

    def forward(self):
        x = torch.FloatTensor([1])
        x = torch.autograd.Variable(x)
        x = self.valve_line(x)
        x = self.sig(x)
        # out=x1*x[0]+x2*x[1]
        # x=x*num
        # return [0,1]
        return x


class val(nn.Module):
    def __init__(self):
        super(val, self).__init__()
        w1 = torch.FloatTensor([0.0])
        self.w1 = torch.autograd.Variable(w1, requires_grad=True)
        w2 = torch.FloatTensor([1])
        self.w2 = torch.autograd.Variable(w2, requires_grad=True)
        # self.w1=torch.arange([0.05])
        # self.w2=torch.arange([0.95])
        # self.register_parameter('w1',self.w1)
        # self.register_parameter('w2',self.w2)
        # self.relu=nn.ReLU(inplace=True)
        # self.w1=torch.autograd.Variable(torch.FloatTensor([0.05]))
        # self.w2=torch.autograd.Variable(torch.FloatTensor([0.95]))

    def forward(self, x1, x2):
        out = x1 * self.w1[0] + x2 * self.w2[0]
        return out


class ResNet_combine(nn.Module):

    def __init__(self, block, layers, num_classes=1000):
        self.inplanes = 64
        super(ResNet_combine, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        # self.drop1=nn.Dropout(0.5)
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        # self.drop2 = nn.Dropout(0.5)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        # self.valve_line=val()
        self.valve_line = valve(2)
        self.w = self.valve_line()
        # print self.w
        self.w1 = self.w.data[0]
        self.w2 = self.w.data[1]
        # self.w1=0.05
        # self.w2=0.95
        # self.w1=torch.autograd.Variable(torch.FloatTensor([0.05]))
        # self.w1=self.w[0]
        # self.w2=torch.autograd.Variable(torch.FloatTensor([0.95]))
        # self.w2=self.w[1]
        # print "================layer3=================="
        # print self.layer3
        layer31 = []
        layer32 = []
        for i in range(23):
            if i < 6:
                layer31.append(self.layer3[i])
            else:
                layer32.append(self.layer3[i])

        self.layer31 = nn.Sequential(*layer31)

        self.layer32 = nn.Sequential(*layer32)
        # self.val_line=nn.Linear(2,2)
        # print "================layer31=================="
        # print self.layer31
        # print "================layer32=================="
        # print self.layer32
        # self.valve_model=valve(2)
        # self.valve_num=self.valve_model()
        # print self.valve
        # self.drop3 = nn.Dropout(0.5)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        #
        # inplanes=self.inplanes
        # self.layer13 = self._make_layer(block, 256, layers[2], stride=2)
        # #self.layer14 = self._make_layer(block, 512, layers[3], stride=2)
        # self.num1=nn.Conv2d(512*4,512*4,kernel_size=1)
        # self.bbn1=nn.BatchNorm2d(512*4)
        #
        # self.inplanes=inplanes
        # self.layer23 = self._make_layer(block, 256, layers[4], stride=2)
        # #self.layer24 = self._make_layer(block, 512, layers[5], stride=2)
        # self.num2 = nn.Conv2d(512*4, 512*4, kernel_size=1)
        # self.bbn2 = nn.BatchNorm2d(512*4 )
        #
        # self.inplanes = inplanes
        # self.layer33 = self._make_layer(block, 256, layers[6], stride=2)
        # #self.layer34 = self._make_layer(block, 512, layers[7], stride=2)
        # self.num3 = nn.Conv2d(512*4, 512*4, kernel_size=1)
        # self.bbn3 = nn.BatchNorm2d(512*4)
        #

        # self.com=combine_layer()
        # self.avgpool = nn.AvgPool2d(7)
        self.avgpool = nn.MaxPool2d(7)
        # self.drop_fc=nn.Dropout(0.5)
        self.fc = nn.Linear(512 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
        # self.val_line.weight[0].data.fill_(0)
        # self.val_line.weight[1].data.fill_(1)
        # self.val_line.bias.data.zero_()
        '''
        self.com.w1.weight.data.fill_(0.1)
        self.com.w2.weight.data.fill_(0.2)
        self.com.w3.weight.data.fill_(0.7)
        '''

    # def acc_num(self,accuracy):
    #     self.com.get_acc(accuracy)

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        # x=self.drop1(x)
        x = self.layer2(x)
        # x=self.drop2(x)
        # x = self.layer3(x)
        # x2 = self.layer4(x)
        x1 = self.layer31(x)
        x2 = self.layer32(x1)
        # print self.valve()
        # valve_num = self.valve()
        # print self.valve_num
        # out = x1 * valve_num[0] + x2 * valve_num[1]
        # print "OUT==============="
        # print valve_num[0],valve_num[1]
        # w=self.valve_line()
        # print "self.w1"
        # out=x1*self.w1+x2*self.w2
        # out=self.valve_line(x1,x2)
        # out=self.valve_line(x1,x2)

        # out=x1*self.w.data[0]+x2*self.w.data[1]
        out = x1 * self.w1 + x2 * self.w2
        # out=self.drop3(out)
        out = self.layer4(out)
        # valve_num=self.valve()
        # out=x1*valve_num[0]+x2*valve_num[1]
        # print "layer12312121=---========================="
        # print x.size

        # x1 = self.layer13(x)
        # x1 = self.layer14(x1)
        # x1 = self.num1(x1)
        # x1 = self.bbn1(x1)
        #
        # x2 = self.layer23(x)
        # x2 = self.layer24(x2)
        # #x2 = self.num2(x2)
        # x2 = self.bbn2(x2)
        #
        # #b=x.size()
        # #print b
        # x3 = self.layer33(x)
        # #print "222"
        # x3 = self.layer34(x3)
        # #x3 = self.num3(x3)
        # x3 = self.bbn3(x3)

        # x=x1+x2+x3
        # print "xxxxxxx"
        # print x1.size,x2.size,x3.size
        # x=x1*0.1+x2*0.2+x3*0.7
        # x=self.com(x1,x2,x3)
        # x=x1*0,5+x3*0.5
        # x=self.relu(x)

        x = self.avgpool(out)
        # x=self.drop_fc(x)
        x = x.view(x.size(0), -1)

        x = self.fc(x)

        return x


def valve_mod(num, **kwargs):
    model = valve(num)
    return model


def resnet_combine(pretrained=False, **kwargs):
    # model = ResNet_combine(Bottleneck, [3, 4, 23 ,3, 12, 3, 23 ,3], **kwargs)
    model = ResNet_combine(Bottleneck, [3, 4, 23, 3], **kwargs)
    '''
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet18']))
    return model
    '''
    if pretrained:
        # own_state=model.state_dict
        model.load_state_dict_part(model_zoo.load_url(model_urls['resnet101']))
    return model


def resnet_new(pretrained=False, **kwargs):
    # model = ResNet_combine(Bottleneck, [3, 4, 23 ,3, 12, 3, 23 ,3], **kwargs)
    model = ResNet_new(Bottleneck, [3, 4, 23, 3], **kwargs)

    if pretrained:
        # own_state=model.state_dict
        model.load_state_dict_part(model_zoo.load_url(model_urls['resnet101']))
    return model


def resnet18(pretrained=False, **kwargs):
    """Constructs a ResNet-18 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(BasicBlock, [2, 2, 2, 2], **kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet18']))
    return model


def resnet34(pretrained=False, **kwargs):
    """Constructs a ResNet-34 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(BasicBlock, [3, 4, 6, 3], **kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet34']))
    return model


def resnet50(pretrained=False, **kwargs):
    """Constructs a ResNet-50 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(Bottleneck, [3, 4, 6, 3], **kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet50']))
    return model


def resnet101(pretrained=False, **kwargs):
    """Constructs a ResNet-101 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(Bottleneck, [3, 4, 23, 3], **kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet101']))
    return model


def resnet152(pretrained=False, **kwargs):
    """Constructs a ResNet-152 model.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = ResNet(Bottleneck, [3, 8, 36, 3], **kwargs)
    if pretrained:
        model.load_state_dict(model_zoo.load_url(model_urls['resnet152']))
    return model
