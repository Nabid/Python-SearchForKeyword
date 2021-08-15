from enum import Enum
import os

class FileExtention(str, Enum):
    YAML = "yaml"
    YML = "yml"
    CSV = "csv"
    JSON = "json"

class FileHelper:
    @staticmethod
    def isValidFile(file_name, file_type):
        if file_type == FileExtention.YAML:
            ret = os.path.isfile(file_name) and (file_name.endswith(FileExtention.YAML) or file_name.endswith(FileExtention.YML))
            return ret
        elif file_type == FileExtention.JSON:
            ret = os.path.isfile(file_name) and file_name.endswith(FileExtention.JSON)
            return ret
        elif file_type == FileExtention.CSV:
            ret = os.path.isfile(file_name) and file_name.endswith(FileExtention.CSV)
            return ret