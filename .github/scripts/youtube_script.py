#!/usr/bin/env python3
import os
import sys
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
import subprocess

# Limpa o cache do Python para evitar conflitos de caminhos locais no Runner
if 'youtube_transcript_api' in sys.modules:
    del sys.modules['youtube_transcript_api']

try:
    import youtube_transcript_api
    from youtube_transcript_api import YouTubeTranscriptApi
except (ImportError, AttributeError):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "youtube-transcript-api"])
    if 'youtube_transcript_api' in sys.modules:
        del sys.modules['youtube_transcript_api']
    import youtube_transcript_api
    from youtube_transcript_api import YouTubeTranscriptApi

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir) 

try:
    from config_testes import CONFIG_TESTES
except ImportError:
    CONFIG_TESTES = {}

RAIZ_PROJETO = Path(script_dir).parents[1]

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': RAIZ_PROJETO / '_posts',
    'MODO_IMAGEM': 'unsplash', 
    'URL_IMAGEM_PADRAO': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&auto=format&fit=crop&q=80',
    
    'EMAIL_NOTIFICACAO': 'mayconmatosdigital@gmail.com',
    'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
    'SMTP_USER': os.getenv('SMTP_USER', ''), 
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''), 
    
    'KEYWORDS': [
        'experts de seo', 'melhores profissionais de seo', 'analise de seo', 
        'consultor de seo', 'curso de seo avaliacao', 'otimizacao para IA'
    ],
    'UNSPLASH_POOL': [
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=60'
    ],
    'MAYCON_LINKS': [
        'https://mayconmatos.com.br/',
        'https://mayconmatos.com.br/recursos/diagnostico-presenca-digital/',
        'https://mayconmatos.com.br/pagespeed-insights-vs-maycon-matos-seo/',
        'https://mayconmatos.com.br/servicos/seo-local/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/'
    ]
}

# Adicionado um parâmetro fictício no fim da URL para forçar bypass de cache de leitura se necessário
YOUTUBE_DATABASE = {
    "neilpatel": [
        "https://www.youtube.com/watch?v=H7m6myWuwII",
        "https://www.youtube.com/watch?v=k8aFgaUTe_I",
        "https://www.youtube.com/watch?v=WQHJcSiTc7s"
    ],
    "@RankMath": [
        "https://www.youtube.com/watch?v=VBRgIcXIxB0",
        "https://www.youtube.com/watch?v=T1iqDNgkxeI",
        "https://www.youtube.com/watch?v=sWpPqXXmi8o"
    ],
    "@AhrefsCom": [
        "https://www.youtube.com/watch?v=Sk8MAbD39Qw",
        "https://www.youtube.com/watch?v=uza9GX0E2mw"
    ]
}

def raspar_links_da_home():
    links_fallback = ["/blog/como-melhorar-nota-pagespeed/"]
    try:
        resposta = requests.get(CONFIG['COMPANY_WEBSITE'], timeout=15)
        if resposta.status_code != 200:
            return links_fallback
        links_encontrados = re.findall(r'href=["\']((?:https://masters-seo\.github\.io)?/blog/[a-zA-Z0-9\-_]+/?)["\']', resposta.text)
        links_limpos = list(set([l.replace("https://masters-seo.github.io", "") for l in links_encontrados]))
        return links_limpos if links_limpos else links_fallback
    except:
        return links_fallback

def extrair_video_id(url):
    match = re.search(r"(?:v=|\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def video_ja_processado(video_id):
    """Lógica corrigida: evita falsos positivos limpando a varredura"""
    folder = Path(CONFIG['OUTPUT_FOLDER'])
    if not folder.exists():
        return False
    
    # Se o painel de testes mandar forçar a gravação, ignora a checagem
    if CONFIG_TESTES.get('FORCAR_GRAVACAO_TESTE', False):
        return False

    for post in folder.glob("*.md"):
        try:
            content = post.read_text(encoding='utf-8')
            # Verifica estritamente a tag de marcação do front-matter
            if f"youtube_id: {video_id}" in content:
                print(f"📌 Vídeo {video_id} ignorado (Já existe no post: {post.name})")
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
    """Abordagem limpa e direta utilizando o fallback dinâmico do módulo"""
    try:
        # Tenta utilizar o método direto da classe importada
        try:
            lista = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
            return " ".join([item['text'] for item in lista])
        except AttributeError:
            # Caso o import tenha vindo encapsulado de outra forma pelo wrapper
            lista = youtube_transcript_api.get_transcript(video_id, languages=['pt', 'en'])
            return " ".join([item['text'] for item in lista])
    except Exception as e:
        print(f"❌ Falha crítica na API de Transcrição para o ID {video_id}: {e}")
        return None

def build_youtube_prompt(titulo_video, canal_autor, transcricao, keyword, contextual_link, secondary_img_url, alt_text_secondary, link_interno_1, link_interno_2):
    return f"""Você é um Copywriter Sênior de Resposta Direta e Analista Principal do {CONFIG['COMPANY_NAME']}.
Crie um artigo de autoridade profunda, altamente persuasivo, claro e totalmente otimizado para SEO semântico adaptando e expandindo o conteúdo de uma transcrição de vídeo.

TÍTULO DO VÍDEO BASE: {titulo_video}
AUTOR ORIGINAL DO VÍDEO: {canal_autor}
PALAVRA-CHAVE PRINCIPAL: {keyword}
LINK CONTEXTUAL: {contextual_link}
URL DA IMAGEM DO MEIO DO ARTIGO: {secondary_img_url}
ALT TEXT DA IMAGEM DO MEIO: {alt_text_secondary}

TRANSCRIÇÃO DO VÍDEO PARA CONTEXTO:
\"\"\"{transcricao}\"\"\"

Escreva um artigo completo estruturado em Markdown, focado em {keyword}, contextualizando o mercado do Brasil.
Use parágrafos curtos (2-3 linhas), subtítulos H2/H3 marcantes, inclua uma seção de resumo rápido, incorpore a imagem do meio usando a sintaxe de imagem do markdown, insira naturalmente os links internos reais: `{link_interno_1}` e `{link_interno_2}`. Termine com um FAQ e o Schema JSON-LD oculto em comentário HTML. Do não adicione delimitadores Front Matter no texto de resposta."""

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def solicitar_indexacao_google(target_url):
    if CONFIG_TESTES.get('DESATIVAR_INDEXING_API', False) or not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
        return False
    try:
        info = json.loads(CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON'])
        scopes = ['https://www.googleapis.com/auth/indexing']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        credentials.refresh(Request())
        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {credentials.token}"}
        body = {"url": target_url, "type": "URL_UPDATED"}
        requests.post(endpoint, json=body, headers=headers)
        return True
    except:
        return False

def executar_geracao_youtube():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ GEMINI_API_KEY ausente.")
        return False

    canais_disponiveis = sorted(list(YOUTUBE_DATABASE.keys()))
    dia_do_ano = datetime.now().timetuple().tm_yday
    
    canal_escolhido = None
    video_escolhido_url = None
    video_id_escolhido = None

    print(f"🔍 Analisando banco de dados de vídeos procurando itens não publicados...")
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
                print(f"🎯 Vídeo Selecionado com Sucesso para Processamento: {v_id} (Canal: {canal_candidato})")
                break
        if video_escolhido_url:
            break

    if not video_escolhido_url:
        print("🚨 Alerta: Nenhum vídeo novo pendente encontrado na fila do banco de dados!")
        return False

    print(f"🎬 Iniciando mineração do link: {video_escolhido_url}")
    titulo_video, canal_autor = obter_metadados_youtube(video_escolhido_url)
    
    if not titulo_video:
        titulo_video = f"Insights de SEO Avançado - Canal {canal_escolhido}"
        canal_autor = canal_escolhido

    transcricao = obter_transcricao(video_id_escolhido)
    if not transcricao:
        print("❌ Transcrição falhou. Forçando acionamento do pipeline de segurança.")
        return False

    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    alt_text_clean = f"Mídias e estratégias de marketing digital focadas em {keyword}."
    alt_text_secondary = f"Análise gráfica de métricas de {keyword} coletadas."

    links_reais = raspar_links_da_home()
    link_int1 = random.choice(links_reais)
    link_int2 = random.choice([l for l in links_reais if l != link_int1] or links_reais)

    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    prompt = build_youtube_prompt(titulo_video, canal_autor, transcricao, keyword, contextual_link, secondary_img_url, alt_text_secondary, link_int1, link_int2)

    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    content = response.text.strip()

    if not content or len(content) < 300:
        return False

    youtube_embed_code = f"""
<div class="youtube-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 35px 0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <iframe src="https://www.youtube.com/embed/{video_id_escolhido}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>
</div>
<p style="font-size: 0.85rem; color: #666; text-align: center; margin-top: -20px; font-style: italic;">Vídeo Original: "{titulo_video}" por {canal_autor}. Disponibilizado via incorporação pública do YouTube para referenciamento educacional do portal.</p>

"""
    content = youtube_embed_code + content
    today_str = datetime.now().strftime('%Y-%m-%d')
    slug = slugify(titulo_video)
    
    image_meta = f"\nimage: {secondary_img_url}\nimg_alt: '{alt_text_clean}'"
    horario_post = "00:01:00" if CONFIG_TESTES.get('FORCAR_PUBLICACAO_IMEDIATA', False) else "12:00:00"

    front_matter = f"""---
layout: post
title: '{titulo_video} - Análise e Insights'
date: {today_str} {horario_post} -0300
categories: 'Análises'
tags: [seo, marketing-digital]{image_meta}
youtube_id: {video_id_escolhido}
---

"""
    final_markdown = front_matter + content
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
        
    print(f"✅ Artigo derivado com sucesso e salvo em: {file_path}")
    solicitar_indexacao_google(f"{CONFIG['COMPANY_WEBSITE']}blog/{slug}/")
    return True

if __name__ == '__main__':
    sucesso = executar_geracao_youtube()
    if not sucesso:
        sys.exit(1)
