import sys

import globalsolver
import localsolver


def main(local, test):
    if not local:
        if not test:
            solver = globalsolver.GlobalSolver(sys.argv[1], sys.argv[2])
            solver.generatetrees()
        else:
            solver = globalsolver.GlobalSolver(sys.argv[2], sys.argv[3])
            solver.testtree("train.json")
    else:
        if not test:
            solver = localsolver.LocalSolver(sys.argv[2])
            solver.generatetrees()
        else:
            solver = localsolver.LocalSolver(sys.argv[3])
            solver.testtree("train_local.json")


if __name__ == "__main__":
    argc = len(sys.argv)

    if argc < 3:
        print("Usage: main.py [local] [test] FM_CSV LUT_CSV")
        print("    if test is specified then the program is ran in test mode")
        exit(-1)

    if sys.argv[1] == "local":
        if sys.argv[2] == "test":
            main(True, True)
        else:
            main(True, False)
    else:
        if sys.argv[1] == "test":
            main(False, True)
        else:
            main(False, False)
