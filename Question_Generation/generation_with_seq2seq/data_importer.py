# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: data_importer.py

@time: 8/14/18

@desc:

"""

from torch.utils.data import Dataset
import pymongo


class TripleQuestion(Dataset):
    def __init__(self):
        # TODO connect to mongodb and fetch triple and question
        connection = pymongo.MongoClient()
        db = connection['chronicle_training_data']
        collection = db['pattern_auto_generated_data']
        for i in collection.find():
            print i

    def __getitem__(self, index):
        pass

    def __len__(self):
        pass

t = TripleQuestion()