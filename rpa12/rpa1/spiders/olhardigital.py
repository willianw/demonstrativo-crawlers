import scrapy


class OlhardigitalSpider(scrapy.Spider):
    name = 'olhardigital'
    allowed_domains = ['olhardigital.com.br']
    start_urls = ['http://olhardigital.com.br/']

    def parse(self, response):
        link = response.xpath('//ul[@class="menu"]/li[position()=3]/a/@href').get()
        yield scrapy.Request(f"https:{link}", callback=self.parse_em_alta)

    def parse_em_alta(self, response):
        news = response.xpath("//div[@id='content']/div[@class='inner-wrapper']" + 
                              "/div[@class='lista-content']/div[@class='inner-wrapper']" + 
                              "//a/@href")
        for new in news[:5]:
            yield scrapy.Request(f"https:{new.get()}", callback=self.parse_news)

    def parse_news(self, response):
        title = response.xpath("//h1[@class='mat-tit']/text()").get()
        subtitle = response.xpath("//h2[@class='mat-lead']/text()").get()
        date = response.xpath("//span[@class='meta-item meta-pub-d']/text()").get()
        time = response.xpath("//span[@class='meta-item meta-pub-h']/text()").get()
        yield {
            'title': title,
            'subtitle': subtitle,
            'date': date,
            'time': time,
        }