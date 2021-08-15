import csv, yaml, json
import os

class ReadFile:
    def __init__(self, file_name, file_type):
        self.file_name = file_name
        self.file_type = file_type

    def isValidFile(self, file_name, file_type):
        if file_type == "csv":
            ret = os.path.isfile(file_name) and file_name.endswith(".csv")
            return ret
        elif file_type == "json":
            ret = os.path.isfile(file_name) and file_name.endswith(".json")
            return ret
        else:
            return False

    def read(self):
        if not self.isValidFile(self.file_name, self.file_type):
            return None

        with open(self.file_name, 'r') as file:
            if self.file_type == "csv":
                data_list = []
                reader = csv.reader(file)
                for row in reader:
                    data_list.append(row)
                return data_list
            elif self.file_type == "json":
                try:
                    data_dictionary = json.loads(file.read())
                except json.JSONDecodeError as exc:
                    print(f'[ERROR in JSON Decode] {exc}')
                return data_dictionary

    def getColumn(self, column):
        if not self.isValidFile(self.file_name, "csv"):
            return None
        col_data =[]
        with open(self.file_name, 'r') as file:
            reader = csv.reader(file)
            col_data = [row[column] for row in reader]
            #if ReadConfig.contains_header:
            col_data.pop(0)
        return col_data
        