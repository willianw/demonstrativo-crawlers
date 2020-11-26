import scrapy
from scrapy_splash import SplashRequest
import re
import pdb
import json

script="""
    function main(splash)
        splash:wait(1)
        
        local element = splash:select('#bigsearch-query-detached-query')
        assert(element:mouse_click{})
        splash:wait(1)
        assert(element:element:send_text('Borá, SP'))
        splash:wait(1)
        local search = splash:select('form')
        splash:runjs('document.querySelector("form").submit()')
        splash:wait(1)
        return splash:html()
        return {
            png = splash:png
            html = splash:html(),
        }
    end
"""


class OlhardigitalSpider(scrapy.Spider):
    name = 'airbnb'
    allowed_domains = ['airbnb.com.br']

    # Tentei simular o clique no splash,
    # mas é mais fácil e garantido buscar direto pela cidade mencionada.
    # Se fosse uma busca genérica, teria de buscar por cidade primeiro.
    start_urls = ['https://www.airbnb.com.br/s/Bor%C3%A1-~-SP--Brasil/homes']

    def __init__(self, *args):
        super().__init__(*args)
        self.places = []

    def start_requests_unused(self):
        yield Request(
            self.start_url, 
            callback = self.get_places, 
            endpoint = 'execute',
            args = {'lua_source': script, 'timeout': 10},
        )

    # Unused
    def get_places(self, response):
        with open('html.html', 'wb') as f:
            f.write(response.body)

    # Parse de localidades
    def parse(self, response):
        for item in response.xpath("//div[@class='_8ssblpx']"):
            name = item.xpath(".//div[@class='_bzh5lkq']/text()").get()
            price = item.xpath(".//span[@class='_1p7iugi']/text()").get()
            place = {'name': name, 'price': int(re.search(r'R\$(\d+)', price).group(1))}

            # Nem todas as localidades possuem avaliações
            info = item.xpath(".//span[@class='_18khxk1']")
            if info:
                aval = info.xpath("span[@class='_10fy1f8']/text()").get()
                reviews = ''.join(info.xpath("span[@class='_a7a5sx']/text()").getall())
                place['aval'] = float(aval)
                place['reviews'] = int(re.sub(r'[^\d]+', '', reviews))
            
            self.places.append(place)
            yield place

    def closed(self, reason):

        # Calcula o preço e avaliação médias
        avg_price = sum([p['price'] for p in self.places])/len(self.places)
        avals = [p['aval'] for p in self.places if 'aval' in p]
        avg_aval = sum(avals)/len(avals)
        resumo = {'avg_price': avg_price, 'avg_aval': avg_aval}

        with open('willian_airbnb_resumo.json', 'w', encoding='utf-8') as f:
            json.dump(resumo, f, ensure_ascii=False)