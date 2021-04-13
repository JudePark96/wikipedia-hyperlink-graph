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
                    hyperlink = self.extract_hyper_link(paragraph)

                    paragraph_dict = {
                        'text': clean_text,
                        'cur_id_by_name': [link for link in hyperlink]
                    }
                    article_dict['paragraphs'].append(paragraph_dict)
                output.append(article_dict)

        print('saving start!')
        with open(self.out_path, 'wb') as f:
            pickle.dump(output, f)
            f.close()
        print('saving done!')


if __name__ == '__main__':
    reader_base = WikiReader(path='./rsc/wikipedia/text', out_path='./rsc/wikipedia/output.pkl')
    reader_base.construct_entity_graph()
    print(reader_base.get_cur_id('노벨 평화상'))
    targets = reader_base.aggregate_files_in_folders()
    json_data = reader_base.read_json_file(targets[0])[0]

    # it only considers first paragraph of fetched article.
    text = json_data['text'].split('\n')[0]
    # print(text)
    # print(reader_base.clean_markup(text))
    # print(re.findall(r'(?<=&lt;a href=")[^"]*', text))
    # print(reader_base.extract_hyper_link(text))




    """
    제임스 얼 카터 주니어(, &lt;a href="1924%EB%85%84"&gt;1924년&lt;/a&gt; &lt;a href="10%EC%9B%94%201%EC%9D%BC"&gt;10월 1일&lt;/a&gt; ~ )는 &lt;a href="%EB%AF%BC%EC%A3%BC%EB%8B%B9%20%28%EB%AF%B8%EA%B5%AD%29"&gt;민주당&lt;/a&gt; 출신 &lt;a href="%EB%AF%B8%EA%B5%AD"&gt;미국&lt;/a&gt; 39대 대통령 (&lt;a href="1977%EB%85%84"&gt;1977년&lt;/a&gt; ~ &lt;a href="1981%EB%85%84"&gt;1981년&lt;/a&gt;)이다.
    제임스 얼 카터 주니어(, 1924년 10월 1일 ~ )는 민주당 출신 미국 39대 대통령 (1977년 ~ 1981년)이다.
    ['1924%EB%85%84', '10%EC%9B%94%201%EC%9D%BC', '%EB%AF%BC%EC%A3%BC%EB%8B%B9%20%28%EB%AF%B8%EA%B5%AD%29', '%EB%AF%B8%EA%B5%AD', '1977%EB%85%84', '1981%EB%85%84']
    ['1924년', '10월 1일', '민주당 (미국)', '미국', '1977년', '1981년']
    """

