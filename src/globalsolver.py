import ctypes
import math
import multiprocessing
import statistics
import sys
import time

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


class GlobalSolver:
    def __init__(self, trainfile, lutfile):
        self.trainparser = trainparser.TrainParser(trainfile)
        self.lutparser = fmparser.FmParser(lutfile)
        self.operations = {
            "M": op_max,
            "m": op_min,
            "a": op_abs,
            "*": operator.mul
        }

    def generatecombinations(self):
        combs = []
        max_list = ["M", "M", "M", "M"]
        min_list = ["m", "m", "m", "m"]
        abs_list = ["a", "a", "a", "a"]
        mul_list = ["*", "*", "*", "*"]

        op_list = max_list + min_list + abs_list + mul_list

        combinations1 = list(set(list(combinations(op_list, 4))))
        combinations2 = list(set(list(combinations(op_list, 4))))
        combinations3 = list(set(list(combinations(op_list, 4))))
        combinations4 = list(set(list(combinations(op_list, 2))))

        for c1 in combinations1:
            for c2 in combinations2:
                for c3 in combinations3:
                    for c4 in combinations4:
                        full_op = c1 + c2 + c3 + c4
                        combs.append(full_op)

        return combs

    def generatetrees(self):
        combs = self.generatecombinations()
        bestaccuracy = None
        bestcomb = None

        try:
            with progress.bar.Bar("Training ", max=len(combs)) as bar:
                for comb in combs:
                    bar.bar_prefix = str(comb)
                    accs = []
                    skip = False
                    for i in range(len(self.trainparser.train)):
                        img = self.trainparser.train[i]
                        res = float(img[0])

                        for j in range(1, len(img)):
                            res = self.operations[comb[j - 1]](res, float(img[j]))

                        if 0 <= res <= 1:
                            idx = math.floor(res * 255)
                            accs.append(float(self.lutparser.fm[i][idx]))
                        else:
                            skip = True
                            break

                    if skip:
                        bar.next()
                        continue

                    avg = statistics.fmean(accs)
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
            with open("train.json", "w") as outf:
                outf.write(jsonobj)
            print("Saved current best tree")
            exit(0)

        dump = {
            str(bestcomb): bestaccuracy
        }
        jsonobj = json.dumps(dump)
        with open("train.json", "w") as outf:
            outf.write(jsonobj)

    def testtree(self, treePath):
        jsonObj = None
        with open(treePath, "r") as inf:
            jsonObj = json.load(inf)

        comb = list(jsonObj.keys())[0]
        init_acc = jsonObj[comb]

        accs = []
        for i in range(len(self.trainparser.train)):
            img = self.trainparser.train[i]
            res = float(img[0])

            for j in range(1, len(img)):
                res = self.operations[comb[j - 1]](res, float(img[j]))

            idx = math.floor(res * 255)
            accs.append(float(self.lutparser.fm[i][idx]))

        avg = statistics.fmean(accs)
        dump = {
            "tree": str(comb),
            "initialAccuracy": init_acc,
            "factualAccuracy": avg
        }
        jsonobj = json.dumps(dump)
        with open("test.json", "w") as outf:
            outf.write(jsonobj)
