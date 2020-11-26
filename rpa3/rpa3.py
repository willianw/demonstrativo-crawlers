from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import os
import re

# Deve ter instalado o driver para chrome
driver = webdriver.Chrome(os.path.expanduser('~/Downloads/chromedriver/chromedriver'))
driver.get("https://www.airbnb.com.br/")

# Digitar a cidade de interesse no campo de busca
city_input = driver.find_element_by_id("bigsearch-query-detached-query")
city_input.clear()
city_input.send_keys("BORÁ, SP")

# Clica no botão de pesquisa
search = driver.find_element_by_css_selector('._w64aej')
search.click()

# Espera até carregar as imagens
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='_8ssblpx']")))
locations = driver.find_elements_by_xpath("//div[@class='_8ssblpx']")


places = []
for location in locations:
    name = location.find_element_by_xpath(".//div[@class='_bzh5lkq']").text
    price = location.find_element_by_xpath(".//span[@class='_1p7iugi']").text
    place = {'name': name, 'price': int(re.search(r'Preço:\nR\$ (\d+)', price).group(1))}
    
    # Pode ser que não contenha as informações de avaliações
    info = location.find_elements_by_xpath(".//span[@class='_18khxk1']")
    if len(info) > 0:
        nota = info[0].find_element_by_xpath("span[@class='_10fy1f8']").text
        reviews = info[0].find_element_by_xpath("span[@class='_a7a5sx']").text
        place['aval'] = float(nota)
        place['reviews'] = int(re.sub(r'[^\d]+', '', reviews))
    
    places.append(place)


# Salva os dados de localidades
output_file = os.path.join(os.path.dirname(__file__), 'willian_airbnb2.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(places, f, ensure_ascii=False)

# Salva os dados com resumo (médias)
output_resume_file = os.path.join(os.path.dirname(__file__), 'willian_airbnb2_resumo.json')
with open(output_resume_file, 'w', encoding='utf-8') as f:
    avg_price = sum([p['price'] for p in places])/len(places)
    avals = [p['aval'] for p in places if 'aval' in p]
    avg_aval = sum(avals)/len(avals)
    resumo = {'avg_price': avg_price, 'avg_aval': avg_aval}
    json.dump(resumo, f, ensure_ascii=False)

driver.close()