import configparser as cs
from pathlib import Path

class ReadConfig:
    search_paths = ''
    keyword_file = ''
    keyword_file_has_header = True
    output_file = ''
    platforms = [str]
    dict_platforms = {str : list}
    dict_platform_mapping = {str : str}
    key_prefix = ''
    empty_layer_template = ''
    layer_output_path = ''
    bypass_keyword_check = False
    enable_platform_based_techniques = False
    subtechnique_switch = True
    ignore_techniques = []
    count_ignore = True

    def __init__(self):
        filename = Path("config/config.cfg")

        configParser = cs.RawConfigParser()
        configParser.read(rf'{filename}')

        ### Search path
        path_separator = configParser.get('search-path-list', 'separator')
        ReadConfig.search_paths = configParser.get('search-path-list', 'path').split(path_separator)
        ### Keywords file
        ReadConfig.keyword_file = configParser.get('keyword-file', 'keyword_file_path')
        ReadConfig.keyword_file_has_header = configParser.get('keyword-file', 'keyword_file_has_header')
        ### Output file
        ReadConfig.output_file = configParser.get('keyword-file', 'output_file_path')
        ### Platforms
        platform_separator = configParser.get('platforms', 'separator')
        #ReadConfig.platforms = list(map(str.lower, configParser.get('platforms', 'platforms').split(platform_separator)))
        ReadConfig.platforms = configParser.get('platforms', 'platforms').split(platform_separator)
        ### Dictionary of platforms <platform: []>
        ReadConfig.dict_platforms = {k.lower():[] for k in ReadConfig.platforms}
        ReadConfig.dict_platform_mapping = {k.lower():k for k in ReadConfig.platforms}
        ### Others
        ReadConfig.key_prefix = 'MITRE:'
        ReadConfig.empty_layer_template = configParser.get('empty-layer-template', 'path')
        ReadConfig.layer_output_path = configParser.get('empty-layer-template', 'layer_output_path')
        ReadConfig.bypass_keyword_check = configParser.get('other-settings', 'bypass_keyword_check')
        ReadConfig.enable_platform_based_techniques = configParser.get('other-settings', 'enable_platform_based_techniques')
        ReadConfig.platform_based_techniques_output_path = configParser.get('other-settings', 'platform_based_techniques_output_path')
        ReadConfig.subtechnique_switch = configParser.get('other-settings', 'subtechnique_switch')
        try:
            ReadConfig.ignore_techniques = configParser.get('other-settings', 'ignore_techniques').split(',')
        except:
            ReadConfig.ignore_techniques = []
        ReadConfig.count_ignore = configParser.get('other-settings', 'count_ignore')
