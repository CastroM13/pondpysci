# -*- coding: utf-8 -*-
from flask import Flask, request
from requests import get
from bs4 import BeautifulSoup
from flask_cors import CORS, cross_origin
from Processor import response
import json
import os

app = Flask("pond")
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

@app.route('/')
def index():
    return '<h1>Lista de Serviços:</h1><a href="/noticias/globo">Notícias Globo</a><br/><a href="/noticias/canalrural">Notícias Canal Rural</a><br/><a href="/cotas/cepea/acucar">Cotas Cepea acucar</a><br/><a href="/cotas/cepea/algodao">Cotas Cepea algodao</a><br/><a href="/cotas/cepea/arroz">Cotas Cepea arroz</a><br/><a href="/cotas/cepea/bezerro">Cotas Cepea bezerro</a><br/><a href="/cotas/cepea/boi-gordo">Cotas Cepea boi-gordo</a><br/><a href="/cotas/cepea/cafe">Cotas Cepea cafe</a><br/><a href="/cotas/cepea/soja">Cotas Cepea soja</a><br/>'


@app.route("/noticias/<fonte>", methods=["GET"])
@cross_origin()
def Noticias(fonte):
  if fonte == "canalrural":
    noticias = get('https://www.canalrural.com.br/noticias-da-agropecuaria/')
    retorno = []
    if noticias:
      page = BeautifulSoup(noticias.content, 'html.parser')
      noticiasFormatadas = page.find_all("div", "info")
      for noticia in noticiasFormatadas:
        retorno.append({"title": noticia.find('a') and noticia.find('a')['title'], "date": noticia.find(attrs={'data-hora'}), "link": noticia.find('a') and noticia.find('a')['href']})
    return str(retorno)
  elif fonte == "globo":
    noticias = get('http://g1.globo.com/dynamo/natureza/rss2.xml')
    retorno = []
    if noticias:
      noticiasFormatadas = BeautifulSoup(noticias.content, 'html.parser')
      todasNoticiasNomes = noticiasFormatadas.find_all("item")
      for noticia in todasNoticiasNomes:
        titulo = BeautifulSoup(str(noticia.find("title")), "html.parser").text
        link = BeautifulSoup(str(noticia.find("guid")), "html.parser").text
        try:
            data = BeautifulSoup(str(noticia.find("guid")), "html.parser").text.split("noticia/")[1][0:10]
        except IndexError:
            data = 'Sem data'
        retorno.append({"title": titulo, "date": data, "link": link})
    return str(retorno)

@app.route("/cotas/cepea/<tipo>", methods=["GET"])
@cross_origin()
def CotacaoCepea1(tipo):
  retorno = []
  noticias = get(f'https://www.cepea.esalq.usp.br/br/indicador/{tipo}.aspx')
  page = BeautifulSoup(noticias.content, 'html.parser')
  cotacoes = page.find_all("table")[0]
  nota = page.find_all(attrs={"imagenet-fonte-tabela"})[1].text
  cotacaoIndividual = cotacoes.find_all("tr")
  for cotacao in cotacaoIndividual:
    if cotacao.find_all("td"):
      retorno.append({"description": f"No dia {cotacao.find_all('td')[0].text} a cotação de {tipo} fechou em R$ {cotacao.find_all('td')[1].text} e US$ {cotacao.find_all('td')[4].text} com uma variação diária de {cotacao.find_all('td')[2].text} e mensal de {cotacao.find_all('td')[3].text}.",
                      "nota": nota})
  return str(retorno)

@app.route("/mensagem/<texto>", methods=["GET"])
@cross_origin()
def Mensagem(texto):
  responseValue = response(texto)
  print(responseValue)
  if responseValue == "request-noticia-globo":
    return Noticias("globo")
  if responseValue == "request-noticia-canal-rural":
    return Noticias("canal-rural")
  if responseValue == "request-cota-acucar":
    return CotacaoCepea1("acucar")
  if responseValue == "request-cota-algodao":
    return CotacaoCepea1("algodao")
  if responseValue == "request-cota-arroz":
    return CotacaoCepea1("arroz")
  if responseValue == "request-cota-bezerro":
    return CotacaoCepea1("bezerro")
  if responseValue == "request-cota-boi-gordo":
    return CotacaoCepea1("boi-gordo")
  if responseValue == "request-cota-cafe":
    return CotacaoCepea1("cafe")
  if responseValue == "request-cota-soja":
    return CotacaoCepea1("soja")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)