import datetime
import json
import os
from typing import Iterable
import scrapy
from datdai_crawler.utils.utils import Utils
from scrapy.signalmanager import dispatcher
from scrapy import signals


class LmkHtmlSpiderSpider(scrapy.Spider):
    name = "lmk_html_spider"

    # start_urls = ["https://local"]

    def __init__(self, *args, **kwargs):
        super(LmkHtmlSpiderSpider, self).__init__(*args, **kwargs)
        self.utils = Utils()
        self.list_json_response = []
        self.heading = "Trả lời"
        self.invalid_link = []
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def convert_to_timestamp(datetime_str):
        # Replace 'SS' with '00'
        datetime_str = datetime_str.replace('SS', '00')

        # Define the datetime format
        datetime_format = "%d-%m-%YT%H:%M:%S%z"

        # Parse the datetime string to a datetime object
        dt = datetime.strptime(datetime_str, datetime_format)

        # Convert the datetime object to a timestamp
        timestamp = dt.timestamp()

        return timestamp

    def start_requests(self):
        lmk_html_dir = '/home/datltt/Documents/utility-repo/process_data/data/lmk_html'
        list_endpoints = []

        # Iterate directory
        for path in os.listdir(lmk_html_dir):
            # check if current path is a file
            if os.path.isfile(os.path.join(lmk_html_dir, path)):
                list_endpoints.append(path)
        # list_endpoints = [
        #     # '-chuyen-muc-dich-su-dung-dat-nong-nghiep-sang-dat-tho-cu-.aspx',
        #     'khi-nao-duoc-chuyen-doi-dat-sang-mo-hinh-trang-trai-chan-nuoi.aspx'
        # ]
        file_path = '/home/datltt/Documents/utility-repo/process_data/data/lmk_html/'
        for endpoint in list_endpoints:
            file_url = f'file://{os.path.abspath(f'{file_path}{endpoint}')}'
            yield scrapy.Request(url=file_url, callback=self.parse, 
                                meta={'url': self.utils.complete_lmk_url(endpoint=endpoint)})

    def parse(self, response):
        url = response.meta['url']
        # self.log(f'URL: {response.meta['url']}')
        title = response.css("title::text").get()
        self.log(f'Title: {title}')
        
        description = ''
        description_element = response.css('.article-detail').css('.description').get()
        if description_element is not None:
            description = self.utils.extract_text_from_html(description_element)

        #Get date
        snippet = response.css('div.meta-date').get()
        ts = 0
        if len(snippet) > 0:
            selector = scrapy.Selector(text=snippet)
            ts = self.utils.convert_to_timestamp(
                selector.xpath('//time[@class="updated"]/@datetime').get())

        list_questions = response.css('div.question').getall()
        formated_questions = []

        if len(list_questions) > 0:
            # self.log(f'Questions: {formated_questions}')
            formated_questions = [self.utils.extract_text_from_html(question) for question in list_questions]
            extracted_responses = response.css('div.staff-response').getall()
            formated_answers = [self.utils.html_to_markdown(answer) for answer in extracted_responses]

            # self.log(f'Answers: {formated_answers}')

            # self.log(f'There are {len(list_questions)} questions and {len(formated_answers)} answers')
            # for answer in formated_answers:
            #     print(f'Answer: {answer}\n')
            if len(list_questions) < len(formated_answers):
                formated_answers = formated_answers[0:len(list_questions)]
                self.log(f'{url} has Redundant answers !!!!')
            if len(list_questions) > len(formated_answers):
                self.log(f'{url} has more questions than answers')
        else:
            ## Case there is no question
            toc = response.css('.toc').css('.toc-list').get()
            if toc is not None:
                self.invalid_link.append(url)
                return

            formated_questions = [title]
            article_content = response.css('#article-content').get()

            ##catch the question before 'Tra loi'
            string_content = self.utils.extract_text_from_html(article_content)
            text_before_heading = self.utils.get_text_before_heading(string_content, self.heading)

            article_content = self.utils.html_to_markdown(article_content)
            if len(text_before_heading) > 0:
                formated_questions = [f'{description}\n{text_before_heading}']
                article_content = self.utils.get_text_after_heading(article_content, self.heading)

            # self.log(f'Content: {article_content}')
            formated_answers = [article_content]
        
        json_output = {
            "post_time": ts,
            "title": title,
            "url": url,
            "tags": [],
            "relevant_topic": [],
            "question": formated_questions,
            "answers": formated_answers
        }

        self.list_json_response.append(json_output)
        
    def spider_closed(self, spider):
        encoding: str = "utf-8"
        path = '/home/datltt/Documents/lmk_json_5'
        invalid_link_path = '/home/datltt/Documents/invalid_lmk'
        with open(path, "w+", encoding=encoding) as f:
            for entry in self.list_json_response:
                json.dump(entry, f, ensure_ascii=False, indent=None)
                f.write("\n")

        with open(invalid_link_path, "w+", encoding=encoding) as f:
            for entry in self.invalid_link:
                json.dump(entry, f, ensure_ascii=False, indent=None)
                f.write("\n")
        