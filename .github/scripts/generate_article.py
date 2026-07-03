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

# Força instalação/importação da biblioteca do YouTube se necessário
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])
    from youtube_transcript_api import YouTubeTranscriptApi

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

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
    
    'TOPICS': [
        'Quem são os maiores nomes de SEO Local no Brasil',
        'Análise dos principais cursos de SEO do mercado atual',
        'Como identificar um verdadeiro especialista em SEO',
        'O que os grandes experts dizem sobre a Otimização para IA',
        'Auditoria de SEO: Critérios usados pelos profissionais',
        'Estratégias de Link Building que os experts recomendam',
        'Análise independente: O impacto das updates do Google',
        'Como escolher uma consultoria de SEO confiável',
        'Métricas que realmente importam segundo os maiores nomes de SEO',
        'O panorama do mercado de SEO técnico no Brasil'
    ],
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
        'https://mayconmatos.com.br/servicos/consultoria/',
        'https://mayconmatos.com.br/servicos/seo-local/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/'
    ]
}

YOUTUBE_DATABASE = {
    "neilpatel": [
        "https://youtu.be/H7m6myWuwII",
        "https://www.youtube.com/watch?v=k8aFgaUTe_I",
        "https://www.youtube.com/watch?v=WQHJcSiTc7s"
    ],
    "@RankMath": [
        "https://www.youtube.com/watch?v=VBRgIcXIxB0",
        "https://www.youtube.com/watch?v=T1iqDNgkxeI"
    ],
    "@AhrefsCom": [
        "https://www.youtube.com/watch?v=Sk8MAbD39Qw",
        "https://www.youtube.com/watch?v=uza9GX0E2mw"
    ]
}

def raspar_links_internos_reais():
    """Busca posts válidos diretamente nos arquivos locais do repositório para evitar links quebrados"""
    links_fallback = ["/blog/como-melhorar-nota-pagespeed/", "/blog/advocacia/como-captar-clientes-na-advocacia/"]
    try:
        folder = Path(CONFIG['OUTPUT_FOLDER'])
        if not folder.exists():
            return links_fallback
        
        links_fatiados = []
        for post in folder.glob("*.md"):
            name = post.name
            # Padrão Jekyll: YYYY-MM-DD-slug.md -> extrai apenas o slug
            match = re.match(r"^\d{{4}}-\d{{2}}-\d{{2}}-(.+)\.md$", name)
            if match:
                slug_real = match.group(1)
                links_fatiados.append(f"/blog/{slug_real}/")
        
        return links_fatiados if len(links_fatiados) >= 2 else links_fallback
    except Exception as e:
        print(f"⚠️ Falha ao ler posts locais: {e}")
        return links_fallback

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def enviar_email_alerta():
    if not CONFIG['SMTP_USER'] or not CONFIG['SMTP_PASSWORD']:
        return
    try:
        msg = MIMEText("Banco de vídeos do YouTube esgotado. Transicionando automação para modo estático.")
        msg['Subject'] = '🚨 Alerta: YouTube Database Esgotada'
        msg['From'] = CONFIG['SMTP_USER']
        msg['To'] = CONFIG['EMAIL_NOTIFICACAO']
        with smtplib.SMTP(CONFIG['SMTP_SERVER'], CONFIG['SMTP_PORT']) as server:
            server.starttls()
            server.login(CONFIG['SMTP_USER'], CONFIG['SMTP_PASSWORD'])
            server.send_message(msg)
    except Exception as e:
        print(f"⚠️ Erro Email: {e}")

def extrair_video_id(url):
    match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def video_ja_processado(video_id):
    folder = Path(CONFIG['OUTPUT_FOLDER'])
    if not folder.exists():
        return False
    for post in folder.glob("*.md"):
        try:
            if f"youtube_id: {video_id}" in post.read_text(encoding='utf-8'):
                return True
        except:
            continue
    return False

def obter_metadados_youtube(url):
    try:
        res = requests.get(f"https://www.youtube.com/oembed?url={url}&format=json", timeout=10)
        if res.status_code == 200:
            d = res.json()
            return d.get('title'), d.get('author_name')
    except:
        pass
    return None, None

def obter_transcricao(video_id):
    try:
        lista = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        return " ".join([item['text'] for item in lista])
    except:
        return None

def solicitar_indexacao_google(target_url):
    if CONFIG_TESTES.get('DESATIVAR_INDEXING_API', False) or not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
        return False
    try:
        info = json.loads(CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON'])
        scopes = ['https://www.googleapis.com/auth/indexing']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        credentials.refresh(Request())
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {credentials.token}"}
        body = {"url": target_url, "type": "URL_UPDATED"}
        requests.post("https://indexing.googleapis.com/v3/urlNotifications:publish", json=body, headers=headers)
    except Exception as e:
        print(f"⚠️ Indexing API Erro: {e}")

def executar_fluxo_comum(prompt_adicional, prefixo_titulo, base_slug, extra_front_matter=""):
    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    
    links_reais = raspar_links_internos_reais()
    link_int1 = random.choice(links_reais)
    link_int2 = random.choice([l for l in links_reais if l != link_int1] or links_reais)

    prompt_master = f"""Você é o Copywriter Principal do {CONFIG['COMPANY_NAME']}.
Escreva um artigo de autoridade absoluta seguindo estas regras de formatação rígidas:

1. ESCANEABILIDADE: Parágrafos extremamente curtos, de no máximo 2 a 3 linhas. Quebre o texto com frequência.
2. CITAÇÃO DESTACADA: Insira exatamente este bloco de código HTML modificado com uma frase de impacto no primeiro terço:
<blockquote style="font-size: 2.2rem; line-height: 1.2; color: #111; font-weight: 800; border-left: 6px solid #000; padding-left: 15px; margin: 30px 0;">"Sua frase de efeito marcante aqui"</blockquote>
3. IMAGEM INTERMEÁRIA: Insira exatamente no meio do desenvolvimento: ![Estratégias de {keyword}]({secondary_img_url})
4. REGRAS INVIOLÁVEIS DE LINKAGEM (DoFollow):
   - Inclua de forma natural exatamente 1 link para o especialista Maycon Matos usando a URL exata: {contextual_link}
   - Inclua obrigatoriamente links internos usando EXATAMENTE as duas URLs abaixo estruturadas em Markdown. Não invente caminhos e não mude os slugs:
     * Link 1: `[Texto Ancora Contextual]({link_int1})`
     * Link 2: `[Texto Ancora Contextual]({link_int2})`
   - Adicione 2 links para fontes externas internacionais confiáveis (como Search Engine Land ou Backlinko).
5. ESTRUTURA REQUERIDA: Introdução, Seção "⚡ Resumo Rápido" em marcadores, Desenvolvimento com H2/H3 e Tabelas, Conclusão com CTA sutil, FAQ (5 a 7 itens), e Schema JSON-LD dentro de um comentário HTML `<!-- -->` ao fim.

Configurações do conteúdo base:
{prompt_adicional}

Escreva as duas tags de controle nas primeiras linhas da resposta de forma crua:
CATEGORIA_SELECIONADA: [Defina entre Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA]
TAGS_SELECIONADAS: [3 tags separadas por virgula]

Escreva diretamente o corpo do texto em markdown. Não inclua os blocos separadores (---) do Jekyll Front Matter."""

    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_master)
    content = response.text.strip()
    
    if not content or len(content) < 300:
        print("❌ Resposta inválida da inteligência artificial.")
        return False

    cat_match = re.search(r"CATEGORIA_SELECIONADA:\s*(.+)", content)
    tags_match = re.search(r"TAGS_SELECIONADAS:\s*(.+)", content)
    category = cat_match.group(1).strip() if cat_match else "Análises"
    tags = tags_match.group(1).strip() if tags_match else "seo, otimizacao"
    
    content = re.sub(r"CATEGORIA_SELECIONADA:.*\n?", "", content)
    content = re.sub(r"TAGS_SELECIONADAS:.*\n?", "", content)
    content = content.strip()

    today_str = datetime.now().strftime('%Y-%m-%d')
    img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    horario = "00:01:00" if CONFIG_TESTES.get('FORCAR_PUBLICACAO_IMEDIATA', False) else "12:00:00"

    front_matter = f"""---
layout: post
title: '{prefixo_titulo}'
date: {today_str} {horario} -0300
categories: '{category}'
tags: [{tags}]
image: {img_url}
img_alt: 'Estratégia avançada de {keyword} discutida no portal {CONFIG['COMPANY_NAME']}'{extra_front_matter}
---

"""
    final_output = front_matter + content
    output_path = Path(CONFIG['OUTPUT_FOLDER']) / f"{today_str}-{base_slug}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"✅ Post publicado com sucesso em: {output_path}")
    solicitar_indexacao_google(f"{CONFIG['COMPANY_WEBSITE']}blog/{base_slug}/")
    return True

def resolver_e_executar():
    # Verifica a intenção do Painel de Controle
    modo_youtube_ativo = CONFIG_TESTES.get('FORCOR_MODELO_YOUTUBE', False) or CONFIG_TESTES.get('FORCAR_MODELO_YOUTUBE', False)
    
    if modo_youtube_ativo:
        print("🎬 [Modo Ativo] Buscando pautas nos Canais do YouTube...")
        canais = sorted(list(YOUTUBE_DATABASE.keys()))
        dia_ano = datetime.now().timetuple().tm_yday
        
        video_url, video_id, canal_nome = None, None, None
        for i in range(len(canais)):
            c_cand = canais[(dia_ano + i) % len(canais)]
            for url in YOUTUBE_DATABASE[c_cand]:
                v_id = extrair_video_id(url)
                if v_id and not video_ja_processado(v_id):
                    video_url, video_id, canal_nome = url, v_id, c_cand
                    break
            if video_url:
                break
                
        if video_url:
            titulo, autor = obter_metadados_youtube(video_url)
            titulo = titulo or f"Estratégia de SEO por {canal_nome}"
            autor = autor or canal_nome
            transcricao = obter_transcricao(video_id)
            
            if transcricao:
                embed_html = f'\n<div class="video-container" style="margin:25px 0;"><iframe src="https://www.youtube.com/embed/{video_id}" width="100%" height="450" frameborder="0" allowfullscreen></iframe></div>\n'
                prompt_yt = f"Adapte em Português do Brasil a seguinte transcrição do vídeo de {autor} intitulado '{titulo}':\n\n{transcricao}"
                extra_meta = f"\nyoutube_id: {video_id}"
                
                return executar_fluxo_comum(prompt_yt, f"{titulo} - Insights", slugify(titulo), extra_front_matter=extra_meta)
            else:
                print("⚠️ Falha na captura da transcrição. Transitando para o modo estático automaticamente.")
        else:
            print("🚨 Banco de vídeos esgotado.")
            enviar_email_alerta()

    # Fallback ou Modo Estático Padrão
    print("📝 [Modo Ativo] Gerando artigo a partir de tópicos institucionais estáticos...")
    topico = random.choice(CONFIG['TOPICS'])
    return executar_fluxo_comum(f"Escreva uma análise profunda sobre o seguinte tema do mercado: {topico}", f"{topico} - Análise Especializada", slugify(topico))

if __name__ == '__main__':
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ Erro: GEMINI_API_KEY não configurada no ambiente do GitHub.")
        sys.exit(1)
    resolver_e_executar()
