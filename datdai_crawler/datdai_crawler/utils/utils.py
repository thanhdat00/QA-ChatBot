
from datetime import datetime
import json
import string
import traceback

from bs4 import BeautifulSoup
from typing import Dict, List, Union
import pandas as pd
import markdown2
import markdownify

class Utils:

    LMK_DOMAIN = "https://luatminhkhue.vn/"

    def __init__(self) -> None:
        pass

    def complete_lmk_url(self, endpoint: string):
        return f'{self.LMK_DOMAIN}{endpoint}'
    
    def extract_text_from_html(self, html_content: str):
        # Parse the HTML content using BeautifulSoup
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract the text
            text = soup.get_text()
            return text.strip()
        except Exception as e:
            print(f'Extract text from html failed {traceback.format_exc()}')
    
    def write(
        data: Union[Dict, List[Dict]],
        path: str,
        encoding: str = "utf-8",
        ensure_ascii: bool = False
    ):
        print(f"Writing JSONL file to {path}")
        print(f'!!!data {data}')
        if isinstance(data, pd.DataFrame):
            data = data.to_dict("records")
        with open(path, "a+", encoding=encoding) as f:
            for entry in data:
                json.dump(entry, f, ensure_ascii=ensure_ascii, indent=None)
                f.write("\n")

        # print(f"JSONL file written to {path}")

    # Define a function to convert HTML to Markdown
    def html_to_markdown(self, html_content:str):
        # Use markdown2 to convert HTML to Markdown
        # markdown_content = markdown2.markdown(html_content)
        # return markdown_content
        try:
            return markdownify.markdownify(html_content, heading_style="ATX")
        except:
            print(f'convert markdown failed')
            return self.extract_text_from_html(html_content)
    
    def convert_to_timestamp(self, date_string):
        # Define the format of the date string
        date_string = date_string.replace('SS', '00')
        date_format = "%d-%m-%YT%H:%M:%SZ"
        # Parse the date string using the defined format
        dt = datetime.datetime.strptime(date_string, date_format)
        
        # Convert the datetime object to a timestamp
        timestamp = int(dt.timestamp())
        
        return timestamp
    
    def get_text_before_heading(self, markdown_text, heading):
        # Find the index of the heading
        index = markdown_text.find(heading)
        # If the heading is found, return the text before it
        if index != -1:
            return markdown_text[:index].strip()
        else:
            return ""  # Return an empty string if the heading is not found

    def get_text_after_heading(self, markdown_text, heading):
        # Find the index of the heading
        index = markdown_text.find(heading)
        # If the heading is found, return the text before it
        if index != -1:
            return markdown_text[index+ len(heading):].strip()
        else:
            return ""  # Return an empty string if the heading is not found
        
    def file_name_to_url(self, file_name: str):
        return file_name.replace('*','/')
    
    def convert_to_timestamp_2(self, date_str):
        try:
            # Remove the pipe and whitespace, then parse the date
            date_str = date_str.replace(' | ', ' ')
            date_obj = datetime.strptime(date_str, '%H:%M %d/%m/%Y')
            # Convert to timestamp
            timestamp = datetime.timestamp(date_obj)
            return int(timestamp)
        except ValueError:
            return None
        
    def is_valid_ouput(self, output):
        return len(output['question']) > 0 and len(output['answers']) > 0 and len(output['title']) > 0