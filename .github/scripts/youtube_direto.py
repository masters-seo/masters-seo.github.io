#!/usr/bin/env python3
import os
import sys
import requests
import xml.etree.ElementTree as ET
from googleapiclient.discovery import build
from google import genai

def obter_legenda_oficial(video_id):
    print(f"🔤 Chamando API Oficial do YouTube para o ID: {video_id}...")
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    
    if not youtube_key:
        print("❌ Erro: A variável YOUTUBE_API_KEY não foi configurada nos Secrets.")
        return None

    try:
        # Inicializa o cliente oficial do YouTube
        youtube = build('youtube', 'v3', developerKey=youtube_key)
        
        # 1. Lista as legendas disponíveis para o vídeo
        request = youtube.captions().list(part="snippet", videoId=video_id)
        response = request.execute()
        
        items = response.get('items', [])
        if not items:
            print(f"⚠️ Nenhuma legenda oficial/rastreável encontrada para o vídeo {video_id}.")
            return None
            
        # Seleciona o ID da primeira legenda disponível (prioriza português se achar)
        caption_id = items[0]['id']
        for item in items:
            if item['snippet'].get('language') == 'pt':
                caption_id = item['id']
                break
        
        # 2. Baixa o arquivo de legenda bruto
        download_request = youtube.captions().download(id=caption_id, tfmt='srt')
        legenda_bruta = download_request.execute().decode('utf-8')
        
        # Limpa as marcações de tempo do formato SRT para deixar apenas o texto limpo
        linhas = legenda_bruta.split('\n')
        texto_limpo = []
        for linha in linhas:
            linha = linha.strip()
            if linha.isdigit() or '-->' in linha or not linha:
                continue
            texto_limpo.append(linha)
            
        resultado = " ".join(texto_limpo)
        print(f"✅ Transcrição obtida via API Oficial ({len(resultado)} caracteres).")
        return resultado

    except Exception as e:
        print(f"⚠️ A API do YouTube retornou um erro ou restrição para este vídeo: {e}")
        return None

def gerar_artigo(transcricao, video_id):
    api_key = os.getenv('GEMINI_API_KEY')
    print("🤖 Conectando à API do Gemini para criar o artigo...")
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"Você é um especialista em SEO. Crie um artigo completo, longo e estruturado em Markdown com base na seguinte transcrição de vídeo. Use subtítulos H2 e H3, parágrafos curtos e inclua uma seção de FAQ no final. Não inclua delimitadores Front Matter (como ---).\n\nTranscrição:\n{transcricao}"
        
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        conteudo = response.text.strip()
        
        front_matter = f"---\nlayout: post\ntitle: 'Insights de SEO Avançado - Vídeo {video_id}'\ndate: 2026-07-03 12:00:00 -0300\ncategories: 'Análises'\ntags: [seo, marketing-digital]\nyoutube_id: {video_id}\n---\n\n"
        
        os.makedirs('_posts', exist_ok=True)
        caminho_arquivo = f"_posts/2026-07-03-analise-seo-{video_id}.md"
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(front_matter + conteudo)
            
        print(f"🎉 SUCESSO! Artigo gerado e salvo em: {caminho_arquivo}")
        return True
    except Exception as e:
        print(f"❌ Erro na geração do Gemini: {e}")
        return False

if __name__ == '__main__':
    # IDs de canais grandes que sempre deixam legendas oficiais ativas
    VIDEOS_TESTE = ["WQHJcSiTc7s", "VBRgIcXIxB0"]
    
    texto_legenda = None
    video_id_sucesso = None
    
    for v_id in VIDEOS_TESTE:
        texto_legenda = obter_legenda_oficial(v_id)
        if texto_legenda:
            video_id_sucesso = v_id
            break
        print("-" * 40)

    if texto_legenda and video_id_sucesso:
        if not gerar_artigo(texto_legenda, video_id_sucesso):
            sys.exit(1)
    else:
        print("🛑 [Proteção de Créditos]: Nenhuma legenda oficial pôde ser extraída. Processo encerrado de forma segura.")
        sys.exit(0)
