#!/usr/bin/env python3
import os
import sys
import requests
import re
import json
from google import genai

def obter_legenda(video_id):
    print(f"🔤 Coletando transcrição nativa para o ID: {video_id}...")
    try:
        # Método alternativo usando a classe de listagem (TranscriptList) que o seu log mostrou que existe!
        from youtube_transcript_api import TranscriptList
        
        # Recupera os dados brutos usando os componentes internos que estão funcionando
        print("🔍 Acessando o buscador interno da API...")
        lista_transcricoes = TranscriptList.fetch(video_id)
        
        # Tenta pegar em português, senão pega em inglês
        try:
            transcricao = lista_transcricoes.find_transcript(['pt'])
        except:
            transcricao = lista_transcricoes.find_transcript(['en'])
            
        dados_brutos = transcricao.fetch()
        texto_completo = " ".join([item['text'] for item in dados_brutos])
        
        print(f"✅ Transcrição obtida com sucesso ({len(texto_completo)} caracteres).")
        return texto_completo
        
    except Exception as e:
        print(f"⚠️ Método primário falhou: {e}. Tentando raspagem direta via HTTP...")
        try:
            # Fallback 100% independente de bibliotecas externas (Raspagem Limpa)
            url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            html = requests.get(url, headers=headers, timeout=15).text
            
            # Localiza os dados de legenda escondidos no HTML do YouTube
            if "captionTracks" not in html:
                print("❌ O YouTube não disponibilizou legendas textuais públicas para este vídeo.")
                return None
                
            match = re.search(r'"captionTracks":\s*(\[.*?\])', html)
            if not match:
                return None
                
            tracks = json.loads(match.group(1))
            url_legenda = tracks[0]["baseUrl"]
            
            # Baixa o XML de legendas e limpa as tags HTML/XML
            xml_legenda = requests.get(url_legenda, headers=headers, timeout=15).text
            linhas = re.findall(r'<text[^>]*>([\s\S]*?)</text>', xml_legenda)
            
            import html as html_parser
            texto_limpo = " ".join([html_parser.unescape(l) for l in linhas])
            print(f"✅ Transcrição recuperada via HTTP ({len(texto_limpo)} caracteres).")
            return texto_limpo
        except Exception as e2:
            print(f"❌ Falha em todos os métodos de extração: {e2}")
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
    ID_DO_VIDEO = "VBRgIcXIxB0" 
    
    texto_legenda = obter_legenda(ID_DO_VIDEO)
    if texto_legenda:
        sucesso = gerar_artigo(texto_legenda, ID_DO_VIDEO)
        if not sucesso:
            sys.exit(1)
    else:
        sys.exit(1)
