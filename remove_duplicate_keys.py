import csv
import helper.Logger as Logger
import helper.Config as Config
from helper.FileHelper import FileHelper, FileExtention

if __name__ == "__main__":
    Logger = Logger.Logger()
    ReadConfig = Config.ReadConfig()

    for platform in ReadConfig.platforms:
        # check if the OS_techniques.csv file exists
        lower_platform = platform.lower()
        if not lower_platform in ReadConfig.dict_platform_mapping:
            continue

        fileName = f'os_techniques/{ReadConfig.dict_platform_mapping[lower_platform]}_techniques.csv'
        if FileHelper.isValidFile(fileName, FileExtention.CSV):
            #read the Os_techniques.csv file
            list_keywords = []

            with open(fileName, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    try:
                        list_keywords.append([row[0], row[1]])
                    except:
                        Logger.error(f'invalid row found <{row}>, coneinue...')
                        continue
            
            list_keywords.pop(0) # drop the header
            with open(fileName, 'w') as file:
                writer = csv.writer(file, delimiter=',', dialect='excel')
                writer.writerow(['TID', 'Description of the technique' , 'Ignore'])
                written_keys = []
                for obj in list_keywords:
                    if obj[0] in written_keys:
                        continue
                    writer.writerow(obj)
                    written_keys.append(obj[0])