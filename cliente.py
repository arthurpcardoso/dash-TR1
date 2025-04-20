"""
===============================
Cliente DASH (A ser desenvolvido pelos alunos)
===============================

Objetivo:
Implementar um cliente DASH que:

1. Baixe o manifesto do servidor
2. Liste as representações disponíveis
3. Meça a largura de banda atual da rede
4. Escolha a melhor qualidade de vídeo com base na largura de banda
5. Baixe o segmento de vídeo da qualidade escolhida
6. Mostre os dados coletados e salve o segmento localmente

💡 Dica: Utilize Wireshark para capturar os pacotes da execução e observar:
   - A requisição ao manifesto
   - O segmento de vídeo baixado
   - O tempo da transferência para calcular a largura de banda

"""

# Exemplo de biblioteca útil:
import requests
import time

# URL do manifesto (use 127.0.0.1 em vez de localhost para evitar erros de permissão)
MANIFEST_URL = "http://127.0.0.1:5000/manifest.mpd"

def baixar_manifesto():
    """
    Função 1: Fazer uma requisição GET ao manifesto
    - Obter o JSON com as representações de vídeo
    - Retornar o dicionário com as informações do manifesto
    """
    
    try:
        resposta = requests.get(MANIFEST_URL)
        resposta.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        manifesto = resposta.json()
        return manifesto
    except requests.RequestException as e:
        print(f"Erro ao baixar o manifesto: {e}")
        return None
    

def medir_largura_de_banda(url_segmento_teste):
    """
    Função 2: Medir a largura de banda
    - Baixar um segmento pequeno (ex: 360p)
    - Medir o tempo da transferência
    - Calcular a largura de banda em Mbps: (tamanho_bytes * 8) / (tempo * 1_000_000)
    - Retornar a largura de banda medida
    """
    inicio = time.time()
    resposta = requests.get(url_segmento_teste, stream=True)
    tamanho_bytes = int(resposta.headers.get('Content-Length', 0))
    fim = time.time()
    
    print(f"Tamanho do segmento: {tamanho_bytes} bytes")
    
    tempo = fim - inicio
    largura_banda_mbps = (tamanho_bytes * 8) / tempo * 1_000_000
    return largura_banda_mbps

def selecionar_qualidade(manifesto, largura_banda_mbps):
    """
    Função 3: Escolher a melhor representação
    - Percorrer as representações disponíveis no manifesto
    - Comparar a largura de banda exigida por cada uma com a medida
    - Retornar a melhor representação suportada
    """
    
    melhor_representacao = None
    
    for representacao in manifesto['video']['representations']:
        largura_banda_representacao = representacao['bandwidth']
        if largura_banda_mbps >= largura_banda_representacao:
            if melhor_representacao is None or representacao['bandwidth'] > melhor_representacao['bandwidth']:
                melhor_representacao = representacao
    return melhor_representacao

def baixar_video(representacao):
    """
    Função 4: Baixar o segmento de vídeo escolhido
    - Fazer uma requisição GET para a URL da representação escolhida
    - Salvar o conteúdo em um arquivo local (ex: video_720p.mp4)
    """
    
    url = representacao['url']
    nome_arquivo = f"video_{representacao['id']}.mp4"
    
    try:
        resposta = requests.get(url, stream=True)
        resposta.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        
        with open(nome_arquivo, 'wb') as arquivo:
            for chunk in resposta.iter_content(chunk_size=8192):
                arquivo.write(chunk)
                
        print(f"Vídeo salvo como {nome_arquivo}")
    except requests.RequestException as e:
        print(f"Erro ao baixar o vídeo: {e}")
    

def main():
    """
     Função principal:
    - Chamar as funções na ordem correta
    - Exibir os dados na tela
    - Salvar o vídeo com a qualidade selecionada
    """
    
    manifesto = baixar_manifesto()
    if manifesto is None:
        print("Não foi possível baixar o manifesto.")
        return
    
    print("Manifesto baixado com sucesso.")
    print("Manifesto:", manifesto)
    
    # Medir a largura de banda
    url_segmento_teste = manifesto['video']['representations'][0]['url']
    largura_banda_mbps = medir_largura_de_banda(url_segmento_teste)
    print(f"Largura de banda medida: {largura_banda_mbps:.2f} Mbps")
    # Selecionar a melhor qualidade
    
    melhor_representacao = selecionar_qualidade(manifesto, largura_banda_mbps)
    if melhor_representacao is None:
        print("Nenhuma representação adequada encontrada.")
        return
    
    print(f"Melhor representação escolhida: {melhor_representacao['id']} ({melhor_representacao['bandwidth'] / 1_000_000:.2f} Mbps)")
    # Baixar o vídeo
    baixar_video(melhor_representacao)
    print("Download do vídeo concluído.")

if __name__ == '__main__':
    main()
