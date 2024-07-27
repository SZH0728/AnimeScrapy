from datetime import datetime
from re import compile
from typing import Iterable

from scrapy import Request, Spider, Selector
from scrapy.http import Response

from AnimeScrapy.items import ScoreItem, DetailItem, PictureItem

URL_PATTERN = compile(r'https?://(.*?)/.*?')
ANIME_PATTERN = compile(r'https?://(.*?)/anime/(\d+)/.*')
REPLACE_BLANK_TEXT = compile(r'[\s\n]+')
LANGUAGES = {"Afrikaans", "Albanian", "Amharic", "Arabic", "Assamese", "Azerbaijani", "Basque", "Belarusian", "Bengali",
             "Bulgarian", "Catalan", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Esperanto",
             "Estonian", "Faroese", "Finnish", "French", "Georgian", "German", "Greek", "Gujarati", "Hebrew", "Hindi",
             "Hungarian", "Icelandic", "Indonesian", "Irish", "Italian", "Japanese", "Javanese", "Kannada", "Kazakh",
             "Khmer", "Korean", "Kyrgyz", "Lao", "Latin", "Latvian", "Lithuanian", "Malagasy", "Malay", "Malayalam",
             "Maltese", "Maori", "Marathi", "Mongolian", "Nepali", "Norwegian", "Pashto", "Persian", "Polish",
             "Portuguese", "Punjabi", "Romanian", "Russian", "Samoan", "Scottish Gaelic", "Serbian", "Shona", "Sindhi",
             "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", "Sundanese", "Swahili", "Swedish", "Tagalog",
             "Tajik", "Tamil", "Tatar", "Telugu", "Thai", "Tibetan", "Turkish", "Turkmen", "Ukrainian", "Urdu",
             "Uyghur", "Uzbek", "Vietnamese", "Welsh", "Xhosa", "Yiddish", "Yoruba", "Zulu"}


class MyanimelistSpider(Spider):
    name = "MyAnimeList"
    allowed_domains = ["myanimelist.net"]

    def start_requests(self) -> Iterable[Request]:
        return [Request(url='https://myanimelist.net/anime/season', callback=self.parse_list, meta={'detail': {}})]

    def parse(self, response: Response):
        pass

    def parse_list(self, response: Response):
        for i in response.xpath(
                r'//*[@id="content"]/div[3]/div[contains(@class, "seasonal-anime-list")]'
                r'/div[contains(@class, "seasonal-anime")]'):
            score = ScoreItem()

            score['name'] = i.xpath(r'./div[1]/div[1]/span[4]/text()').get()
            score['score'] = float(i.xpath(r'./div[1]/div[1]/span[2]/text()').get())
            score['vote'] = int(i.xpath(r'./div[1]/div[1]/span[1]/text()').get())
            score['source'] = URL_PATTERN.findall(response.url)[0]

            yield score

        urls = []
        for i in response.xpath(
                r'//*[@id="content"]/div[3]/div[contains(@class, "seasonal-anime-list")]/'
                r'div[contains(@class, "seasonal-anime")]'):
            name = i.xpath(r'./div[1]/div[1]/span[4]/text()').get()
            if name not in response.meta['anime']:
                urls.append(i.xpath(r'./div[1]/div[1]/div/h2/a/@href').get())

        yield from response.follow_all(urls, callback=self.parse_detail, meta=response.meta)

    def parse_detail(self, response: Response):
        detail = DetailItem()
        detail['alias'] = []
        detail['tag'] = []
        detail['cast'] = []

        info_list: Selector = response.xpath(r'//div[contains(@class, "leftside")]')
        info_list: list[Selector] = info_list.xpath(r'.//div[contains(@class, "spaceit_pad")]')
        for i in info_list:
            text = i.xpath(r'string(.)').get()
            text = text.strip()
            text = REPLACE_BLANK_TEXT.sub(' ', text)

            match text.split(':', 1):
                case 'Japanese', name:
                    detail['name'] = name.strip()
                case (language, name) if language in LANGUAGES:
                    detail['alias'].append(name.strip())
                case 'Aired', time:
                    time = time.split(' to ')[0].strip()
                    detail['time'] = datetime.strptime(time, '%b %d, %Y').date()

        translation = response.xpath(r'//*[contains(@class, "h1-title")]//text()')
        match len(translation):
            case 1:
                detail['translation'] = translation[0].get().strip()
            case 2:
                detail['translation'] = translation[1].get().strip()
            case _:
                raise ValueError(f'Invalid translation on page {response.url}')

        detail['description'] = response.xpath(r'string(//p[contains(@itemprop, "description")])').get()
        detail['web'], detail['webId'] = ANIME_PATTERN.findall(response.url)[0]
        picture_url = response.xpath(r'//div[contains(@class, "leftside")]/div/a/img/@data-src').get()
        detail['picture'] = picture_url

        character_url = response.xpath('//*[@id="horiznav_nav"]/ul/li[2]/a/@href').get()
        response.meta['detail'][detail['translation']] = detail
        yield response.follow(url=character_url, callback=self.parse_character, meta=response.meta)

        if detail['alias']:
            name_list = (detail['name'], detail['translation'], *detail['alias'])
        else:
            name_list = (detail['name'], detail['translation'])

        response.meta['picture'][picture_url] = tuple(set(name_list))
        yield response.follow(url=picture_url, callback=self.parse_picture, meta=response.meta)

    @staticmethod
    def parse_character(response: Response):
        name = response.xpath(r'//*[contains(@class, "h1-title")]//text()')
        match len(name):
            case 1:
                name = name[0].get().strip()
            case 2:
                name = name[1].get().strip()
            case _:
                raise ValueError(f'Invalid translation on page {response.url}')

        detail = response.meta['detail'][name]

        casts = []
        for i in response.xpath(r'//tr[contains(@class, "js-anime-character-va-lang")]'):
            casts.append(i.xpath(r'./td[1]/div[1]/a/text()').get())
        detail['cast'] = casts

        for i in response.xpath(r'//div[contains(@class, "rightside js-scrollfix-bottom-rel")]/table'):
            position = i.xpath(r'./tr/td[2]/div/small/text()').get()
            position = position.split(', ')
            if 'Director' in position:
                detail['director'] = i.xpath(r'./tr/td[2]/a/text()').get()
                break

        yield detail

    @staticmethod
    def parse_picture(response: Response):
        picture = PictureItem()
        picture['name'] = response.meta['picture'][response.url]
        picture['picture'] = response.body
        yield picture


if __name__ == '__main__':
    from scrapy.cmdline import execute
    execute('scrapy crawl MyAnimeList'.split())
