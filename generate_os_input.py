from http.client import NotConnected
from logging import NullHandler
from helper.WriteFile import WriteCsv
import helper.ReadFile as FileHelper
import helper.Logger as Logger
import helper.Config as Config
import copy
from pathlib import Path

if __name__ == "__main__":
    Logger = Logger.Logger()
    ReadConfig = Config.ReadConfig()
    platform_dict = copy.deepcopy(ReadConfig.dict_platforms)
    platform_map = copy.deepcopy(ReadConfig.dict_platform_mapping)
    reportPath = Path("./report.txt").absolute()
    print(reportPath)
    directory = './os_techniques'

    jsonFileReader = FileHelper.ReadFile(f"{directory}/enterprise-attack.json", "json")
    data = jsonFileReader.read()
    objects = data["objects"]

    # parse enterprise-attach.json
    for object in objects:
        technique = None
        description = ''
        revokedUrl = None

        isFound = False
        try:
            for refs in object['external_references']:
                if isFound:
                    break

                for key in refs:
                    if key == "external_id":
                        isFound = True
                        technique = refs['external_id']

                        if not technique.startswith('T'):
                            technique = None
                            raise ValueError

                        revokedUrl = refs['url']
                        break
        except ValueError as v:
            Logger.error(f'Ignoring key not starting with < T >')
            continue
        except:
            Logger.error(f"No key <external_references> found, skipping...")
            continue

        if not technique:
            Logger.info("No technique found!")
            continue

        # get the technique description
        try:
            description = object['name']
        except:
            Logger.error(f"No description found for key <{technique}>")

        try:
            os_array = object['x_mitre_platforms']
        except:
            isRevoked = None
            isDeprecated = None
            try:
                isRevoked = object['revoked']
            except:
                isRevoked = None

            try:
                isDeprecated = object['x_mitre_deprecated']
            except:
                isDeprecated = None

            msg = f"No x_mitre_platforms found for <{technique}> -> revoked = {isRevoked} -> deprecated = {isDeprecated} -> url = {revokedUrl}"
            Logger.info(msg, True, reportPath)
            continue

        for os in os_array:
            try:
                platform_dict[os.lower()].append([technique, description])
            except KeyError as k:
                Logger.info(f'Platform <{os}> does not exist Config, adding <{os}> in dictionary')
                platform_dict[os.lower()] = []
                platform_dict[os.lower()].append([technique, description])
                platform_map[os.lower()] = os

    # write new csv files
    for platform in platform_dict:
        if not len(platform_dict[platform]):
            Logger.info(f'No technique for OS <{platform}>')
            continue

        filename = f'{directory}/{platform_map[platform]}_techniques.csv'
        wf = WriteCsv(file_name=filename, mode='w+')

        wf.writeFile(file_header=['TID', 'Description of the technique' , 'Ignore'], file_data=platform_dict[platform], delimiter=',')