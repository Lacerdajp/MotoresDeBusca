from pathlib import Path
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from whoosh.scoring import BM25F
import timeit
import shutil
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


def limparLixo(string):

    antesLimpeza = timeit.default_timer()
    saida = string.replace("\n", " ").replace(
        ".B", "").replace(".W", "").replace("the ", "").replace("an ", "").replace("a ", "").strip()
    depoisLimpeza = timeit.default_timer()

    tempoLimpeza = depoisLimpeza - antesLimpeza
    return saida


def limparQuery(string):
    saida = string.replace("\n", " ").replace(
        "the ", "").replace("an ", "").replace("a ", "").strip()
    return saida


def lerColecao(path):

    antesLeitura = timeit.default_timer()
    with open(path, "r") as file:
        f = file.read()
    depoisLeitura = timeit.default_timer()

    tempoLeitura = depoisLeitura - antesLeitura
    return f.split(".I")[1:]


def VerificaDiretorioIndex(index_diretorio, schema):
    tempoCriacao = 0
    tempoAbertura = 0
    if index_diretorio.exists():
        print("Diretório de indexação já existe, abrindo...")
        tempoAbertura = timeit.default_timer()
        index = open_dir(index_diretorio)
        tempoAbertura = timeit.default_timer() - tempoAbertura
        print("Tempo de abertura do diretório de indexação: " + str(tempoAbertura))
    else:
        print("Criando diretório de indexação...")
        tempoCriacao = timeit.default_timer()
        index_diretorio.mkdir()
        index = create_in(index_diretorio, schema)
        tempoCriacao = timeit.default_timer() - tempoCriacao
    print("Tempo de criação do diretório de indexação: " + str(tempoCriacao))
    return index


def lerDiretorioIndex(index, arquivo):
    tempoIndexacao = timeit.default_timer()
    writer = index.writer()
    for linha in lerColecao(arquivo):
        content = limparLixo(linha)
        i = ''.join(content.split(" .T")[:1])
        title = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[:1])
        content = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[1:])
        writer.add_document(index=i, title=title, content=content)
    writer.commit()
    tempoIndexacao = timeit.default_timer() - tempoIndexacao
    return tempoIndexacao


def realizarBusca(index, searcher, busca, tipoBusca, numeroResultados):
    tempoBusca = timeit.default_timer()
    query = MultifieldParser(tipoBusca, index.schema).parse(busca)
    results = searcher.search(query, limit=numeroResultados)
    tempoBusca = timeit.default_timer()-tempoBusca
    return results, tempoBusca


def plotarGRaficos(nome, x, y, namex, namey):
    plt.plot(x, y, color='red')
    plt.xlabel(namex)
    plt.ylabel(namey)
    plt.show()


arquivo = "DataSets/cran.all.1400"
index_diretorio = Path("/Whoosh")
shutil.rmtree(index_diretorio)
schema = Schema(index=TEXT(stored=True), title=TEXT(
    stored=True), content=TEXT(stored=True))
index = VerificaDiretorioIndex(index_diretorio, schema)
tempoIndexacao = lerDiretorioIndex(index, arquivo)
# Caso queira Habiilitar a busca Manual descomente esse codigo e ajuste a identação:
# tipo_teste = int(
#     input("Digite o tipo de teste:\n1.Teste Automatico\n2.Teste Manual\n"))
# if (tipo_teste == 2):
#     searcher = index.searcher()
#     while True:
#         escolha = input("Deseja realizar uma busca? (S/N): ")
#         if (escolha == "N"):
#             break
#         elif (escolha == "S"):
#             tipoBusca = int(input(
#                 "Digite o tipo de busca (Linha ou Texto):\n1.Numero Estudo\n2.Conteudo\n3.Titulo\n "))
#             if (tipoBusca == 2):
#                 busca = input("Digite o conteudo de busca: ")
#                 numeroResultados = int(
#                     input("Digite o número de resultados: "))
#                 results = realizarBusca(index, searcher, busca,
#                                         ["content"], numeroResultados)
#                 for result in results:
#                     content_value = result.get("content")
#                     linha_value = result.get("index")
#                     title_value = result.get("title")
#                     score = result.score
#                     print(
#                         f"Index: {linha_value}-SCORE:{score}\nTitle:{title_value}\nTexto: {content_value}")
#                     print("----------------------\n")
#             elif (tipoBusca == 1):
#                 busca = input("Digite o numero da linha: ")
#                 results = realizarBusca(index, searcher, busca, ["index"], 1)
#                 for result in results:
#                     content_value = result.get("content")
#                     linha_value = result.get("index")
#                     title_value = result.get("title")
#                     score = result.score
#                     print(
#                         f"Index: {linha_value}-SCORE:{score}\nTitle:{title_value}\nTexto: {content_value}")
#                     print("----------------------\n")
#             elif (tipoBusca == 3):
#                 busca = input("Digite o parte do Titulo do estudo: ")
#                 results = realizarBusca(index, searcher, busca,
#                                         ["title"], 1)
#                 for result in results:
#                     content_value = result.get("content")
#                     linha_value = result.get("index")
#                     title_value = result.get("title")
#                     score = result.score
#                     print(
#                         f"Index: {linha_value}-SCORE:{score}\nTitle:{title_value}\nTexto: {content_value}")
#                     print("----------------------\n")
#             else:
#                 print("Tipo de busca inválido!")
# elif (tipo_teste == 1):
queryArquivo = "DataSets/cran.qry"
arquivoResposta = open("Respostas/respostasCran.txt", "a")
arquivoResposta.truncate(0)
searcher = index.searcher(weighting=BM25F())
precision = []
recall = []
tempoBusca = []
perguntas = []
docsRelev = []
docs = []
for x, linha in enumerate(lerColecao(queryArquivo)):
    doc = []
    perguntas.append(x+1)
    busca = limparQuery(linha)
    i = ''.join(busca.split(" .W ")[:1])
    busca = ''.join(busca.split(" .W ")[1:])
    buscarOR = busca.replace(" ", " OR ")
    results, temp = realizarBusca(
        index, searcher, buscarOR, ["content", "title"], 10)
    for (result) in results:
        doc.append(result.get('index'))
        arquivoResposta.write(
            f"Linha={x+1}-ID Questao:{i}- ID Documento: {result.get('index')}-Score: {result.score}\n")
        arquivoResposta.write(f"Pergunta: {busca}\n")
        arquivoResposta.write(f"Resposta: {result.get('title')}\n")
        arquivoResposta.write(
            "-------------------------------------------------\n")
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
plotarGRaficos("Grafico de Recall X K Whoosh", y=recall,
               x=[linha+1 for linha in range(10)], namex="k", namey="Recall")
plotarGRaficos("Grafico de Precision X K Whoosh", y=precision,
               x=[linha+1 for linha in range(10)], namex="k", namey="Precision")

arquivoResposta.close()
index.close()
