__author__ = 'Eunhwan Jude Park'
__email__ = 'judepark@{kookmin.ac.kr, jbnu.ac.kr}'

import itertools
import json
import re
from glob import glob
from typing import List, Dict
from urllib.parse import unquote

import requests


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
    def __init__(self, path) -> None:
        super(WikiReader, self).__init__(path)


if __name__ == '__main__':
    reader_base = WikiReader(path='./rsc/wikipedia/text')
    targets = reader_base.aggregate_files_in_folders()
    json_data = reader_base.read_json_file(targets[0])[0]

    # it only considers first paragraph of fetched article.
    text = json_data['text'].split('\n')[0]
    print(text)
    print(reader_base.clean_markup(text))
    print(re.findall(r'(?<=&lt;a href=")[^"]*', text))
    print(reader_base.extract_hyper_link(text))

    """
    제임스 얼 카터 주니어(, &lt;a href="1924%EB%85%84"&gt;1924년&lt;/a&gt; &lt;a href="10%EC%9B%94%201%EC%9D%BC"&gt;10월 1일&lt;/a&gt; ~ )는 &lt;a href="%EB%AF%BC%EC%A3%BC%EB%8B%B9%20%28%EB%AF%B8%EA%B5%AD%29"&gt;민주당&lt;/a&gt; 출신 &lt;a href="%EB%AF%B8%EA%B5%AD"&gt;미국&lt;/a&gt; 39대 대통령 (&lt;a href="1977%EB%85%84"&gt;1977년&lt;/a&gt; ~ &lt;a href="1981%EB%85%84"&gt;1981년&lt;/a&gt;)이다.
    제임스 얼 카터 주니어(, 1924년 10월 1일 ~ )는 민주당 출신 미국 39대 대통령 (1977년 ~ 1981년)이다.
    ['1924%EB%85%84', '10%EC%9B%94%201%EC%9D%BC', '%EB%AF%BC%EC%A3%BC%EB%8B%B9%20%28%EB%AF%B8%EA%B5%AD%29', '%EB%AF%B8%EA%B5%AD', '1977%EB%85%84', '1981%EB%85%84']
    ['1924년', '10월 1일', '민주당 (미국)', '미국', '1977년', '1981년']
    """

