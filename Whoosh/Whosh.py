from pathlib import Path
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, NUMERIC
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
import timeit
import shutil


def limparLixo(string):

    antesLimpeza = timeit.default_timer()
    saida = string.replace("\n", " ").replace(".T", "").replace(".A", "").replace(
        ".B", "").replace(".W", "").replace("the ", "").replace("an ", "").replace("a ", "").strip()
    depoisLimpeza = timeit.default_timer()

    tempoLimpeza = depoisLimpeza - antesLimpeza

#   print(f"LOG: Tempo de limpeza: {tempoLimpeza}")

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
    for i, linha in enumerate(lerColecao(arquivo)):
        content = limparLixo(linha)
        writer.add_document(title=i, content=content)
    writer.commit()


def realizarBusca(index, searcher, busca, tipoBusca, numeroResultados):
    query = QueryParser(tipoBusca, index.schema).parse(busca)
    results = searcher.search(query, limit=numeroResultados)
    for result in results:
        title_value = result.get("title")
        content_value = result.get("content")
        print(f"Linha {title_value} - Texto: {content_value}")
        print("----------------------\n")


arquivo = "DataSets/cran.all.1400"
index_diretorio = Path("/Whoosh")
# shutil.rmtree(index_diretorio)
schema = Schema(title=NUMERIC(stored=True), content=TEXT(stored=True))
index = VerificaDiretorioIndex(index_diretorio, schema)
lerDiretorioIndex(index, arquivo)
searcher = index.searcher()

while True:
    escolha = input("Deseja realizar uma busca? (S/N): ")
    if (escolha == "N"):
        break
    elif (escolha == "S"):
        tipoBusca = int(input(
            "Digite o tipo de busca (Linha ou Texto):\n1.Linha\n2.Texto\n "))
        if (tipoBusca == 1 or tipoBusca == 2):
            if (tipoBusca == 1):
                tipo = "title"
            else:
                tipo = "content"
            busca = input("Digite o conteudo de busca: ")
            numeroResultados = int(
                input("Digite o número de resultados: "))
            realizarBusca(index, searcher, busca, tipo, numeroResultados)
        else:
            print("Tipo de busca inválido!")
index.close()
