import csv, yaml, json
from xxlimited import Null
import os

class WriteCsv:
    def __init__(self, file_name, mode):
        self.file_name = file_name
        self.mode = mode

    def writeColumn(self, read_file, col_data):
        with open(read_file, "r") as reader_file, \
        open(self.file_name, self.mode) as writer_file:
            reader = csv.reader(reader_file)
            writer = csv.writer(writer_file, delimiter=";")
            for i, row in enumerate(reader):

                if type(col_data[i]) == str:
                    row.append(col_data[i])
                elif type(col_data[i]) == list:
                    for data in col_data[i] : row.append(data)

                writer.writerow(row)

    def writeFile(self, file_header = None, file_data = [], delimiter = ",", dialect='excel'):
        try:
            with open(self.file_name, self.mode, newline='') as writer_file:
                writer = csv.writer(writer_file, delimiter=delimiter, dialect=dialect)
                
                if file_header:
                    writer.writerow(file_header)
                if len(file_data):
                    writer.writerows(file_data)
        except Exception as e:
            print(f'[ERROR] {e}')

    ###
    ###   file_data = [ [row], [row] ]
    ###
    def writeRow(self, file_header = None, file_data = [], delimiter = ",", dialect='excel'):
        try:
            with open(self.file_name, self.mode, newline='') as writer_file:
                writer = csv.writer(writer_file, delimiter=delimiter, dialect=dialect)
                
                if file_header:
                    writer.writerow(file_header)
                if len(file_data):
                    for row in file_data:
                        writer.writerow(row)
        except Exception as e:
            print(f'[ERROR] {e}')