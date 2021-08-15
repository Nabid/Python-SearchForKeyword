from http.client import NotConnected
from helper.WriteFile import WriteCsv
import helper.ReadFile as FileHelper
import helper.Logger as Logger
import helper.Config as Config
import copy, re, csv
from pathlib import Path
import urllib.request
from bs4 import BeautifulSoup

if __name__ == "__main__":
    Logger = Logger.Logger()
    ReadConfig = Config.ReadConfig()
    platform_dict = copy.deepcopy(ReadConfig.dict_platforms)
    platform_map = copy.deepcopy(ReadConfig.dict_platform_mapping)
    reportPath = Path("./report.txt").absolute()
    mappingPath = Path("./mapping.csv").absolute()
    print(reportPath)
    directory = './os_techniques'

    techniques = []
    line_pattern = 'revoked = True -> deprecated = None'
    pattern = '<(T[.|\d]*)>'

    with open(reportPath, 'r') as reportfile:
        # breakCount = 0
        for line in reportfile:
            # breakCount = breakCount + 1
            # if breakCount == 10:
            #     break
            if line_pattern in line:
                try:
                    oldKey = re.search(pattern, line).group(1)
                except:
                    Logger.info(f'no match in line: {line}')
                    continue

                url = line.split('=')[3]
                url = url.replace(' ', '')
                url = url.replace('\n', '')
                # send http request
                Logger.info(f'reading url <{url}> ...')
                with urllib.request.urlopen(url) as resp:
                    Logger.info(f'received response')
                    resp_read = resp.read().decode("utf-8")

                # parse new kew from response
                tmp = resp_read.replace('/', '.')
                newKey = re.search('(T[.|\d]*)', tmp).group(1)
                technique = [oldKey, newKey]

                # parse the new url
                tmp = re.search('(\/techniques\/\D\d{4}[\/|\d]*)', resp_read).group(1)
                newurl = f'https://attack.mitre.org{tmp}'
                Logger.info(f'reading url <{newurl}> ...')
                with urllib.request.urlopen(newurl) as newresp:
                    Logger.info(f'received response')
                    newhtml = newresp.read()
                    html = newhtml.decode("utf8")

                soup = BeautifulSoup(html, "html.parser")
                # find correcponding platform
                cards = soup.find_all("div", class_="row card-data")
                for card in cards:
                    text = card.get_text()
                    if not 'Platforms' in text:
                        continue
                    text = text.replace('\n', '')
                    break

                for platform in ReadConfig.platforms:
                    if platform in text:
                        technique.append(platform)
                #find corresponding description
                description = ''
                breadcrumbs = soup.find_all("li", class_="breadcrumb-item")
                description = breadcrumbs[len(breadcrumbs)-1].text.strip()
                technique.append(description)

                techniques.append(technique)

    #now write it in mapping.csv
    writeMap = WriteCsv(mappingPath, 'w+')
    writeMap.writeRow(["Old Technique", 'New Technique', 'Platform', 'Description of the new technique'], techniques)

    # finally appennd new mapped techniques the os_techniques.csv files 
    for platform in ReadConfig.platforms:
        data = []
        for obj in techniques:
            if platform in obj:
                data.append( [obj[1], obj[len(obj)-1]] ) # new technique and description (last index)

        filename = f'{directory}/{platform}_techniques.csv'
        wf = WriteCsv(filename, 'a')
        wf.writeRow(None, data)

        