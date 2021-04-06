__author__ = 'Eunhwan Jude Park'
__email__ = 'judepark@{kookmin.ac.kr, jbnu.ac.kr}'

import itertools
import json
import requests
from glob import glob
from typing import List, Dict


class ReaderBase(object):
    def __init__(self, path) -> None:
        super(ReaderBase, self).__init__()
        self.path = path
        self.prefix = 'https://ko.wikipedia.org/w/api.php?action=query&format=json&titles='

    def aggregate_files_in_folders(self) -> List[str]:
        target_folder_list = glob(f'{self.path}/*')
        aggregated_file_paths = list(itertools.chain(*[glob(f'{folder}/*') for folder in target_folder_list]))

        return sorted(aggregated_file_paths)

    def read_json_file(self, file_path: str) -> List[Dict[str, str]]:
        with open(file_path, 'rb') as f:
            output = [json.loads(line) for line in f]
            f.close()
        return output

    def get_cur_id(self, title: str) -> str:
        return list(requests.get(self.prefix + title).json()['query']['pages'].keys())[0]


class WikiReader(ReaderBase):
    def __init__(self, path) -> None:
        super().__init__(path)


if __name__ == '__main__':
    reader_base = WikiReader(path='./rsc/wikipedia/text')
    call = 'https://ko.wikipedia.org/w/api.php?action=query&format=json&titles=' + '지미 카터'
    print(list((requests.get(call).json()['query']['pages'].keys())))
