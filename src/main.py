import argparse

from section_splitter import SectionSplitter
from utils import *

def main(path):
    file_path = Path(path)
    encoding = 'utf_8' if detect_encoding(file_path).encoding=='utf_8' else 'shift_jis'
    # with open(file_path, "r", encoding="shi") as file:
    with open(file_path, "r", encoding=encoding) as file:
        content = file.read()
        
    splitted_texts = [text.replace('\n', '') for text in text_splitter.split_text(content)]

    sec_splitter = SectionSplitter()
    sec_split_res = sec_splitter.run_split_by_sections(splitted_texts)

    save(sec_split_res, file_path.parent/f'segment_result_{file_path.stem}.json')

    json_to_csv(sec_split_res, file_path.parent/f'segment_result_{file_path.stem}.csv')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--path')
    
    args = parser.parse_args()
    
    main(args.path)