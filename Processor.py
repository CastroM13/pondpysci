#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB

def exibir_resultado(valor):
    frase, resultado = valor
    if resultado[0] == '0':
        resultado = "request-noticia-globo"
    if resultado[0] == '1':
        resultado = "request-noticia-canal-rural"
    if resultado[0] == '2':
        resultado = "request-cota-acucar"
    if resultado[0] == '3':
        resultado = "request-cota-algodao"
    if resultado[0] == '4':
        resultado = "request-cota-arroz"
    if resultado[0] == '5':
        resultado = "request-cota-bezerro"
    if resultado[0] == '6':
        resultado = "request-cota-boi-gordo"
    if resultado[0] == '7':
        resultado = "request-cota-cafe"
    if resultado[0] == '8':
        resultado = "request-cota-soja"
    return resultado

def analisar_frase(classificador, vetorizador, frase):
    return frase, classificador.predict(vetorizador.transform([frase]))

def obter_dados_das_fontes():
    diretorio_base = "C:\\Repositories\\pondpysci\\dataset\\"
    dados = []
         
    with open(diretorio_base + "dataset.txt", "r", encoding="utf8") as arquivo_texto:
        dados += arquivo_texto.read().split('\n')

    return dados

def tratamento_dos_dados(dados):
    dados_tratados = []
    for dado in dados:
        if len(dado.split("%")) == 2 and dado.split("%")[1] != "":
            dados_tratados.append(dado.split("%"))

    return dados_tratados

def dividir_dados_para_treino_e_validacao(dados):
    quantidade_total = len(dados)
    percentual_para_treino = 0.75
    treino = []
    validacao = []

    for indice in range(0, quantidade_total):
        if indice < quantidade_total * percentual_para_treino:
            treino.append(dados[indice])
        else:
            validacao.append(dados[indice])

    return treino, validacao

def pre_processamento():
    dados = obter_dados_das_fontes()
    dados_tratados = tratamento_dos_dados(dados)

    return dividir_dados_para_treino_e_validacao(dados_tratados)


def realizar_treinamento(registros_de_treino, vetorizador):
    treino_comentarios = [registro_treino[0] for registro_treino in registros_de_treino]
    treino_respostas = [registro_treino[1] for registro_treino in registros_de_treino]

    treino_comentarios = vetorizador.fit_transform(treino_comentarios)

    return BernoulliNB().fit(treino_comentarios, treino_respostas)

def realizar_avaliacao_simples(registros_para_avaliacao):
    avaliacao_comentarios = [registro_avaliacao[0] for registro_avaliacao in registros_para_avaliacao]
    avaliacao_respostas   = [registro_avaliacao[1] for registro_avaliacao in registros_para_avaliacao]

    total = len(avaliacao_comentarios)
    acertos = 0
    for indice in range(0, total):
        resultado_analise = analisar_frase(classificador, vetorizador, avaliacao_comentarios[indice])
        frase, resultado = resultado_analise
        acertos += 1 if resultado[0] == avaliacao_respostas[indice] else 0

    return acertos * 100 / total

def realizar_avaliacao_completa(registros_para_avaliacao):
    avaliacao_comentarios = [registro_avaliacao[0] for registro_avaliacao in registros_para_avaliacao]
    avaliacao_respostas   = [registro_avaliacao[1] for registro_avaliacao in registros_para_avaliacao]

    total = len(avaliacao_comentarios)
    verdadeiros_positivos = 0
    verdadeiros_negativos = 0
    falsos_positivos = 0
    falsos_negativos = 0

    for indice in range(0, total):
        resultado_analise = analisar_frase(classificador, vetorizador, avaliacao_comentarios[indice])
        frase, resultado = resultado_analise
        if resultado[0] == '0':
            verdadeiros_negativos += 1 if avaliacao_respostas[indice] == '0' else 0
            falsos_negativos += 1 if avaliacao_respostas[indice] != '0' else 0
        else:
            verdadeiros_positivos += 1 if avaliacao_respostas[indice] == '1' else 0
            falsos_positivos += 1 if avaliacao_respostas[indice] != '1' else 0

    return ( verdadeiros_positivos * 100 / total, 
             verdadeiros_negativos * 100 / total,
             falsos_positivos * 100 / total,
             falsos_negativos * 100 / total
           )

registros_de_treino, registros_para_avaliacao = pre_processamento()
vetorizador = CountVectorizer(binary = 'true')
classificador = realizar_treinamento(registros_de_treino, vetorizador)

percentual_acerto = realizar_avaliacao_simples(registros_para_avaliacao)
informacoes_analise = realizar_avaliacao_completa(registros_para_avaliacao)

verdadeiros_positivos,verdadeiros_negativos,falsos_positivos,falsos_negativos = informacoes_analise

def response(message):
    result = exibir_resultado( analisar_frase(classificador, vetorizador,message))
    return result