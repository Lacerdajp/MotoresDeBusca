from pathlib import Path
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, NUMERIC
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, OrGroup
from whoosh.scoring import BM25F
import timeit
import shutil


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
    if index_diretorio.exists():
        print("Diretório de indexação já existe, abrindo...")
        index = open_dir(index_diretorio)
    else:
        print("Criando diretório de indexação...")
        index_diretorio.mkdir()
        index = create_in(index_diretorio, schema)
    return index


def lerDiretorioIndex(index, arquivo):
    writer = index.writer()
    for linha in lerColecao(arquivo):
        content = limparLixo(linha)
        i = ''.join(content.split(" .T")[:1])
        title = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[:1])
        content = ''.join(''.join(content.split(" .T ")[1:]).split(" .A ")[1:])
        writer.add_document(index=i, title=title, content=content)
    writer.commit()


def realizarBusca(index, searcher, busca, tipoBusca, numeroResultados):
    query = QueryParser(tipoBusca, index.schema).parse(busca)
    results = searcher.search(query, limit=numeroResultados)
    return results


arquivo = "DataSets/cran.all.1400"
index_diretorio = Path("/Whoosh")
shutil.rmtree(index_diretorio)
schema = Schema(index=TEXT(stored=True), title=TEXT(
    stored=True), content=TEXT(stored=True))
index = VerificaDiretorioIndex(index_diretorio, schema)
lerDiretorioIndex(index, arquivo)
tipo_teste = int(
    input("Digite o tipo de teste:\n1.Teste Automatico\n2.Teste Manual\n"))
if (tipo_teste == 2):
    searcher = index.searcher()
    while True:
        escolha = input("Deseja realizar uma busca? (S/N): ")
        if (escolha == "N"):
            break
        elif (escolha == "S"):
            tipoBusca = int(input(
                "Digite o tipo de busca (Linha ou Texto):\n1.Numero Estudo\n2.Conteudo\n3.Titulo\n "))
            if (tipoBusca == 2):
                busca = input("Digite o conteudo de busca: ")
                numeroResultados = int(
                    input("Digite o número de resultados: "))
                results = realizarBusca(index, searcher, busca,
                                        "content", numeroResultados)
                for result in results:
                    content_value = result.get("content")
                    linha_value = result.get("index")
                    title_value = result.get("title")
                    score = result.score
                    print(
                        f"Index: {linha_value}-SCORE:{score}\nTitle:{title_value}\nTexto: {content_value}")
                    print("----------------------\n")
            elif (tipoBusca == 1):
                busca = input("Digite o numero da linha: ")
                results = realizarBusca(index, searcher, busca, "index", 1)
                for result in results:
                    content_value = result.get("content")
                    linha_value = result.get("index")
                    title_value = result.get("title")
                    score = result.score
                    print(
                        f"Index: {linha_value}-SCORE:{score}\nTitle:{title_value}\nTexto: {content_value}")
                    print("----------------------\n")
            elif (tipoBusca == 3):
                busca = input("Digite o parte do Titulo do estudo: ")
                results = realizarBusca(index, searcher, busca,
                                        "title", 1)
                for result in results:
                    content_value = result.get("content")
                    linha_value = result.get("index")
                    title_value = result.get("title")
                    score = result.score
                    print(
                        f"Index: {linha_value}-SCORE:{score}\nTitle:{title_value}\nTexto: {content_value}")
                    print("----------------------\n")
            else:
                print("Tipo de busca inválido!")
elif (tipo_teste == 1):
    queryArquivo = "DataSets/cran.qry"
    arquivoResposta = open("Respostas/respostasCran.txt", "a")
    arquivoResposta.truncate(0)
    searcher = index.searcher(weighting=BM25F())
    for x, linha in enumerate(lerColecao(queryArquivo)):

        busca = limparQuery(linha)
        i = ''.join(busca.split(" .W ")[:1])
        busca = ''.join(busca.split(" .W ")[1:])
        buscarOR = busca.replace(" ", " OR ")
        results = realizarBusca(
            index, searcher, buscarOR, "content", 10)
        for (result) in results:
            arquivoResposta.write(
                f"Linha={x+1}-ID Questao:{i}- ID Documento: {result.get('index')}-Score: {result.score}\n")
            arquivoResposta.write(f"Pergunta: {busca}\n")
            arquivoResposta.write(f"Resposta: {result.get('title')}\n")
            arquivoResposta.write(
                "-------------------------------------------------\n")

    arquivoResposta.close()
index.close()
