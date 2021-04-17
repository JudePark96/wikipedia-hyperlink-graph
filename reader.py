__author__ = 'Eunhwan Jude Park'
__email__ = 'judepark@{kookmin.ac.kr, jbnu.ac.kr}'

import itertools
import json
import pickle
import re
from glob import glob
from typing import List, Dict
from tqdm import tqdm
from urllib.parse import unquote, quote

import requests


class ReaderBase(object):
    def __init__(self, path: str) -> None:
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

    def extract_hyper_link(self, text: str, is_decode: bool = True) -> List[str]:
        items = re.findall(r'(?<=&lt;a href=")[^"]*', text)
        return [unquote(item) for item in items] if is_decode else items

    def extract_hyper_link_as_title(self, text: str) -> List[str]:
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        return re.findall(r'[^>]*>*([^<]+)</a>', text)

    def clean_markup(self, text: str) -> str:
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        return re.sub(r'<.*?>', '', text)

    def split_paragraph(self, text: str) -> List[str]:
        """
        paragraphs of each articles has seperators \n.
        """
        return text.split('\n')


class WikiReader(ReaderBase):
    def __init__(self, path: str, out_path: str) -> None:
        super(WikiReader, self).__init__(path)
        self.out_path = out_path

    def construct_entity_graph(self):
        target_files = self.aggregate_files_in_folders()
        output = []
        c = re.compile(r'[^ .,?!/@$%~％·∼()\x00-\x7F가-힣]+')
        for file in tqdm(target_files, desc='target files loading'):
            json_data = self.read_json_file(file)
            for json_object in json_data:
                article_dict = {
                    'cur_id': json_object['id'],
                    'revid': json_object['revid'],
                    'paragraphs': [
                    ]
                }
                paragraphs = self.split_paragraph(json_object['text'])

                for paragraph in paragraphs:
                    clean_text = self.clean_markup(paragraph)
                    if clean_text == '':
                        continue

                    hyperlink = self.extract_hyper_link(paragraph)

                    if len(hyperlink) == 0:
                        continue

                    hyperlink_title = self.extract_hyper_link_as_title(paragraph)

                    # this shouldn't be the zero!
                    assert len(hyperlink_title) != 0
                    entity_spans = hyperlink_title

                    paragraph_dict = {
                        'text': re.sub(c, '', clean_text),
                        'cur_id_by_name': [link for link in hyperlink],
                        'entity_span': entity_spans
                    }
                    article_dict['paragraphs'].append(paragraph_dict)
                if len(article_dict['paragraphs']) != 0:
                    output.append(article_dict)

        print('saving start!')
        with open(self.out_path, 'wb') as f:
            pickle.dump(output, f)
            f.close()
        print('saving done!')


if __name__ == '__main__':
    reader_base = WikiReader(path='./rsc/wikipedia/text', out_path='./rsc/wikipedia/output.pkl')
    reader_base.construct_entity_graph()