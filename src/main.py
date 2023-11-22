import sys

import globalsolver


def main(test):
    if not test:
        solver = globalsolver.GlobalSolver(sys.argv[1], sys.argv[2])
        solver.generatetrees()
    else:
        solver = globalsolver.GlobalSolver(sys.argv[2], sys.argv[3])
        solver.testtree("train.json")


if __name__ == "__main__":
    argc = len(sys.argv)

    if argc < 3:
        print("Usage: main.py [test] FM_CSV LUT_CSV")
        print("    if test is specified then the program is ran in test mode")
        exit(-1)

    if sys.argv[1] == "test":
        main(True)
    else:
        main(False)
