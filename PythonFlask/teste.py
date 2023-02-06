import urllib.request, json

# URL de filmes mais populares: 
url = "https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key=f77a1348eeabba3f19e8d5deb63f3452"

# Requisição para abrir a URL:
resposta = urllib.request.urlopen(url)

# Ler os dados que estão na URL:
dados = resposta.read()

# Converter os dados para o formato JSON:
jsondata = json.loads(dados)

# Retornar somente os resultados:
print(jsondata['results'])