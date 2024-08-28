import json
import traceback
from datdai_crawler.utils.utils import Utils
import scrapy


class TestSpiderSpider(scrapy.Spider):
    name = "test_spider"
    allowed_domains = ["local"]
    start_urls = ["https://thuvienphapluat.vn/hoi-dap-phap-luat/472AD-hd-thoi-han-su-dung-dat-khi-gia-han-la-bao-lau.html"]

    utils = Utils()
    list_json_response = []
    heading = "Trả lời"
    invalid_link = []

    def parse(self, response):

            # url = response.meta['url']
            url = ""

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
                
                print(f'Json ouput {json.dumps(json_output, ensure_ascii=False)}')

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
                # print(f'nexth2 {next_h2}')
                # print(f'content {content}')
                next_h2_start_index = content.index(next_h2.extract())
                content = content[:next_h2_start_index]
            else:
                # Get content after the last <h2>
                content = h2.xpath('following-sibling::node()').getall()
            
            # Clean up the content by joining text parts and stripping whitespace
            content = ' '.join(content).strip()
            print(f'Content obj type: {type(content)}')
            print(f'Content {content}')
            print(f'Length : {len(content)}')
            content = self.utils.html_to_markdown(content)

            list_answers.append(content)