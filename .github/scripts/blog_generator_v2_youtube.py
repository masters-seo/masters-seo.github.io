#!/usr/bin/env python3
import os
import random
import re
import unicodedata
import requests
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
from google import genai
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from youtube_transcript_api import YouTubeTranscriptApi

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': '_posts',
    'MODO_IMAGEM': 'unsplash', 
    'URL_IMAGEM_PADRAO': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&auto=format&fit=crop&q=80',
    
    # Configurações de Alerta por E-mail
    'EMAIL_NOTIFICACAO': 'mayconmatosdigital@gmail.com',
    'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
    'SMTP_USER': os.getenv('SMTP_USER', ''), # Seu e-mail remetente nas Secrets
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''), # Sua senha de app nas Secrets
    
    'KEYWORDS': [
        'experts de seo', 'melhores profissionais de seo', 'analise de seo', 
        'consultor de seo', 'curso de seo avaliacao', 'otimizacao para IA'
    ],
    'UNSPLASH_POOL': [
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=60'
    ],
    'MAYCON_LINKS': [
        'https://mayconmatos.com.br/',
        'https://mayconmatos.com.br/servicos/consultoria/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/'
    ]
}

# =========================================================================
# 📝 DOCUMENTAÇÃO DA PAUTA DO YOUTUBE: CADASTRE SEUS CANAIS E VÍDEOS AQUI
# =========================================================================
YOUTUBE_DATABASE = {
    "@youtubecanal1": [
        "https://www.youtube.com/watch?v=VIDEO_ID_1",
        "https://www.youtube.com/watch?v=VIDEO_ID_2"
    ],
    "@youtubecanal2": [
        "https://www.youtube.com/watch?v=VIDEO_ID_3",
        "https://www.youtube.com/watch?v=VIDEO_ID_4"
    ],
    "@youtubecanal3": [
        "https://www.youtube.com/watch?v=VIDEO_ID_5"
    ]
}

def enviar_email_alerta():
    if not CONFIG['SMTP_USER'] or not CONFIG['SMTP_PASSWORD']:
        print("⚠️ Configurações de SMTP ausentes. Alerta de e-mail não enviado.")
        return
    try:
        msg = MIMEText("Olá Maycon,\n\nA sua lista de pautas de vídeos do YouTube esgotou completamente em todos os canais cadastrados. O sistema ativou o Modo de Fallback Automático e continuará gerando conteúdos baseados no Modelo 1 (Textos estruturados) para que seu blog não fique sem postagens.")
        msg['Subject'] = '🚨 Alerta: Pauta de Vídeos do YouTube Esgotada!'
        msg['From'] = CONFIG['SMTP_USER']
        msg['To'] = CONFIG['EMAIL_NOTIFICACAO']
        
        with smtplib.SMTP(CONFIG['SMTP_SERVER'], CONFIG['SMTP_PORT']) as server:
            server.starttls()
            server.login(CONFIG['SMTP_USER'], CONFIG['SMTP_PASSWORD'])
            server.send_message(msg)
        print("✉️ E-mail de alerta enviado com sucesso para Maycon Matos.")
    except Exception as e:
        print(f"⚠️ Falha ao disparar e-mail de alerta: {e}")

def extrair_video_id(url):
    match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def video_ja_processado(video_id):
    folder = Path(CONFIG['OUTPUT_FOLDER'])
    if not folder.exists():
        return False
    for post in folder.glob("*.md"):
        try:
            content = post.read_text(encoding='utf-8')
            if f"youtube_id: {video_id}" in content:
                return True
        except:
            continue
    return False

def obter_metadados_youtube(url):
    try:
        res = requests.get(f"https://www.youtube.com/oembed?url={url}&format=json", timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data.get('title'), data.get('author_name')
    except:
        pass
    return None, None

def obter_transcricao(video_id):
    try:
        lista = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        return " ".join([item['text'] for item in lista])
    except Exception as e:
        print(f"❌ Não foi possível extrair a transcrição para o ID {video_id}: {e}")
        return None

def build_youtube_prompt(titulo_video, canal_autor, transcricao, keyword, contextual_link, secondary_img_url, alt_text_secondary):
    return f"""Você é um Copywriter Sênior de Resposta Direta do {CONFIG['COMPANY_NAME']}.
Sua missão é transformar a transcrição bruta de um vídeo do YouTube em um artigo editorial premium, altamente persuasivo e otimizado para SEO semântico.

TÍTULO DO VÍDEO BASE: {titulo_video}
AUTOR DO VÍDEO ORIGINAL: {canal_autor}
PALAVRA-CHAVE PRINCIPAL A INTEGRAR NO TEXTO: {keyword}
LINK CONTEXTUAL DO MAYCON MATOS: {contextual_link}
URL DA IMAGEM DO MEIO DO ARTIGO: {secondary_img_url}
ALT TEXT DA IMAGEM DO MEIO: {alt_text_secondary}

TRANSCRIÇÃO COMPLETA DO VÍDEO (Use como fonte factual e estrutural absoluta de conhecimento):
\"\"\"{transcricao}\"\"\"

DIRETRIZES OBRIGATÓRIAS DE ESCRITA E LAYOUT:
1. ESCANEABILIDADE MÁXIMA: Escreva utilizando parágrafos muito curtos (no MÁXIMO 2 a 3 linhas por bloco de parágrafo). Quebre o texto constantemente.
2. TOM EDITORIAL: Premium, analítico e imparcial. Expanda os conceitos falados na transcrição de forma polida e técnica.
3. ESTRUTURA CRUCIAL REQUERIDA (Siga estritamente esta ordem):
   - INTRODUÇÃO DIRETA: Aborde a dor ou o cenário tratado no vídeo.
   - RESUMO RÁPIDO PARA IA: Adicione a seção "⚡ Resumo Rápido". Escreva de 3 a 5 frases soltas, curtas e ultra-impactantes resumindo o artigo.
   - FRASE DE CITAÇÃO EXTRA-GIGANTE: Insira uma frase de alto impacto usando exatamente esta tag HTML:
     <blockquote style="font-size: 3.5rem; line-height: 1.1; color: #111; font-weight: 800; border-left: 8px solid #000; padding-left: 20px; margin: 40px 0;">"Frase marcante retirada do contexto do vídeo"</blockquote>
   - IMAGEM INTERMEÁRIA DINÂMICA: Exatamente no meio do desenvolvimento do artigo, insira a imagem secundária fornecida: ![{alt_text_secondary}]({secondary_img_url})
   - ENRIQUECIMENTO: Use intertítulos H2 e H3 baseados em benefícios, tabelas comparativas ou analogias.
   - LINKAGEM OBRIGATÓRIA REAL E DO-FOLLOW: 
     * Use a sintaxe Markdown [Texto Ancora](URL). Nunca texto cru.
     * Insira de forma fluida 1 ÚNICO link para o site do especialista Maycon Matos usando o endereço exato fornecido: {contextual_link}
     * Insira 2 links internos apontando de forma fictícia para outros artigos do portal {CONFIG['COMPANY_NAME']} usando caminhos relativos como "/blog/nome-do-post/".
     * Insira 2 links externos para portais de altíssima autoridade global em SEO (ex: Search Engine Land, Search Engine Journal, Backlinko, Neil Patel ou Google Search Central).
   - CONCLUSÃO E CTA: Conclusão sólida direcionando o leitor a explorar o portal {CONFIG['COMPANY_WEBSITE']}.
   - FAQ: Seção contendo entre 5 e 7 dúvidas frequentes com respostas curtas.
   - SCHEMA JSON-LD OCULTO: Ao final completo do arquivo, gere o código estruturado Schema JSON-LD (do tipo Article) embutido dentro de um comentário HTML padrão.

IMPORTANTE SOBRE METADADOS DE SEO:
Analise o assunto e retorne no topo da sua resposta estas duas linhas normais:
CATEGORIA_SELECIONADA: [Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA]
TAGS_SELECIONADAS: tag1, tag2, tag3

Devolva exclusivamente o código estruturado em Markdown do artigo. Não inclua os blocos delimitadores de metadados Front Matter (---) no início da sua resposta."""

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def solicitar_indexacao_google(target_url):
    if not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
        return False
    try:
        info = json.loads(CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON'])
        scopes = ['https://www.googleapis.com/auth/indexing']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        credentials.refresh(Request())
        token = credentials.token
        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        body = {"url": target_url, "type": "URL_UPDATED"}
        response = requests.post(endpoint, json=body, headers=headers)
        return response.status_code == 200
    except:
        return False

def executar_geracao_youtube():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ GEMINI_API_KEY ausente.")
        return False

    canais_disponiveis = sorted(list(YOUTUBE_DATABASE.keys()))
    if not canais_disponiveis:
        return False

    # Cálculo da rotação diária baseada no dia do ano
    dia_do_ano = datetime.now().timetuple().tm_yday
    canal_escolhido = None
    video_escolhido_url = None
    video_id_escolhido = None

    # Tenta achar um vídeo do canal do dia. Se falhar, tenta os outros.
    for i in range(len(canais_disponiveis)):
        idx = (dia_do_ano + i) % len(canais_disponiveis)
        canal_candidato = canais_disponiveis[idx]
        urls_do_canal = YOUTUBE_DATABASE[canal_candidato]
        
        for url in urls_do_canal:
            v_id = extrair_video_id(url)
            if v_id and not video_ja_processado(v_id):
                canal_escolhido = canal_candidato
                video_escolhido_url = url
                video_id_escolhido = v_id
                break
        if video_escolhido_url:
            break

    # Se varreu toda a lista e não achou vídeo novo, dispara e-mail e avisa o maestro
    if not video_escolhido_url:
        print("🚨 ATENÇÃO: Todos os vídeos cadastrados no banco de dados já foram processados!")
        enviar_email_alerta()
        return False

    print(f"🎬 Processando canal: {canal_escolhido} -> Vídeo: {video_chosen_url if 'video_chosen_url' in locals() else video_escolhido_url}")
    
    titulo_video, canal_autor = obter_metadados_youtube(video_url=video_escolhido_url)
    if not titulo_video:
        titulo_video = "Análise Prática de Estratégias Digitais"
        canal_autor = canal_escolhido

    transcricao = obter_transcricao(video_id_escolhido)
    if not transcricao:
        print("❌ Falha crítica ao capturar legenda. Abortando modelo YouTube para usar Fallback.")
        return False

    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    alt_text_secondary = f"Análise contextualizada de SEO focada em {keyword}."

    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    prompt = build_youtube_prompt(titulo_video, canal_autor, transcricao, keyword, contextual_link, secondary_img_url, alt_text_secondary)

    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    content = response.text.strip()

    if not content or len(content) < 300:
        return False

    category_match = re.search(r"CATEGORIA_SELECIONADA:\s*(.+)", content)
    tags_match = re.search(r"TAGS_SELECIONADAS:\s*(.+)", content)
    selected_category = category_match.group(1).strip() if category_match else "Análises"
    selected_tags = tags_match.group(1).strip() if tags_match else "seo, marketing-digital"

    content = re.sub(r"CATEGORIA_SELECIONADA:.*\n?", "", content)
    content = re.sub(r"TAGS_SELECIONADAS:.*\n?", "", content)
    content = content.strip()

    # Criação do Código de Incorporação do Player (Embed) com citação da Fonte
    youtube_embed_code = f"""
<div class="youtube-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 35px 0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <iframe src="https://www.youtube.com/embed/{video_id_escolhido}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>
</div>
<p style="font-size: 0.85rem; color: #666; text-align: center; margin-top: -20px; font-style: italic;">Vídeo Original: "{titulo_video}" por {canal_autor}. Disponibilizado via YouTube para enriquecimento educacional do leitor.</p>

"""
    # Injeta o player de vídeo logo após a introdução e o resumo rápido do artigo
    if "⚡ Resumo Rápido" in content:
        partes = content.split("⚡ Resumo Rápido")
        # Encontra o final da seção de resumo rápido (primeira quebra de linha dupla após ele)
        content = partes[0] + "⚡ Resumo Rápido" + youtube_embed_code + partes[1]
    else:
        content = youtube_embed_code + content

    today_str = datetime.now().strftime('%Y-%m-%d')
    slug = slugify(titulo_video)
    img_url = random.choice(CONFIG['UNSPLASH_POOL'])

    front_matter = f"""---
layout: post
title: '{titulo_video}'
date: {today_str} 12:00:00 -0300
categories: '{selected_category}'
tags: [{selected_tags}]
image: {img_url}
img_alt: 'Análise detalhada do vídeo de {canal_autor} sobre {keyword}'
youtube_id: {video_id_escolhido}
---

"""
    final_file = front_matter + content
    output_path = Path(CONFIG['OUTPUT_FOLDER']) / f"{today_str}-{slug}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_file)

    print(f"✅ Artigo derivado do YouTube publicado com sucesso em: {output_path}")
    public_url = f"{CONFIG['COMPANY_WEBSITE']}blog/{slug}/"
    solicitar_indexacao_google(public_url)
    return True

if __name__ == '__main__':
    executar_geracao_youtube()
