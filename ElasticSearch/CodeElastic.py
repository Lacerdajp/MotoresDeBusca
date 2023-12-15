from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import timeit
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt


def documentosRelevantes(nome, i):
    val = []
    with open(nome, "r") as arquivo:
        for linha in arquivo:
            if int(linha.split()[0]) == (i+1):
                val.append(''.join(linha.split()[1]))

    return val


def getPrecision(Ra, R):
    return Ra/R


def getRecall(Ra, A):
    return Ra/A


def limparQuery(string):
    saida = string.replace("\n", " ").replace(
        "the ", "").replace("an ", "").replace("a ", "").strip()
    return saida


def limparLixo(string):

    antesLimpeza = timeit.default_timer()
    saida = string.replace("\n", " ").replace(
        ".B", "").replace(".W", "").replace("the ", "").replace("an ", "").replace("a ", "").strip()
    depoisLimpeza = timeit.default_timer()

    tempoLimpeza = depoisLimpeza - antesLimpeza

    return saida


def lerColecao(path):

    antesLeitura = timeit.default_timer()
    with open(path, "r") as file:
        f = file.read()
    depoisLeitura = timeit.default_timer()

    tempoLeitura = depoisLeitura - antesLeitura
    return f.split(".I")[1:]


def lerDiretorioIndex(index_name, arquivo, es):
    docs = []
    tempoIndexacao = timeit.default_timer()
    for x, linha in enumerate(lerColecao(arquivo)):
        content = limparLixo(linha)
        index = x
        i = ''.join(content.split(" .T")[:1])
        title = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[:1])
        content = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[1:])
        doc = {
            '_index': index_name,
            '_id': index,
            '_source': {
                'index': i,
                'title': title,
                'content': content
            }
        }
        docs.append(doc)

    tempoIndexacao = timeit.default_timer() - tempoIndexacao
    success, failled = bulk(es, docs)
    return tempoIndexacao


def VerificaDiretorioIndex(index_diretorio, arquivo, es):
    if not es.indices.exists(index=index_diretorio):
        es.indices.create(index=index_diretorio)
    tempoIndexacao = lerDiretorioIndex(index_diretorio, arquivo, es)
    return tempoIndexacao


def plotarGRaficos(nome, x, y, namex, namey):
    plt.plot(x, y, color='red')
    plt.xlabel(namex)
    plt.ylabel(namey)
    plt.show()


load_dotenv()

es = Elasticsearch(
    ['http://localhost:9200/'],
    basic_auth=(os.environ.get('ELASTIC_NAME'), os.environ.get('ELASTIC_PASSWORD')))
index_diretorio = "my_index"
arquivo = "DataSets/cran.all.1400"
tempoIndexacao = VerificaDiretorioIndex(index_diretorio, arquivo, es)
# Caso queira Habiilitar a busca Manual descomente esse codigo e ajuste a identação:
# tipo_teste = int(
#     input("Digite o tipo de teste:\n1.Teste Automatico\n2.Teste Manual\n"))
# if (tipo_teste == 1):
arquivo_query = "DataSets/cran.qry"
arquivoResposta = open("Respostas/elasticRespostasCran.txt", "a")
arquivoResposta.truncate(0)
precision = []
recall = []
tempoBusca = []
perguntas = []
docsRelev = []
docs = []
for x, linha in enumerate(lerColecao(arquivo_query)):
    doc = []
    perguntas.append(x+1)
    busca = limparQuery(linha)
    i = ''.join(busca.split(" .W ")[:1])
    busca = ''.join(busca.split(" .W ")[1:])
    temp = timeit.default_timer()
    results = es.search(index=index_diretorio,
                        body={
                            "query": {
                                "multi_match": {
                                    "query": busca,
                                    "fields": ["title", "content"]
                                }
                            }
                        }
                        )
    temp = timeit.default_timer()-temp
    for hit in results['hits']['hits']:
        doc.append(hit['_source']['index'])
        arquivoResposta.write(
            f"Linha:{x+1}-IDPergunta:{i}-IDDocumento:{hit['_source']['index']}-Score:{hit['_score']}\n")
        arquivoResposta.write(f"Pergunta:{busca}\n")
        arquivoResposta.write(f"Titulo:{hit['_source']['title']}\n")
        arquivoResposta.write(
            f"--------------------------------------------\n")
    docReelev = documentosRelevantes("DataSets/cranqrel", x)
    docsRelev.append(docReelev)
    docs.append(doc)
    tempoBusca.append(temp)
for k in range(10):
    p = []
    r = []
    for i, linha in enumerate(docs):

        releRecupTotal = len(
            set(linha[:k+1]).intersection(set(docsRelev[i])))
        p.append(getPrecision(releRecupTotal, k+1))
        r.append(getRecall(releRecupTotal, len(docsRelev[i])))
    precision.append(sum(p)/len(p))
    recall.append(sum(r)/len(r))
print("O tempo de busca se da por: "+str(sum(tempoBusca)/len(tempoBusca)))
print("O tempo de Indexação é: "+str(tempoIndexacao))
plotarGRaficos("Grafico de Recall X K ElasticSearch", y=recall,
               x=[linha for linha in range(10)], namex="k", namey="Recall")
plotarGRaficos("Grafico de Precision X ElasticSearch", y=precision,
               x=[linha for linha in range(10)], namex="k", namey="Precision")
arquivoResposta.close()
# elif (tipo_teste == 2):
#     tipoBusca = int(input(
#         "Digite o tipo de busca (Linha ou Texto):\n1.Numero Estudo\n2.Conteudo\n3.Titulo\n "))
#     if (tipoBusca == 2):
#         busca = input("Digite o conteudo de busca: ")
#         results = es.search(index=index_diretorio, body={
#             "query": {"match": {"content": busca}}})
#         flag = True

#     elif (tipoBusca == 1):
#         busca = input("Digite o numero da linha: ")
#         results = results = results = es.search(index=index_diretorio, body={
#             "query": {"match": {"identificador": busca}}})
#         flag = True
#     elif (tipoBusca == 3):
#         busca = input("Digite o parte do Titulo do estudo: ")
#         results = results = es.search(index=index_diretorio, body={
#             "query": {"match": {"title": busca}}})
#         flag = True
#     else:
#         flag = False
#         print("Opção invalida")
#     if (flag == True):
#         for x in results['hits']['hits']:
#             print(
#                 f"ID:{x['_souce']['indentificador']}\nTitle: {x['_source']['title']}\nCorpo: {x['_source']['content']}\n")
#             print('--------------------------------------------\n')

es.indices.delete(index=index_diretorio)
