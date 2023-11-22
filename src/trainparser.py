import csv


class TrainParser:
    def __init__(self, filepath):
        self.columns = 15
        self.train = []

        with open(filepath, "r") as csvfile:
            reader = csv.reader(csvfile)

            next(reader)

            for row in reader:
                self.train.append(row)
