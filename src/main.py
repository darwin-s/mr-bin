import sys

import globalsolver


def main():
    solver = globalsolver.GlobalSolver(sys.argv[2], sys.argv[3])
    tree = solver.generatetrees()


if __name__ == "__main__":
    argc = len(sys.argv)

    if argc < 3:
        print("Usage: main.py FM_CSV LUT_CSV")
        exit(-1)

    main()
