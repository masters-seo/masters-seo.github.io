#!/usr/bin/env python3
import os
import sys
import requests
import re
import json
from google import genai

def obter_legenda(video_id):
    print(f"🔤 Verificando transcrição para o ID: {video_id}...")
    
    # Tentativa via Raspagem Direta HTTP (Mais estável para o GitHub Actions)
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        html = requests.get(url, headers=headers, timeout=15).text
        
        if "captionTracks" not in html:
            print(f"⚠️ O YouTube não possui nenhuma legenda disponível (nem automática) para o vídeo {video_id}.")
            return None
            
        match = re.search(r'"captionTracks":\s*(\[.*?\])', html)
        if not match:
            return None
            
        tracks = json.loads(match.group(1))
        # Prefere português, se não houver, pega a primeira disponível (geralmente inglês)
        url_legenda = tracks[0]["baseUrl"]
        for track in tracks:
            if 'langCode' in track and track['langCode'] == 'pt':
                url_legenda = track['baseUrl']
                break
        
        xml_legenda = requests.get(url_legenda, headers=headers, timeout=15).text
        linhas = re.findall(r'<text[^>]*>([\s\S]*?)</text>', xml_legenda)
        
        import html as html_parser
        texto_limpo = " ".join([html_parser.unescape(l) for l in linhas])
        
        # Remove marcações de tempo restantes ou textos vazios
        texto_limpo = re.sub(r'<[^>]*>', '', texto_limpo).strip()
        
        if len(texto_limpo) > 100:
            print(f"✅ Transcrição recuperada com sucesso ({len(texto_limpo)} caracteres).")
            return texto_limpo
        return None
    except Exception as e:
        print(f"❌ Erro técnico ao raspar o YouTube: {e}")
        return None

def gerar_artigo(transcricao, video_id):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Erro: A variável de ambiente GEMINI_API_KEY não foi configurada.")
        return False

    print("🤖 Conectando à API do Gemini para criar o artigo...")
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
title: 'Insights de SEO Avançado - Vídeo {video_id}'
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
            
        print(f"🎉 SUCESSO! Artigo gerado e salvo em: {caminho_arquivo}")
        return True
    except Exception as e:
        print(f"❌ Erro na geração do Gemini: {e}")
        return False

if __name__ == '__main__':
    # Lista de vídeos para teste. O primeiro (do RankMath) não tem legenda. 
    # O segundo (do Neil Patel) tem legenda e vai funcionar perfeitamente!
    VIDEOS_TESTE = ["VBRgIcXIxB0", "k8aFgaUTe_I"]
    
    texto_legenda = None
    video_id_sucesso = None
    
    for v_id in VIDEOS_TESTE:
        texto_legenda = obter_legenda(v_id)
        if texto_legenda:
            video_id_sucesso = v_id
            break
        print(f"⏭️ Pulando vídeo {v_id} e tentando o próximo da fila...")
        print("-" * 40)

    if texto_legenda and video_id_sucesso:
        sucesso = gerar_artigo(texto_legenda, video_id_sucesso)
        if not sucesso:
            sys.exit(1)
    else:
        print("🛑 [Proteção de Créditos]: Nenhum dos vídeos da fila possui legendas disponíveis. Processo encerrado sem gastar tokens.")
        # Sai com 0 para o GitHub Actions não marcar como "falha de sistema", já que foi apenas uma escolha de negócio
        sys.exit(0)
