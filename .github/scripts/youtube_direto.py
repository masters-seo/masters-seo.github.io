#!/usr/bin/env python3
import os
import sys
import requests
import re
import json
import html as html_parser
from google import genai

def obter_legenda_humana(video_id):
    print(f"🔤 Simulando acesso humano para extrair legenda do ID: {video_id}...")
    
    # Headers complexos que imitam perfeitamente um navegador real atualizado
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        url_video = f"https://www.youtube.com/watch?v={video_id}"
        sessao = requests.Session()
        html_pagina = sessao.get(url_video, headers=headers, timeout=20).text
        
        # Procura os dados internos de legenda injetados na timeline do vídeo
        if "captionTracks" not in html_pagina:
            print(f"⚠️ O YouTube escondeu a timeline de legendas para o robô no vídeo {video_id}.")
            return None
            
        match = re.search(r'"captionTracks":\s*(\[.*?\])', html_pagina)
        if not match:
            print(f"⚠️ Falha ao decodificar a estrutura de faixas do vídeo {video_id}.")
            return None
            
        tracks = json.loads(match.group(1))
        
        # Tenta selecionar a faixa em português, se não achar, usa a primeira (geralmente inglês/automática)
        url_legenda = tracks[0]["baseUrl"]
        for track in tracks:
            if track.get("languageCode") == "pt" or "pt" in track.get("baseUrl", ""):
                url_legenda = track["baseUrl"]
                break
                
        # Baixa os blocos de texto da legenda estruturada
        resposta_legenda = sessao.get(url_legenda, headers=headers, timeout=20).text
        
        # Extrai o texto limpo de dentro das tags XML <text> do YouTube
        blocos_texto = re.findall(r'<text[^>]*>([\s\S]*?)</text>', resposta_legenda)
        
        if not blocos_texto:
            print(f"⚠️ O arquivo de legenda do vídeo {video_id} veio sem conteúdo legível.")
            return None
            
        # Junta tudo, limpa códigos HTML e quebras de linha espalhadas
        texto_completo = " ".join([html_parser.unescape(b) for b in blocos_texto])
        texto_completo = re.sub(r'\s+', ' ', texto_completo).strip()
        
        print(f"✅ Transcrição extraída com sucesso! ({len(texto_completo)} caracteres).")
        return texto_completo

    except Exception as e:
        print(f"❌ Erro na simulação humana para {video_id}: {e}")
        return None

def gerar_artigo(transcricao, video_id):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Erro: A variável de ambiente GEMINI_API_KEY não foi configurada.")
        return False

    print("🤖 Enviando dados limpos para a inteligência do Gemini...")
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
            
        print(f"🎉 SUCESSO ABSOLUTO! Artigo gerado e salvo em: {caminho_arquivo}")
        return True
    except Exception as e:
        print(f"❌ Erro na geração do Gemini: {e}")
        return False

if __name__ == '__main__':
    # Lista contendo o vídeo do Neil Patel (que sabidamente possui trilhas estáveis de texto)
    VIDEOS_TESTE = ["WQHJcSiTc7s", "k8aFgaUTe_I"]
    
    texto_legenda = None
    video_id_sucesso = None
    
    for v_id in VIDEOS_TESTE:
        texto_legenda = obter_legenda_humana(v_id)
        if texto_legenda:
            video_id_sucesso = v_id
            break
        print("-" * 40)

    if texto_legenda and video_id_sucesso:
        if not gerar_artigo(texto_legenda, video_id_sucesso):
            sys.exit(1)
    else:
        print("🛑 [Proteção de Créditos]: Nenhuma legenda pôde ser extraída por simulação. Abortando execução para salvar tokens.")
        sys.exit(0)
