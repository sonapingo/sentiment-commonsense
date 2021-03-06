# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from torch.utils.data import Dataset, DataLoader

from core.data.dataset_readers.sst import sst_binary_loader, sst_fine_loader


class TextData(Dataset):
    def __init__(self, xy):
        self.xs, self.lens, self.ys, self.tags = xy

    def __getitem__(self, index):
        x = self.xs[index]
        x_len = self.lens[index]
        y = self.ys[index]
        tag = self.tags[index]

        return x, x_len, y, tag

    def __len__(self):
        return len(self.ys)


class DataContainer:
    def __init__(self,
                 vocabulary,
                 sentiment_lexicon,
                 root_dir="../../",
                 data_dir="../../../senteval",
                 data_name="sst.binary"):

        self.root_dir = root_dir
        self.data_dir = data_dir
        self.data_name = data_name

        max_len = 50  # 56
        batch_size = 50

        train_file = self.data_dir + "/{}.train".format(data_name)
        valid_file = self.data_dir + "/{}.dev".format(data_name)
        test_file = self.data_dir + "/{}.test".format(data_name)

        def preprocess(sentence):
            s = sentence.replace(" -lrb- ", " ( ").replace(" -rrb- ", " ) ").replace("-", " ")
            return " ".join(s.split())

        if "binary" in data_name:
            sst_loader = sst_binary_loader
        elif "fine" in data_name:
            sst_loader = sst_fine_loader
        else:
            raise ValueError("no such data: %s" % data_name)

        def wrap_data(in_file):
            instances, labels = sst_loader(in_file, preprocess)
            x = []
            lens = []
            tags = []

            for sentence in instances:
                s_ids, s_len = vocabulary.encode(sentence, max_len)
                if s_len == 0:
                    print("s_len == 0 !!!! ==> %s" % sentence)
                t_ids, _ = sentiment_lexicon.encode(sentence, max_len)
                x.append(s_ids)
                lens.append(s_len)
                tags.append(t_ids)

            x = np.array(x, dtype=np.int64)
            lens = np.array(lens, dtype=np.int64)
            y = np.array(labels, dtype=np.int64)
            tags = np.array(tags, dtype=np.int64)
            return TextData([x, lens, y, tags])

        self.train = wrap_data(train_file)
        self.valid = wrap_data(valid_file)
        self.test = wrap_data(test_file)
        self.train_loader = DataLoader(dataset=self.train, batch_size=batch_size, shuffle=True)
        self.valid_loader = DataLoader(dataset=self.valid, batch_size=100)
        self.test_loader = DataLoader(dataset=self.test, batch_size=100)
