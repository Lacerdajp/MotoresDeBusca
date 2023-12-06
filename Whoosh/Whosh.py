from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.index import create_in
from whoosh.qparser import QueryParser

# Criar o esquema do índice
schema = Schema(title=TEXT(stored=True), content=TEXT, path=ID(stored=True))

# Criar um diretório para armazenar o índice
index_dir = "exemplo_index"
ix = create_in(index_dir, schema)

# Adicionar documentos ao índice
writer = ix.writer()
writer.add_document(title=u"Documento 1",
                    content=u"Este é o conteúdo do Documento 1", path=u"/doc1")
writer.add_document(title=u"Documento 2",
                    content=u"Conteúdo do Documento 2", path=u"/doc2")
writer.commit()

# Consultar o índice
searcher = ix.searcher()
query = QueryParser("content", ix.schema).parse("conteúdo")
results = searcher.search(query)

# Exibir resultados
for result in results:
    print(result)

# Fechar os objetos de índice e pesquisa
searcher.close()
ix.close()
