# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: main.py

@time: 18-10-23

@desc:


"""
from torch.utils.data import DataLoader
from text_cnn import TextCNN
from data_importer import QuestionType
import torch.optim as optim
import torch
import time
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '1'
log_interval = 50


def train(epoch, data, model, op, criterion):
    total_loss = 0.
    total_correct = 0.
    batches = len(data)

    for index, sample in enumerate(data):
        model.zero_grad()

        sources, targets = sample
        sources, targets = sources.cuda(), targets.cuda()

        out = model(sources)
        loss = criterion(out, targets.squeeze())

        if index % log_interval == 0:
            print('Epoch:{0}-{1}/{2}, Batch Loss:{3}'.format(epoch, index, batches, loss.item() / sources.size(0)))

        loss.backward()
        total_loss += loss.item()
        total_correct += (targets.squeeze() == out.argmax(1)).sum().item()
        op.step()

    return total_loss, total_correct

if __name__ == '__main__':
    epochs = 2
    hidden_dim = 300

    dataset = QuestionType()
    data_loader = DataLoader(dataset, batch_size=64, shuffle=True)

    model = TextCNN(len(dataset.word2idx), hidden_dim, 100, len(dataset.cat2idx)).cuda()
    optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)
    criterion = torch.nn.CrossEntropyLoss()

    start = time.time()
    for epoch in range(1, epochs + 1):
        loss, correct_num = train(epoch, data_loader, model, optimizer, criterion)
        print('Epoch:{0}, Loss:{1}, Precision:{2}, Elapsed-time:{3}'.format(epoch,
                                                                            loss / len(dataset),
                                                                            correct_num / len(dataset),
                                                                            round(time.time() - start, 2)))
        print('#' * 100)

    torch.save(model, './check_point/model.pkl')