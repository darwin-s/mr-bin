import fmparser
import trainparser

from itertools import combinations
import operator

class GlobalSolver:
    def __init__(self, trainfile, lutfile):
        self.trainparser = trainparser.TrainParser(trainfile)
        self.lutparser = fmparser.FmParser(lutfile)
        self.operations = {
            "+": operator.add,
            "-": operator.sub,
            "/": operator.truediv,
            "*": operator.mul
        }

    def generatecombinations(self):
        combs = []
        add_list = ["+", "+", "+", "+"]
        sub_list = ["-", "-", "-", "-"]
        div_list = ["/", "/", "/", "/"]
        mul_list = ["*", "*", "*", "*"]

        op_list = add_list + sub_list + div_list + mul_list

        combinations1 = list(set(list(combinations(op_list, 4))))
        combinations2 = list(set(list(combinations(op_list, 4))))
        combinations3 = list(set(list(combinations(op_list, 4))))
        combinations4 = list(set(list(combinations(op_list, 2))))

        for c1 in combinations1:
            for c2 in combinations2:
                for c3 in combinations3:
                    for c4 in combinations4:
                        full_op = c1 + c2 + c3 + c4
                        nr_add = full_op.count("+")
                        nr_sub = full_op.count("-")
                        nr_div = full_op.count("/")
                        nr_mul = full_op.count("*")

                        if nr_add == nr_sub and nr_div == nr_mul:
                            combs.append(full_op)

        return combs

    def generatetrees(self):
        combinations = self.generatecombinations()


