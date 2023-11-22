import csv


class FmParser:
    def __init__(self, filepath):
        self.columns = 256
        self.fm = []

        with open(filepath, "r") as csvfile:
            reader = csv.reader(csvfile)

            next(reader)

            for row in reader:
                self.fm.append(row)
