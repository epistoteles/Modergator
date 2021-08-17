from hm import HM

import collections
import os
import sys

from param import args

import numpy as np

from tqdm import tqdm
import torch
import torch.nn as nn
from torch.utils.data.dataloader import DataLoader

if args.tsv:
    from fts_tsv.hm_data_tsv import HMTorchDataset, HMEvaluator, HMDataset
else:
    from fts_lmdb.hm_data import HMTorchDataset, HMEvaluator, HMDataset

from src.vilio.transformers.optimization import AdamW, get_linear_schedule_with_warmup
from utils.pandas_scripts import clean_data

from entryU import ModelU


DataTuple = collections.namedtuple("DataTuple", 'dataset loader evaluator')


def get_tuple(splits: str, bs: int, shuffle=False, drop_last=False) -> DataTuple:

    dset = HMDataset(splits)

    tset = HMTorchDataset(splits)
    evaluator = HMEvaluator(tset)
    data_loader = DataLoader(
        tset, batch_size=bs,
        shuffle=shuffle, num_workers=args.num_workers,
        drop_last=drop_last, pin_memory=True
    )
    return DataTuple(dataset=dset, loader=data_loader, evaluator=evaluator)


def main():
    # Build Class
    print("build class")
    hm = HM()
    return_value = 0
    for split in args.test.split(","):
        # Anthing that has no labels:
        if 'test' in split: 
            id2ans, id2prob = hm.predict(
                get_tuple(split, bs=args.batch_size,
                          shuffle=False, drop_last=False),
                dump=os.path.join(
                    args.output, '{}_{}.csv'.format(args.exp, split))
            )
            return_value = list(id2prob.values())[0]
    print(return_value)
   


main()
