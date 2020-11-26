from xml.etree import ElementTree
from pymongo import MongoClient
from flask import Flask, jsonify
import requests


client = MongoClient()
enderecos = client.database.enderecos
app = Flask(__name__)

@app.route('/')
def redirect(cep):
    return "Insira uma url válida, como: 'localhost:5000/01001-001'"

@app.route('/<cep>')
def search_cep(cep):
    response = requests.get(f"https://viacep.com.br/ws/{cep}/xml/")
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)

        # Caso o CEP seja inválido, tratamento do erro
        if tree.find('erro') is not None:
            return jsonify({'sucesso': False})
        else:
            endereco = {
                'cep': tree.find('cep').text,
                'logr': tree.find('logradouro').text,
                'compl': tree.find('complemento').text,
                'bairro': tree.find('bairro').text,
                'cidade': tree.find('localidade').text,
                'uf': tree.find('uf').text,
            }

            # Inserção no banco de dados
            enderecos.insert_one(endereco)
            del endereco['_id']
            
            return jsonify({
                'sucesso': True,
                'endereco': endereco
            })
    else:
        return jsonify({'sucesso': False})
    

if __name__ == '__main__':
    app.run()