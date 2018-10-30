# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: main.py

@time: 18-10-16

@desc:


"""
from torch.utils.data import DataLoader
from bilstm_crf import BiLSTM_CRF
from data_importer import QuestionTag
import torch.optim as optim
import torch
import time
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '1'
log_interval = 50


def train(epoch, data, model, op):
    total_loss = 0.
    batches = len(data)

    for index, sample in enumerate(data):
        model.zero_grad()

        sources, targets = sample
        sources = sources.view(-1, 1)
        targets = targets.view(-1, 1)
        sources, targets = sources.cuda(), targets.cuda()

        loss = model.neg_log_likelihood(sources, targets)

        if index % log_interval == 0:
            print('Epoch:{0}-{1}/{2}, Batch Loss:{3}'.format(epoch, index, batches, loss.item() / sources.size(0)))

        loss.backward()
        total_loss += loss.item()
        op.step()

    return total_loss

if __name__ == '__main__':
    epochs = 1
    embedding_dim = hidden_dim = 300

    dataset = QuestionTag()
    data_loader = DataLoader(dataset, batch_size=1, shuffle=True)

    model = BiLSTM_CRF(len(dataset.word2idx), dataset.tag2idx, embedding_dim, hidden_dim).cuda()
    optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)

    start = time.time()
    for epoch in range(1, epochs + 1):
        loss = train(epoch, data_loader, model, optimizer)
        print('Epoch:{0}, Loss:{1}, Elapsed-time:{2}'.format(epoch, loss / len(dataset), round(time.time() - start, 2)))
        print('#' * 100)

    torch.save(model, './check_point/model.pkl')