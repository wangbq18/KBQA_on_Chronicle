#encoding=utf-8
import pandas as pd
import chardet
import re
import torch

a = torch.LongTensor([[1]*64])
print(a.size())