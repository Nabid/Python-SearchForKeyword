import csv, yaml, json
import os, re, copy
import helper.Logger as Logger
import helper.Config as Config
from helper.FileHelper import FileHelper, FileExtention

class SearchForKeywords:
    os_based_techniques = {}
    ignore_techniques = {}
    found_indexes = []

    # def update_found_indexes():

    def validate_found_key(self, key, platform, parsed_type, list_keywords):
        ### bypass of key checking in in.csv
        isKeywordValidated = True if ReadConfig.bypass_keyword_check == 'True' or key in list_keywords else False

        # check ignored list
        if key in self.ignore_techniques[platform] and self.ignore_techniques[platform][key] == 'Yes' and ReadConfig.count_ignore == 'False':
            Logger.info(f'key <{key}> found in ignored list for <{ReadConfig.dict_platform_mapping[platform]}>...')
            return

        isKeyFoundInListKeywords = False
        if isKeywordValidated:
            if ReadConfig.subtechnique_switch == 'True':
                # add it in the os categorized list anyway
                self.os_based_techniques[platform][key] = 'No'

                # do not need to match whole key
                # if part of it matches like:
                # if T1110 in T1110.003 then do
                for key_in_list in list_keywords:
                    if key in key_in_list:
                        idx = list_keywords.index(key_in_list)
                        self.found_indexes[idx] = True
                        isKeyFoundInListKeywords = True
                        self.update_platform_based_techniques(platform, key, True, True)
                if (not isKeyFoundInListKeywords) and key in self.os_based_techniques[platform]:
                    list_keywords.append(key)
                    self.found_indexes.append(True)
                    isKeyFoundInListKeywords = True
                    self.update_platform_based_techniques(platform, key, True, True)
            else:
                if key in list_keywords:
                    ### Save in list for csv output
                    idx = list_keywords.index(key)
                    self.found_indexes[idx] = True
                    isKeyFoundInListKeywords = True
                # else:
                #     list_keywords.append(key)
                #     idx = list_keywords.index(key)
                #     self.found_indexes[idx] = True
                #     isKeyFoundInListKeywords = True
                self.update_platform_based_techniques(platform, key, isKeyFoundInListKeywords, False)
            ### Save in dictionary
            ReadConfig.dict_platforms[platform].append((key, parsed_type.lower()))

    def search_in_yaml(self, list_keywords):
        for search_path in ReadConfig.search_paths:
            if not search_path: # if the path is empty
                continue
            try:
                files = os.listdir(search_path)
            except FileNotFoundError:
                Logger.error(f'Search directory not founnd: <{search_path}>')
                continue
            except NotADirectoryError:
                Logger.error(f'Not a directory: <{search_path}>')
                continue

            for search_file in files:
                search_file_path = os.path.join(search_path, search_file)
                if FileHelper.isValidFile(search_file_path, FileExtention.YAML):
                    with open(search_file_path, 'r') as file:
                        try:
                            data = yaml.safe_load(file)
                            try:
                                if "tags" in data:
                                    tags = data["tags"]
                                elif "hive_alert_config" in data:
                                    tags = data["hive_alert_config"]["tags"]
                                else:
                                    raise KeyError
                            except KeyError:
                                Logger.error(f'[KeyError] <tags> not found in file <{file.name}>')
                                continue

                            regex = re.compile(f'{ReadConfig.key_prefix}' + 'T\d{4,4}(\.\d{3,3})?')
                            t = list(filter(regex.match, tags))
                            
                            if not len(t): # list contains key
                                continue
                            for k in t:
                                key = k.split(':')[1]                                

                                match_platform = [x for x in ReadConfig.dict_platforms.keys() if x in list(map(str.lower, tags))]
                                if not len(match_platform):
                                    ### tags does not contain any of valid platforms
                                    Logger.error(f'[WARNING] No valid platform was found in <{file.name}>')
                                    continue

                                platform = match_platform[0]
                                type = data["hive_alert_config"]["type"]
                                parsed_type = type if ReadConfig.key_prefix not in type else type.split(ReadConfig.key_prefix)[1]

                                self.validate_found_key(key, platform, parsed_type, list_keywords)
                        except yaml.YAMLError as exc:
                            Logger.error(f'[ERROR] {exc}')
                else: 
                    ReadConfig.search_paths.append(search_file_path)
        # include ignored keys if count_ignore is true
        if ReadConfig.count_ignore == 'True':
            for platform in self.ignore_techniques:
                keys = dict(filter(lambda e:e[1] == 'Yes', self.ignore_techniques[platform].items()))
                # now add all ignores into found
                for k,v in keys.items():
                    self.os_based_techniques[platform][k] = 'Found'
                    if k in list_keywords:
                        idx = list_keywords.index(k)
                        self.found_indexes[idx] = True
                    else:
                        list_keywords.append(k)
                        self.found_indexes.append(True)
        return self.found_indexes

    def update_platform_based_techniques(self, platform, key, isKeyFoundInListKeywords, isSwitchIsOn = None):
        # get new mapping
        mapped_key = None
        with open("mapping.csv", 'r') as mappingFile:
            reader = csv.reader(mappingFile)
            for row in reader:
                if row[0] == key:
                    mapped_key = row[1]

        ### os based techniques
        if ReadConfig.enable_platform_based_techniques == 'True':
            if platform in self.os_based_techniques:
                if isSwitchIsOn:
                    # do not need to match whole key
                    # if part of it matches like:
                    # if T1110 in T1110.003 then do it is found
                    for key_in_list in self.os_based_techniques[platform]:
                        if key in key_in_list:
                            self.os_based_techniques[platform][key_in_list] = 'Found'
                        if mapped_key and mapped_key in key_in_list:
                            self.os_based_techniques[platform][key_in_list] = 'Found'
                elif key in self.os_based_techniques[platform]:
                    self.os_based_techniques[platform][key] = 'Found'
                elif isKeyFoundInListKeywords:
                    self.os_based_techniques[platform][key] = 'Found'
                else:
                    self.os_based_techniques[platform][key] = 'No'

    def get_keywords(self):
        list_keywords = []
        with open(ReadConfig.keyword_file, 'r') as file:
            reader = csv.reader(file)
            list_keywords = [row[0] for row in reader]
        return list_keywords

    def get_os_based_techniques(self):
        for platform in ReadConfig.platforms:
            # check if the OS_techniques.csv file exists
            lower_platform = platform.lower()
            if not lower_platform in ReadConfig.dict_platform_mapping:
                continue

            fileName = f'os_techniques/{ReadConfig.dict_platform_mapping[lower_platform]}_techniques.csv'
            if FileHelper.isValidFile(fileName, FileExtention.CSV):
                self.os_based_techniques[lower_platform] = {}
                self.ignore_techniques[lower_platform] = {}

                #read the Os_techniques.csv file
                list_keywords = []
                dict_ignores = {}

                with open(fileName, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        list_keywords.append(row[0])
                        if len(row) > 2 and (row[2] == 'ignore' or (row[2] == 'Ignore')):
                            dict_ignores[row[0]] = 'Yes'
                        else:
                            dict_ignores[row[0]] = 'No'

                if not len(list_keywords):
                    continue

                list_keywords.pop(0) # remove the header
                for technique in list_keywords:
                    self.os_based_techniques[lower_platform][technique] = 'No'
                    self.ignore_techniques[lower_platform][technique] = dict_ignores[technique]

    def write_result_in_file(self, filename, mode, fieldname, coldata):
        with open(filename, mode, newline='') as file:
            writer = csv.writer(file, dialect='excel')
            writer.writerow(fieldname)
            for row in coldata:
                writer.writerow(row)

    def write_result(self, list_keywords, found_indexes):
        rows = [(x, '' if not y else 'Found') for x,y in zip(list_keywords, found_indexes)]
        
        total_found = found_indexes.count(True)
        total_keywords = len(list_keywords)
        percentage = float(total_found)/float(total_keywords) * 100

        fieldNames = ['Keyword', 'isFound']
        self.write_result_in_file(ReadConfig.output_file, 'w+', fieldNames, rows)
        fieldNames = ["Total Keywords", "Keywords Found", "Percentage"]
        rows = [[total_keywords, total_found, "{:0.2f}".format(percentage)]]
        self.write_result_in_file(ReadConfig.output_file, 'a', fieldNames, rows)

        for platform in self.os_based_techniques:
            filename = f'{ReadConfig.platform_based_techniques_output_path}{ReadConfig.dict_platform_mapping[platform]}_techniques.csv'

            fieldNames = ['Keyword', 'isFound']
            total_keywords = len(self.os_based_techniques[platform])
            total_found = 0
            coldata = []

            for key, value in self.os_based_techniques[platform].items():
                coldata.append([key, value])
                if value == 'Found':
                    total_found += 1
            self.write_result_in_file(filename, 'w+', fieldNames, coldata)

            try:
                percentage = float(total_found)/float(total_keywords) * 100
            except ZeroDivisionError:
                percentage = 0.00
            fieldNames = ["Total Keywords", "Keywords Found", "Percentage"]
            rows = [[total_keywords, total_found, "{:0.2f}".format(percentage)]]
            self.write_result_in_file(filename, 'a', fieldNames, rows)

    def generate_platform_json_files(self):
         if FileHelper.isValidFile(ReadConfig.empty_layer_template, FileExtention.JSON):
             with open(ReadConfig.empty_layer_template, 'r') as template:
                try:
                    data = json.loads(template.read())
                except json.JSONDecodeError as exc:
                    Logger.error(f'[ERROR in JSON Decode] {exc}')

                for platform, list_keys in ReadConfig.dict_platforms.items():
                    if len(list_keys):
                        new_layer = copy.deepcopy(data)
                        for item in list_keys:
                            obj = {
                                "techniqueID": item[0],
                                "tactic": item[1],
                                "color": "#fcf3a2",
                                "comment": "",
                                "enabled": True,
                                "metadata": [],
                                "showSubtechniques": False
                            }
                            new_layer['techniques'].append(obj)
                        
                        new_layer['filters']['platforms'] = [ ReadConfig.dict_platform_mapping[platform] ]
                        ### Write platform json
                        with open(os.path.join(ReadConfig.layer_output_path, f'{platform}.json'), 'w+') as outfile:
                            json.dump(new_layer, outfile, indent=2)

    def show_terminal_output(self):
        total = sum( [len(i) for k, i in ReadConfig.dict_platforms.items()] )
        print('[AGAINST NET FOUND TECHNIQUES]--------------->')
        for k, i in ReadConfig.dict_platforms.items():
            if len(i):
                value = len(i)
                print("{:<40}".format(f"{ReadConfig.dict_platform_mapping[k]} - Enterprise coverage") + f":{float(value)/float(total)*100}%")
        print('[AGAINST CATEGORISED TECHNIQUES]------------->')
        for platform in self.os_based_techniques:
            total_keywords = len(self.os_based_techniques[platform])
            total_found = 0
            for key, value in self.os_based_techniques[platform].items():
                if value == 'Found':
                    total_found += 1

            if total_found == 0 or total_keywords == 0:
                continue

            percentage = "{:0.2f}".format(float(total_found)/float(total_keywords) * 100)
            print("{:<40}".format(f"{ReadConfig.dict_platform_mapping[platform]} - Enterprise coverage") + f":{percentage}%")
        print('----------------------------------------------')

    def run(self):
        list_keywords = self.get_keywords()
        if ReadConfig.keyword_file_has_header == 'True':
            list_keywords.pop(0)

        self.found_indexes = [False] * len(list_keywords)
        self.get_os_based_techniques()

        found_indexes = self.search_in_yaml(list_keywords=list_keywords)
        self.write_result(list_keywords=list_keywords, found_indexes=found_indexes)
        self.generate_platform_json_files()
        self.show_terminal_output()

if __name__ == "__main__":
    Logger = Logger.Logger()
    ReadConfig = Config.ReadConfig()
    s = SearchForKeywords()
    s.run()
