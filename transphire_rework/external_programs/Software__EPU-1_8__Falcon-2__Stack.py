import json
import numpy as np
a = {
    'get_type': 'software',
    'get_name': 'EPU',
    'get_version': '1.09',
    'get_camera': 'Falcon3',
    'get_movie_type': 'Stack',
    'get_pre_first_command': None,
    'get_first_command': None,
    'get_post_first_command': None,
    'get_pre_second_command': None,
    'get_second_command': None,
    'get_post_second_command': None,
    'get_pre_third_command': None,
    'get_third_command': None,
    'get_post_third_command': None,
    'get_pre_final_command': None,
    'get_final_command': None,
    'get_post_final_command': None,
    'get_import_data': None,
    'get_output_files': ['.txt', '.log'],
    'get_content': {
        'test1': {
            'default': 0,
            'tooltip': 'test1 tooltip',
            'dependency': [],
            'type': 'int',
            'xml': False,
            'lower_limit': 0,
            'upper_limit': 'inf',
            'is_dir': False,
            'is_file': False,
            'new_output_file': [],
            'suppressed_output_file': [],
        },
        'test2': {
            'default': 'True',
            'tooltip': 'test2 tooltip',
            'dependency': [],
            'type': 'bool',
            'xml': None,
            'lower_limit': None,
            'upper_limit': None,
            'is_dir': False,
            'is_file': False,
            'new_output_file': [],
            'suppressed_output_file': [],
        },
        'test3': {
            'default': '3.0',
            'tooltip': 'test3 tooltip',
            'dependency': [],
            'type': 'float',
            'xml': True,
            'lower_limit': '-inf',
            'upper_limit': 'inf',
            'is_dir': False,
            'is_file': False,
            'new_output_file': [],
            'suppressed_output_file': [],
        },
        'test4': {
            'default': '',
            'tooltip': 'test4 tooltip',
            'dependency': ['test2:True'],
            'type': 'str',
            'xml': True,
            'lower_limit': '-inf',
            'upper_limit': 'inf',
            'is_dir': True,
            'is_file': False,
            'new_output_file': ['_test.txt'],
            'suppressed_output_file': ['_no_test.txt'],
        }
    },
}

with open('test.json', 'w') as w:
    print(json.dump(a, w, indent=2))
