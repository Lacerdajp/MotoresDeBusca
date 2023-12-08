from elasticsearch import Elasticsearch
import timeit
from dotenv import load_dotenv
import os


def VerificaDiretorioIndex(index_diretorio, es):
    if not es.indices.exists(index=index_diretorio):
        es.indices.create(index=index_diretorio)
        print("Indexando...")
        lerDiretorioIndex(index_diretorio, arquivo)


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


def lerDiretorioIndex(index_name, arquivo):
    for x, linha in enumerate(lerColecao(arquivo)):
        content = limparLixo(linha)
        index = x
        i = ''.join(content.split(" .T")[:1])
        title = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[:1])
        content = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[1:])
        doc = {
            'index': index,
            'identificador': i,
            'title': title,
            'content': content
        }
        es.index(index=index_name, id=index, body=doc)
        print(doc)


load_dotenv()

es = Elasticsearch(
    ['http://localhost:9200/'],
    basic_auth=(os.environ.get('ELASTIC_NAME'), os.environ.get('ELASTIC_PASSWORD')))
index_diretorio = "my_index"
arquivo = "DataSets/cran.all.1400"
VerificaDiretorioIndex(index_diretorio, es)
tipo_teste = int(
    input("Digite o tipo de teste:\n1.Teste Automatico\n2.Teste Manual\n"))
if (tipo_teste == 1):
    arquivo_query = "DataSets/cran.qry"
    arquivoResposta = open("Respostas/elasticRespostasCran.txt", "a")
    arquivoResposta.truncate(0)
    for x, linha in enumerate(lerColecao(arquivo_query)):
        busca = limparQuery(linha)
        i = ''.join(busca.split(" .W ")[:1])
        busca = ''.join(busca.split(" .W ")[1:])
        #buscarOR = busca.replace(" ", " OR ")
        results = es.search(index=index_diretorio,
                            body={
                                "query": {
                                    "match": {
                                        "content": busca
                                    }
                                }
                            }
                            )
        for hit in results['hits']['hits']:
            arquivoResposta.write(
                f"Linha:{x+1}-IDPergunta:{i}-IDDocumento:{hit['_source']['identificador']}-Score:{hit['_score']}\n")
            arquivoResposta.write(f"Pergunta:{busca}\n")
            arquivoResposta.write(f"Titulo:{hit['_source']['title']}\n")
            arquivoResposta.write(
                f"--------------------------------------------\n")
    arquivoResposta.close()
elif (tipo_teste == 2):
    tipoBusca = int(input(
        "Digite o tipo de busca (Linha ou Texto):\n1.Numero Estudo\n2.Conteudo\n3.Titulo\n "))
    if (tipoBusca == 2):
        busca = input("Digite o conteudo de busca: ")
        results = es.search(index=index_diretorio, body={
            "query": {"match": {"content": busca}}})
        flag = True

    elif (tipoBusca == 1):
        busca = input("Digite o numero da linha: ")
        results = results = results = es.search(index=index_diretorio, body={
            "query": {"match": {"identificador": busca}}})
        flag = True
    elif (tipoBusca == 3):
        busca = input("Digite o parte do Titulo do estudo: ")
        results = results = es.search(index=index_diretorio, body={
            "query": {"match": {"title": busca}}})
        flag = True
    else:
        flag = False
        print("Opção invalida")
    if (flag == True):
        for x in results['hits']['hits']:
            print(
                f"ID:{x['_souce']['indentificador']}\nTitle: {x['_source']['title']}\nCorpo: {x['_source']['content']}\n")
            print('--------------------------------------------\n')

# es.indices.delete(index=index_diretorio)
