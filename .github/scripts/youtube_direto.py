
#!/usr/bin/env python3
import sys
# Remove o diretório local do topo da fila de busca do Python
if "" in sys.path: sys.path.remove("")
if "." in sys.path: sys.path.remove(".")
# Remove o diretório do próprio script da fila para não importar arquivos fantasmas vizinhos
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path: sys.path.remove(script_dir)

# AGORA SIM OS IMPORTS OFICIAIS:
import requests
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
# ... resto do código igual ...
import os
import sys
import requests
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

def obter_legenda(video_id):
    print(f"🔤 Buscando transcrição para o ID: {video_id}...")
    try:
        # Método direto e oficial documentado na biblioteca
        lista = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        texto_completo = " ".join([item['text'] for item in lista])
        print(f"✅ Transcrição obtida com sucesso ({len(texto_completo)} caracteres).")
        return texto_completo
    except Exception as e:
        print(f"❌ Erro ao coletar transcrição: {e}")
        return None

def gerar_artigo(transcricao, video_id):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Erro: A variável de ambiente GEMINI_API_KEY não foi configurada.")
        return False

    print("🤖 Conectando à API do Gemini...")
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""Você é um especialista em SEO. Crie um artigo completo, longo e estruturado em Markdown com base na seguinte transcrição de vídeo. Use subtítulos H2 e H3, parágrafos curtos e inclua uma seção de FAQ no final. Não inclua delimitadores Front Matter (como ---).

Transcrição:
{transcricao}"""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        conteúdo = response.text.strip()
        
        # Estrutura o Markdown com Front Matter básico para o Jekyll
        front_matter = f"""---
layout: post
title: 'Análise de SEO Avançada - Vídeo {video_id}'
date: 2026-07-03 12:00:00 -0300
categories: 'Análises'
tags: [seo, marketing-digital]
youtube_id: {video_id}
---

<div class="youtube-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 35px 0; border-radius: 8px;">
  <iframe src="https://www.youtube.com/embed/{video_id}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>
</div>

"""
        markdown_final = front_matter + conteúdo
        
        # Garante a existência da pasta e salva
        os.makedirs('_posts', exist_ok=True)
        caminho_arquivo = f"_posts/2026-07-03-analise-seo-{video_id}.md"
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(markdown_final)
            
        print(f"🎉 Artigo gerado com sucesso e salvo em: {caminho_arquivo}")
        return True
    except Exception as e:
        print(f"❌ Erro na geração do Gemini: {e}")
        return False

if __name__ == '__main__':
    # ID do vídeo do RankMath que você está tentando processar
    ID_DO_VIDEO = "VBRgIcXIxB0" 
    
    texto_legenda = obter_legenda(ID_DO_VIDEO)
    if texto_legenda:
        sucesso = gerar_artigo(texto_legenda, ID_DO_VIDEO)
        if not sucesso:
            sys.exit(1)
    else:
        sys.exit(1)
