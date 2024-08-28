import json
import os
import traceback
import scrapy
from datdai_crawler.utils.utils import Utils
from scrapy.signalmanager import dispatcher
from scrapy import signals

class GiaoDichBatDongSanSpider(scrapy.Spider):
    name = "tvpl"
    def __init__(self, topic = None, *args, **kwargs):
        super(GiaoDichBatDongSanSpider, self).__init__(*args, **kwargs)
        self.utils = Utils()
        self.list_json_response = []
        self.heading = "Trả lời"
        self.invalid_link = []
        self.topic_name = topic
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        dir = f'/home/datltt/Documents/luat-dat-dai/{self.topic_name}/'

        list_files_name = []

        for file_name in os.listdir(dir):
            # check if current path is a file
            if os.path.isfile(os.path.join(dir, file_name)):
                file_path = f'file://{os.path.abspath(f'{dir}{file_name}')}'
                yield scrapy.Request(url=file_path, callback=self.parse, 
                                    meta={'url': self.utils.file_name_to_url(file_name=file_name),
                                        'file_name': file_name
                                        })

    def parse(self, response):

        url = response.meta['url']

        try:
            title = response.css("title::text").get()
            time = response.xpath('//span[@class="news-time"]/text()').get()
            ts = self.utils.convert_to_timestamp_2(time)
            list_questions, list_answers = [] , []

            toc = response.css('div.accordion-item').get()
            if toc is not None:
                self.parse_page_having_toc(response, list_questions, list_answers)
            else:
                self.parse_page_having_content_only(response, list_questions, list_answers)


            json_output = {
                    "url": url,
                    "title": title,
                    "post_time": ts,
                    "tags": [],
                    "relevant_topic": [],
                    "question": list_questions,
                    "answers": list_answers
                }

            if self.utils.is_valid_ouput(json_output):
                self.list_json_response.append(json_output)
                # print(f'output {json_output}')
            else:
                # print('invalid ' + url)
                # print(f'output {json_output}')
                self.invalid_link.append(url)
            
        except Exception as e:
            print(f'parse failed ' + traceback.format_exc())
            self.invalid_link.append(url)

    def parse_page_having_content_only(self, response, list_questions: list, list_answers: list):
        question = response.css('.tvpl-main .sapo').get()
        question = self.utils.extract_text_from_html(question)
        list_questions.append(question)

        article_content = response.css('#news-content').get()
        article_content = self.utils.html_to_markdown(article_content)

        if len(question) > 0:
            article_content = self.utils.get_text_after_heading(article_content, question[-6:])

        list_answers.append(article_content)
            # print(f'Contentttt:   {article_content}')

    def parse_page_having_toc(self, response, list_questions, list_answers):
        self.parse_h2_content(response, list_questions, list_answers)


    def parse_h2_content(self, response, list_questions, list_answers):

        # Extract all <h2> tags
        h2_tags = response.xpath('//h2')
        
        # Iterate over each <h2> tag and its content
        for i, h2 in enumerate(h2_tags):
            h2_text = h2.xpath('string()').get().strip()
            list_questions.append(h2_text)

            # Determine the scope of the content to scrape
            if i + 1 < len(h2_tags):
                # Get content up to the next <h2>
                content = h2.xpath('following-sibling::node()').getall()
                next_h2 = h2_tags[i + 1]
                next_h2_start_index = content.index(next_h2.extract())
                content = content[:next_h2_start_index]
            else:
                # Get content after the last <h2>
                content = h2.xpath('following-sibling::node()').getall()
            
            # Clean up the content by joining text parts and stripping whitespace
            content = ' '.join(content).strip()
            content = self.utils.html_to_markdown(content)
            list_answers.append(content)

    def spider_closed(self, spider):
        encoding: str = "utf-8"
        path = f'/home/datltt/Documents/luat-dat-dai/output/{self.topic_name}-ouput.jsonl'
        invalid_link_path = f'/home/datltt/Documents/luat-dat-dai/output/{self.topic_name}-invalid.jsonl'
        with open(path, "w+", encoding=encoding) as f:
            for entry in self.list_json_response:
                json.dump(entry, f, ensure_ascii=False, indent=None)
                f.write("\n")

        if len(self.invalid_link) > 0:
            with open(invalid_link_path, "w+", encoding=encoding) as f:
                for entry in self.invalid_link:
                    json.dump(entry, f, ensure_ascii=False, indent=None)
                    f.write("\n")
