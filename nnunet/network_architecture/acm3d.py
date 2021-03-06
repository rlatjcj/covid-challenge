import torch
import torch.nn as nn
from torch.nn import functional as F

#reference: https://github.com/mk-minchul/attend-and-compare/blob/master/context_module.py

class ACM3D(nn.Module):
    def __init__(self, num_heads, num_features, orthogonal_loss=True):
        super(ACM3D, self).__init__()
        assert num_features % num_heads == 0, 'num_features/num_heads must be 0'

        self.num_heads = num_heads
        self.num_features = num_features

        self.P_module = ModulateModule(channel=self.num_features, num_groups=num_heads, compressions=2)
        self.K_module = AttendModule(self.num_features, num_heads=num_heads)
        self.Q_module = AttendModule(self.num_features, num_heads=num_heads)

    def forward(self, x):
        mu = x.mean([2,3,4], keepdim=True)
        x_mu = x - mu

        P = self.P_module(mu)
        K = self.K_module(x_mu)
        Q = self.Q_module(x_mu)
        
        y = (x + K - Q ) * P

        return y

class AttendModule(nn.Module):
    def __init__(self, num_features, num_heads):
        super(AttendModule, self).__init__()

        self.num_heads = int(num_heads)
        self.num_features = num_features

        self.num_ch_per_head = self.num_features // self.num_heads

        self.conv = nn.Conv3d(self.num_features, self.num_heads, kernel_size=1, stride=1, padding=0, bias=True, groups=num_heads)
        self.normalize = nn.Softmax(dim=2) #channel wise normalization

        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                nn.init.constant_(m.bias, 0.0)

    def forward(self, x):
        b, c, h, w, z = x.shape
        
        x_reshape = x.view(b*self.num_heads, self.num_ch_per_head, h, w, z)
        x_reshape = x_reshape.view(b*self.num_heads, self.num_ch_per_head, h*w*z)

        weights = self.conv(x)
        weights_reshape = weights.view(b*self.num_heads, 1, h, w, z)
        weights_reshape = weights_reshape.view(b*self.num_heads, 1, h*w*z)
        weights_normalized = self.normalize(weights_reshape)
        weights_normalized = weights_normalized.transpose(1,2)

        res = torch.bmm(x_reshape, weights_normalized)
        res = res.view(b, self.num_heads * self.num_ch_per_head, 1, 1, 1)
        
        return res

class ModulateModule(nn.Module):
    def __init__(self, channel, num_groups=32, compressions=2):
        super(ModulateModule, self).__init__()
        self.feature = nn.Sequential(
            nn.Conv3d(channel, channel//compressions, kernel_size=1, stride=1, padding=0, bias=True, groups=num_groups),
            nn.ReLU(inplace=True),
            nn.Conv3d(channel//compressions, channel, kernel_size=1, stride=1, padding=0, bias=True, groups=num_groups),
            nn.Sigmoid()
            )

        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                nn.init.constant_(m.bias, 0.0)

    def forward(self, x):
        return self.feature(x)
