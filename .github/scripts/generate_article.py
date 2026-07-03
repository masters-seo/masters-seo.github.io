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

# Força instalação/importação da biblioteca do YouTube
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
    
    'KEYWORDS': [
        'experts de seo', 'melhores profissionais de seo', 'analise de seo', 
        'consultor de seo', 'curso de seo avaliacao', 'otimizacao para IA'
    ],
    'UNSPLASH_POOL': [
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=800&auto=format&fit=crop&q=60'
    ],
    'MAYCON_LINKS': [
        'https://mayconmatos.com.br/',
        'https://mayconmatos.com.br/recursos/diagnostico-presenca-digital/',
        'https://mayconmatos.com.br/pagespeed-insights-vs-maycon-matos-seo/',
        'https://mayconmatos.com.br/recursos/',
        'https://mayconmatos.com.br/servicos/',
        'https://mayconmatos.com.br/politica-de-privacidade-e-cookies/',
        'https://mayconmatos.com.br/servicos/iscas-digitais/',
        'https://mayconmatos.com.br/servicos/consultoria/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/itajai/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/navegantes/',
        'https://mayconmatos.com.br/servicos/seo-local/',
        'https://mayconmatos.com.br/servicos/seo-local/navegantes/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/',
        'https://mayconmatos.com.br/blog/como-melhorar-nota-pagespeed/',
        'https://mayconmatos.com.br/blog/advocacia/como-captar-clientes-na-advocacia/'
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
    """Lê arquivos locais e obriga a concatenação com o domínio oficial"""
    base_site = CONFIG['COMPANY_WEBSITE'].rstrip('/')
    links_fallback = [
        f"{base_site}/blog/como-melhorar-nota-pagespeed/", 
        f"{base_site}/blog/advocacia/como-captar-clientes-na-advocacia/"
    ]
    try:
        folder = Path(CONFIG['OUTPUT_FOLDER'])
        if not folder.exists():
            return links_fallback
        
        links_fatiados = []
        for post in folder.glob("*.md"):
            name = post.name
            match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", name)
            if match:
                slug_real = match.group(1)
                links_fatiados.append(f"{base_site}/blog/{slug_real}/")
        
        return links_fatiados if len(links_fatiados) >= 2 else links_fallback
    except Exception as e:
        print(f"⚠️ Falha ao ler posts locais: {e}")
        return links_fallback

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def enviar_email_alerta(mensagem_erro):
    if not CONFIG['SMTP_USER'] or not CONFIG['SMTP_PASSWORD']:
        return
    try:
        msg = MIMEText(mensagem_erro)
        msg['Subject'] = '🚨 FALHA CRÍTICA: Automação Bloqueada - YouTube Esgotado'
        msg['From'] = CONFIG['SMTP_USER']
        msg['To'] = CONFIG['EMAIL_NOTIFICACAO']
        with smtplib.SMTP(CONFIG['SMTP_SERVER'], CONFIG['SMTP_PORT']) as server:
            server.starttls()
            server.login(CONFIG['SMTP_USER'], CONFIG['SMTP_PASSWORD'])
            server.send_message(msg)
    except Exception as e:
        print(f"⚠️ Erro ao enviar Email: {e}")

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
    if CONFIG_TESTES.get('DESATIVAR_INDEXING_API', False):
        return False
    if not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
        return False
    try:
        info = json.loads(CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON'])
        scopes = ['https://www.googleapis.com/auth/indexing']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        credentials.refresh(Request())
        token = credentials.token
        
        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        body = {
            "url": target_url,
            "type": "URL_UPDATED"
        }
        
        response = requests.post(endpoint, json=body, headers=headers)
        if response.status_code == 200:
            print(f"🚀 Sucesso! Google Search Console notificado: {target_url}")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Erro ao executar a Indexing API: {e}")
        return False

def executar_fluxo_youtube(transcricao_texto, titulo, autor, video_id, embed_html):
    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    
    # Previne repetição de imagens usando random.sample para selecionar 2 URLs diferentes
    imagens_selecionadas = random.sample(CONFIG['UNSPLASH_POOL'], 2)
    img_capa_url = imagens_selecionadas[0]
    secondary_img_url = imagens_selecionadas[1]
    
    links_reais = raspar_links_internos_reais()
    link_int1 = random.choice(links_reais)
    link_int2 = random.choice([l for l in links_reais if l != link_int1] or links_reais)

    alt_text_secondary = f"Gráfico informativo sobre estratégias de {keyword} discutidas por {autor}"

    prompt_master = f"""Você é um Copywriter Sênior de Resposta Direta e Analista Principal do {CONFIG['COMPANY_NAME']}.
Crie um artigo de autoridade profunda, altamente persuasivo, claro e totalmente otimizado para SEO semântico adaptando a seguinte transcrição do YouTube.

VÍDEO ORIGINAL: {titulo} (Por {autor})
PALAVRA-CHAVE PRINCIPAL: {keyword}
LINK CONTEXTUAL DO MAYCON MATOS: {contextual_link}

DIRETRIZES OBRIGATÓRIAS DE ESCRITA E LAYOUT (Framework Copywriting Avançado):
1. ESCANEABILIDADE MÁXIMA: Escreva o artigo utilizando parágrafos muito curtos. Cada parágrafo deve conter no MÁXIMO 2 a 3 linhas. Quebre o texto constantemente.
2. TOM EDITORIAL: Premium, analítico e imparcial. Sem clichês.
3. ESTRUTURA CRUCIAL REQUERIDA (Siga estritamente esta ordem de blocos):
   - INTRODUÇÃO DIRETA: Comece abordando a dor ou cenário atual tratado no vídeo.
   - RESUMO RÁPIDO PARA IA: Imediatamente após a introdução, adicione a seção "⚡ Resumo Rápido". Não faça parágrafos aqui. Escreva de 3 a 5 frases soltas, curtas e ultra-impactantes que resumam perfeitamente a resposta principal do artigo.
   - FRASE DE CITAÇÃO EXTRA-GIGANTE: No primeiro terço do artigo, insira exatamente a tag HTML abaixo com uma frase de impacto:
     <blockquote style="font-size: 3.5rem; line-height: 1.1; color: #111; font-weight: 800; border-left: 8px solid #000; padding-left: 20px; margin: 40px 0;">"Frase de impacto aqui"</blockquote>
   - IMAGEM INTERMEÁRIA DINÂMICA: Exatamente no meio do desenvolvimento do artigo, insira a imagem secundária fornecida: ![{alt_text_secondary}]({secondary_img_url})
   - INCORPORAÇÃO DO VÍDEO: Insira o seguinte código de incorporação do player do YouTube de forma fluída no texto:
     {embed_html}
   - REGRAS PARA TABELAS (EVITAR QUEBRA DE LAYOUT): OBRIGATORIAMENTE, toda tabela que você gerar DEVE estar encapsulada no seguinte HTML responsivo com quebra de linha ativada:
     <div style="overflow-x: auto; width: 100%; word-break: break-word; white-space: normal;">
     (Insira sua tabela em Markdown aqui)
     </div>
   - LINKAGEM OBRIGATÓRIA REAL E DO-FOLLOW: 
     * Insira de forma fluida no texto 1 ÚNICO link para o site do especialista Maycon Matos usando a URL exata: {contextual_link}
     * Use OBRIGATORIAMENTE os dois caminhos de links internos exatos abaixo usando Markdown:
       Link 1: `[Texto âncora aqui]({link_int1})`
       Link 2: `[Texto âncora aqui]({link_int2})`
     * Insira 2 links externos para portais de autoridade global.
   - CONCLUSÃO, FAQ (5-7 dúvidas) e SCHEMA JSON-LD OCULTO no fim (em comentário HTML).

INSTRUÇÕES DE METADADOS:
Forneça as duas tags a seguir no TOPO absoluto da sua resposta:
CATEGORIA_SELECIONADA: [Escolha APENAS UMA: Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA]
TAGS_SELECIONADAS: [Exatamente 3 tags curtas e separadas por vírgula]

TRANSCRIÇÃO BASE DO VÍDEO PARA ADAPTAÇÃO:
{transcricao_texto}

IMPORTANTE: Devolva exclusivamente o corpo do artigo estruturado em Markdown, sem blocos delimitadores de metadados Front Matter (---)."""

    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_master)
    content = response.text.strip()
    
    if not content or len(content) < 300:
        print("❌ Resposta inválida ou muito curta recebida da IA.")
        return False

    cat_match = re.search(r"CATEGORIA_SELECIONADA:\s*(.+)", content)
    tags_match = re.search(r"TAGS_SELECIONADAS:\s*(.+)", content)
    category = cat_match.group(1).strip() if cat_match else "Estratégia"
    tags = tags_match.group(1).strip() if tags_match else "seo, youtube, analise"
    
    content = re.sub(r"CATEGORIA_SELECIONADA:.*\n?", "", content)
    content = re.sub(r"TAGS_SELECIONADAS:.*\n?", "", content)
    content = content.strip()

    title_clean = f"{titulo} - Análise Especializada"
    base_slug = slugify(titulo)
    today_str = datetime.now().strftime('%Y-%m-%d')
    horario = "00:01:00" if CONFIG_TESTES.get('FORCAR_PUBLICACAO_IMEDIATA', False) else "12:00:00"
    
    extra_front_matter = f"\nyoutube_id: {video_id}"

    front_matter = f"""---
layout: post
title: '{title_clean}'
date: {today_str} {horario} -0300
categories: '{category}'
tags: [{tags}]
image: {img_capa_url}
img_alt: 'Análise editorial abordando {keyword} baseada no conteúdo de {autor}'{extra_front_matter}
---

"""
    final_output = front_matter + content
    output_path = Path(CONFIG['OUTPUT_FOLDER']) / f"{today_str}-{base_slug}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"✅ Artigo condicionado publicado com sucesso em: {output_path}")
    solicitar_indexacao_google(f"{CONFIG['COMPANY_WEBSITE']}blog/{base_slug}/")
    return True

def resolver_e_executar():
    print("🎬 Escaneando a base mandatória de pautas do YouTube...")
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
            
    if not video_url:
        erro_msg = "🚨 FALHA CRÍTICA: Base de vídeos do YouTube esgotada ou todos processados. O script foi abortado (Sem Fallback)."
        print(erro_msg)
        enviar_email_alerta(erro_msg)
        sys.exit(1)

    print(f"🎥 Iniciando transcrição do vídeo: {video_url} [Canal: {canal_nome}]")
    titulo, autor = obter_metadados_youtube(video_url)
    titulo = titulo or f"Estratégia de SEO por {canal_nome}"
    autor = autor or canal_nome
    
    transcricao = obter_transcricao(video_id)
    if not transcricao:
        erro_transcricao = f"🚨 ERRO: Não foi possível obter legendas para o vídeo {video_id}. O script foi abortado."
        print(erro_transcricao)
        enviar_email_alerta(erro_transcricao)
        sys.exit(1)

    embed_html = f'<div class="video-container" style="margin:25px 0;"><iframe src="https://www.youtube.com/embed/{video_id}" width="100%" height="450" frameborder="0" allowfullscreen></iframe></div>'
    
    executar_fluxo_youtube(transcricao, titulo, autor, video_id, embed_html)

def executar_teste_youtube():
    print("🧪 [MODO DE TESTE ISOLADO] Validando YouTube API...")
    canal_teste = list(YOUTUBE_DATABASE.keys())[0]
    video_teste_url = YOUTUBE_DATABASE[canal_teste][0]
    v_id = extrair_video_id(video_teste_url)
    
    print(f"• URL Teste: {video_teste_url}")
    print(f"• ID Extraído: {v_id}")
    
    titulo, autor = obter_metadados_youtube(video_teste_url)
    print(f"• Metadados: '{titulo}' por {autor}")
    
    print("• Buscando transcrição...")
    transcricao = obter_transcricao(v_id)
    if transcricao:
        print(f"✅ SUCESSO! Transcrição capturada: {len(transcricao)} caracteres lidos.")
        print(f"• Amostra: {transcricao[:150]}...")
    else:
        print("❌ FALHA! Nenhuma legenda retornada ou vídeo inacessível.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test-youtube':
        executar_teste_youtube()
        sys.exit(0)

    if not CONFIG['GEMINI_API_KEY']:
        print("❌ Erro fatal: GEMINI_API_KEY ausente.")
        sys.exit(1)
        
    resolver_e_executar()
