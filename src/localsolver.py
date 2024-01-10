import ctypes
import math
import multiprocessing
import os
import statistics
import sys
import time
import csv

import progress.bar

import fmparser
import trainparser

from itertools import combinations
from multiprocessing import Pool
import operator
import json


def op_max(x, y):
    return max(x, y)


def op_min(x, y):
    return min(x, y)


def op_abs(x, y):
    return abs(x - y)


class CSVFile:
    def __init__(self):
        self.thresholdings = []
        self.pixel_class = []

    def read(self, file):
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')

            for row in reader:
                self.thresholdings.append(row[2:])
                self.pixel_class.append(row[1])


class LocalSolver:
    def __init__(self, trainfile):
        self.trainfile = trainfile
        self.operations = {
            "M": op_max,
            "m": op_min,
            "a": op_abs,
            "*": operator.mul
        }

    def generatecombinations(self):
        combs = []
        max_list = ["M", "M", "M"]
        min_list = ["m", "m", "m"]
        abs_list = ["a", "a", "a"]
        mul_list = ["*", "*", "*"]

        op_list = max_list + min_list + abs_list + mul_list

        combinations1 = list(set(list(combinations(op_list, 3))))
        combinations2 = list(set(list(combinations(op_list, 3))))
        combinations3 = list(set(list(combinations(op_list, 3))))

        for c1 in combinations1:
            for c2 in combinations2:
                for c3 in combinations3:
                    full_op = c1 + c2 + c3
                    combs.append(full_op)

        return combs

    def generatetrees(self):
        combs = self.generatecombinations()
        bestaccuracy = None
        bestcomb = None
        dir_list = os.listdir(self.trainfile)

        try:
            with progress.bar.Bar("Training ", max=len(combs)) as bar:
                for comb in combs:
                    fms = []
                    bar.bar_prefix = str(comb)
                    for train_file in dir_list:
                        csv_file = CSVFile()
                        csv_file.read(self.trainfile + '/' + train_file)
                        fp = 0.0
                        fn = 0.0
                        tp = 0.0
                        tn = 0.0

                        for i in range(len(csv_file.thresholdings)):
                            pixel_class = csv_file.pixel_class[i]
                            res = float(csv_file.thresholdings[i][0])

                            for j in range(1, len(csv_file.thresholdings[i])):
                                res = self.operations[comb[j - 1]](res, float(csv_file.thresholdings[i][j]))

                            if 0.0 <= res < 0.5:
                                if int(pixel_class) == 0:
                                    tn += 1.0
                                else:
                                    fn += 1.0
                            elif 0.5 <= res <= 1.0:
                                if int(pixel_class) == 1:
                                    tp += 1.0
                                else:
                                    fp += 1.0

                        fm = tp / (tp + 0.5 * (fp + fn))
                        fms.append(fm)

                    avg = statistics.fmean(fms)
                    if bestaccuracy is None:
                        print(f"New best accuracy: {avg}")
                        bestaccuracy = avg
                        bestcomb = comb
                    elif avg > bestaccuracy:
                        print(f"New best accuracy: {avg}")
                        bestaccuracy = avg
                        bestcomb = comb

                    bar.next()
        except KeyboardInterrupt:
            dump = {
                "".join([bestcomb[i] for i in range(0, len(bestcomb))]): bestaccuracy
            }
            jsonobj = json.dumps(dump)
            with open("train_local.json", "w") as outf:
                outf.write(jsonobj)
            print("Saved current best tree")
            exit(0)

        dump = {
            str(bestcomb): bestaccuracy
        }
        jsonobj = json.dumps(dump)
        with open("train_local.json", "w") as outf:
            outf.write(jsonobj)

    def testtree(self, treePath):
        jsonObj = None
        with open(treePath, "r") as inf:
            jsonObj = json.load(inf)

        comb = list(jsonObj.keys())[0]
        init_acc = jsonObj[comb]

        dir_list = os.listdir(self.trainfile)
        fms = []
        for train_file in dir_list:
            csv_file = CSVFile()
            csv_file.read(self.trainfile + '/' + train_file)
            fp = 0.0
            fn = 0.0
            tp = 0.0
            tn = 0.0

            for i in range(len(csv_file.thresholdings)):
                pixel_class = csv_file.pixel_class[i]
                res = float(csv_file.thresholdings[i][0])

                for j in range(1, len(csv_file.thresholdings[i])):
                    res = self.operations[comb[j - 1]](res, float(csv_file.thresholdings[i][j]))

                if 0.0 <= res < 0.5:
                    if int(pixel_class) == 0:
                        tn += 1.0
                    else:
                        fn += 1.0
                elif 0.5 <= res <= 1.0:
                    if int(pixel_class) == 1:
                        tp += 1.0
                    else:
                        fp += 1.0

            fm = tp / (tp + 0.5 * (fp + fn))
            fms.append(fm)

        avg = statistics.fmean(fms)
        dump = {
            "tree": str(comb),
            "initialAccuracy": init_acc,
            "factualAccuracy": avg
        }
        jsonobj = json.dumps(dump)
        with open("test_local.json", "w") as outf:
            outf.write(jsonobj)
