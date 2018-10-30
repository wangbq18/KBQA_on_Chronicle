# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: text_cnn.py

@time: 18-10-23

@desc:


"""

import torch.nn as nn
import torch.nn.functional as F
import torch


class TextCNN(nn.Module):
    def __init__(self, vocab_size, hidden_dim, filter_num, class_num):
        super(TextCNN, self).__init__()

        self.embedding_layer = nn.Embedding(vocab_size, hidden_dim)
        self.conv_layer1 = nn.Conv2d(in_channels=1, out_channels=filter_num, kernel_size=(3, hidden_dim), bias=False)
        self.conv_layer2 = nn.Conv2d(in_channels=1, out_channels=filter_num, kernel_size=(4, hidden_dim), bias=False)
        self.conv_layer3 = nn.Conv2d(in_channels=1, out_channels=filter_num, kernel_size=(5, hidden_dim), bias=False)

        self.dense_layer = nn.Linear(3 * filter_num, 3 * filter_num)
        self.out_layer = nn.Linear(3 * filter_num, class_num)

    def forward(self, inputs):
        embedding = self.embedding_layer(inputs)
        embedding = embedding.unsqueeze(1)

        conv1 = self.conv_layer1(embedding).squeeze(3)
        conv2 = self.conv_layer2(embedding).squeeze(3)
        conv3 = self.conv_layer3(embedding).squeeze(3)

        max1 = F.max_pool1d(conv1, kernel_size=conv1.size(2)).squeeze(2)
        max2 = F.max_pool1d(conv2, kernel_size=conv2.size(2)).squeeze(2)
        max3 = F.max_pool1d(conv3, kernel_size=conv3.size(2)).squeeze(2)

        combined = torch.cat((max1, max2, max3), dim=-1)
        combined = F.relu(combined)
        combined = F.dropout(combined)

        out = self.dense_layer(combined)
        out = F.relu(out)
        out = F.dropout(out)
        out = self.out_layer(out)

        return out
