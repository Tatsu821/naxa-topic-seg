from time import sleep
import json
import os
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter

from openai import OpenAI, AzureOpenAI

text_splitter = CharacterTextSplitter(
    separator = "\n",  # セパレータ
    chunk_size = 2000,  # チャンクの文字数
    chunk_overlap = 0,  # チャンクオーバーラップの文字数
)

class SectionSplitter:
    def __init__(self, conf=None) -> None:
        self.client = OpenAI()
        
        self.prompt = PromptTemplate(
            template="{input_text} \n上記はあるテレビ番組の音声を文字起こしした文章です。上記の文章を内容に応じてセクションに分割して、文章はそのままで出力してください。ただしセクションが一つの場合もあります。出力は以下のJSON形式に従ってください。\n{json_scheme}",
            input_variables=["input_text"],
            partial_variables={"json_scheme": self.j_scheme()},
        )
        
        self.prompt_for_revise_sections = PromptTemplate(
            template="{input_text} \n上記の各セクションの文章の誤字脱字を修正してください。出力は以下のJSON形式に従ってください。\n{json_scheme}",
            input_variables=["input_text"],
            partial_variables={"json_scheme": self.j_scheme()},
        )
        
        self.revise_sections = False
        
    def run_split_by_sections(self, splitted_texts: list[str]) -> list[object]:
        outputs = []
        #オーバラップ用の出力の最後のセクション文
        last_section = ""
        
        # リトライ間隔（秒）
        retry_interval = 1
        # 試行回数
        tries = 5
        
        for idx, text in enumerate(splitted_texts):
            #入力をオーバラップ
            text = last_section + text
            
            output = self.text_generation(self.prompt.format(input_text=text))
            
            last_section = output['sections'][-1]['content']
            if idx is not len(splitted_texts)-1:
                output['sections'].pop()
            outputs.extend(output['sections'])
            # except:
            #     if idx + 1 == tries:
            #         # print(i)
            #         raise Exception("Error in Section Split")
            #     sleep(retry_interval)
                
            #     continue
        
        if self.revise_sections:
            section_texts = [sec['content'] for sec in outputs]
            outputs = self.run_revise_sections(text_splitter.split_text('\n'.join(section_texts)))
            
        return outputs
    
    def text_generation(self, prompt: str):        
        output_valid_flg = True
        while output_valid_flg:
            response = self.client.chat.completions.create(
                                    model = "gpt-4o",
                                    response_format={"type": "json_object"},
                                    messages = [
                                        {"role": "system", "content": "You are a helpful assistant."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    temperature=0.0,
                                )
            # print(response.choices[0].message.content)
            # output = Output.model_validate_json(response.choices[0].message.content, strict=False)
            output = json.loads(response.choices[0].message.content)
            
            if self.validate_json_structure(output):
                output_valid_flg = False
            else:
                output_valid_flg = True
        # print(output)
        return output
    
    def run_revise_sections(self, splitted_texts: list[str]) -> list[object]:
        outputs = []
        
        # リトライ間隔（秒）
        retry_interval = 1
        # 試行回数
        tries = 5
        
        def revise_sections(prompt: str):
            output_valid_flg = True
            while output_valid_flg:
                response = self.client.chat.completions.create(
                                        model = "gpt-4o",
                                        response_format={"type": "json_object"},
                                        messages = [
                                            {"role": "system", "content": "You are a helpful assistant."},
                                            {"role": "user", "content": prompt}
                                        ],
                                        temperature=0.0,
                                    )
                # print(response.choices[0].message.content)
                # output = Output.model_validate_json(response.choices[0].message.content, strict=False)
                output = json.loads(response.choices[0].message.content)
                
                if self.validate_json_structure(output):
                    output_valid_flg = False
                else:
                    output_valid_flg = True
            # print(output)
            return output
        
        for idx, text in enumerate(splitted_texts):
            try:
                output = revise_sections(self.prompt_for_revise_sections.format(input_text=text))
                
                outputs.extend(output['sections'])
            except:
                if idx + 1 == tries:
                    # print(i)
                    raise Exception("Error in Section Split")
                sleep(retry_interval)
                
                continue
            
        return outputs
        
        
    
    def j_scheme(self):
        return """
            {
                "sections": [
                    "title": "セクションのタイトル",
                    "content": "セクションの本文"
                ]
            }
            """
        # return """
        #     {
        #         "sections": [
        #             "content": "セクションの本文"
        #         ]
        #     }
        #     """
    
    def validate_json_structure(self, data):
        """
        指定されたJSON構造が正しいか確認する
        """
        if not isinstance(data, dict):
            return False
        if 'sections' not in data:
            return False
        if not isinstance(data['sections'], list):
            return False
        for section in data['sections']:
            if not isinstance(section, dict):
                return False
            if 'title' not in section or 'content' not in section:
            # if 'content' not in section:
                return False
        return True