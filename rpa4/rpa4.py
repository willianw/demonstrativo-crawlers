from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import json
import os
import re

# Deve ter instalado o driver para chrome
driver = webdriver.Chrome(os.path.expanduser('~/Downloads/chromedriver/chromedriver'))
driver.get("https://www.mercadolivre.com.br/")


# Formulário de busca do mercado livre
form = driver.find_element_by_css_selector("form.nav-search")

# Busca por produto
prod_input = form.find_element_by_css_selector("input.nav-search-input")
prod_input.clear()
prod_input.send_keys("GPON")

# Clica no botão de busca
prod_search = form.find_element_by_css_selector("button.nav-search-btn")
prod_search.click()


# Espera carregar a página dos produtos
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item")))
products_elements = driver.find_elements_by_css_selector("li.ui-search-layout__item")


products = []
for product in products_elements:
    title = product.find_element_by_css_selector("div.ui-search-item__group--title h2").text
    price = product.find_element_by_css_selector(".ui-search-item__group--price span.price-tag-fraction").text
    carousel = product.find_element_by_css_selector(".ui-search-result__image")
    ActionChains(driver).move_to_element(carousel).perform()

    # As imagens dos produtos são carregadas conforme o usuário clica no botão para
    # ver mais imagens. Dessa forma, é necessário clicar nos botões de 'próxima imagem'
    # para que todas apareçam
    buttons = carousel.find_elements_by_css_selector("button.next-button")
    if len(buttons) > 0:
        button = buttons[0]
        while 'arrow-disabled' not in button.get_attribute('class').split():
            try:
                ActionChains(driver).move_to_element(button).perform()
            except:
                pass
            button.click()
            driver.implicitly_wait(0.05)
    images_urls = [img.get_attribute('src')
                   for img in carousel.find_elements_by_css_selector("img")]
    products.append({
        'title': title,
        'price': price,
        'images_urls': images_urls
    })


# Salva os dados obtidos
output_file = os.path.join(os.path.dirname(__file__), 'willian_mercadolivre.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False)

driver.close()