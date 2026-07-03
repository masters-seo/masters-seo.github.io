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
from youtube_transcript_api import YouTubeTranscriptApi

# Garante a importação correta do config_testes indepedente de onde o script foi chamado
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from config_testes import CONFIG_TESTES
except ImportError:
    CONFIG_TESTES = {}

# Define a raiz do projeto (uma pasta acima de .github/scripts) para salvar os posts no local certo
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
        "https://www.youtube.com/watch?v=WQHJcSiTc7s",
        "https://www.youtube.com/watch?v=8InmhKjncoo",
        "https://www.youtube.com/watch?v=Lt-9PB0tIUU",
        "https://www.youtube.com/watch?v=SxTuBggWU2w"
    ],
    "@RankMath": [
        "https://www.youtube.com/watch?v=VBRgIcXIxB0",
        "https://www.youtube.com/watch?v=T1iqDNgkxeI",
        "https://www.youtube.com/watch?v=sWpPqXXmi8o"
    ],
    "@AhrefsCom": [
        "https://www.youtube.com/watch?v=Sk8MAbD39Qw",
        "https://www.youtube.com/watch?v=uza9GX0E2mw",
        "https://www.youtube.com/watch?v=Y_QrXGeNfQU"
    ]
}

def enviar_email_alerta():
    if not CONFIG['SMTP_USER'] or not CONFIG['SMTP_PASSWORD']:
        print("⚠️ Configurações de SMTP ausentes. Notificação por e-mail ignorada.")
        return
    try:
        msg = MIMEText("Olá Maycon,\n\nA sua lista de vídeos do YouTube cadastrados esgotou em todos os canais.\n\nO orquestrador do sistema ativou com sucesso o Modo Fallback e continuará gerando os conteúdos diários baseando-se no Modelo 1 por tópicos estáticos para manter o portal ativo.")
        msg['Subject'] = '🚨 Alerta: Banco de Vídeos do YouTube Esgotado!'
        msg['From'] = CONFIG['SMTP_USER']
        msg['To'] = CONFIG['EMAIL_NOTIFICACAO']
        
        with smtplib.SMTP(CONFIG['SMTP_SERVER'], CONFIG['SMTP_PORT']) as server:
            server.starttls()
            server.login(CONFIG['SMTP_USER'], CONFIG['SMTP_PASSWORD'])
            server.send_message(msg)
        print("✉️ E-mail de notificação enviado para mayconmatosdigital@gmail.com")
    except Exception as e:
        print(f"⚠️ Erro ao despachar e-mail: {e}")

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
        print(f"❌ Não foi possível carregar a transcrição do vídeo {video_id}: {e}")
        return None

def build_youtube_prompt(titulo_video, canal_autor, transcricao, keyword, contextual_link, secondary_img_url, alt_text_secondary):
    return f"""Você é um Copywriter Sênior de Resposta Direta e Analista Principal do {CONFIG['COMPANY_NAME']}.
Crie um artigo de autoridade profunda, altamente persuasivo, claro e totalmente otimizado para SEO semântico adaptando e expandindo o conteúdo de uma transcrição de vídeo.

TÍTULO DO VÍDEO BASE: {titulo_video}
AUTOR ORIGINAL DO VÍDEO: {canal_autor}
PALAVRA-CHAVE PRINCIPAL: {keyword}
LINK CONTEXTUAL DO MAYCON MATOS: {contextual_link}
URL DA IMAGEM DO MEIO DO ARTIGO: {secondary_img_url}
ALT TEXT DA IMAGEM DO MEIO: {alt_text_secondary}

TRANSCRIÇÃO DO VÍDEO PARA CONTEXTO ABSOLUTO:
\"\"\"{transcricao}\"\"\"

🚨 DIRETRIZES DE IDIOMA, ADAPTAÇÃO E LOCALIZAÇÃO CULTURAL (OBRIGATÓRIO):
- IDIOMA: Todo o conteúdo gerado deve ser escrito em PORTUGUÊS DO BRASIL.
- ADAPTAÇÃO CULTURAL: Adapte ferramentas e referências internacionais para o ecossistema brasileiro de SEO.

DIRETRIZES OBRIGATÓRIAS DE ESCRITA E LAYOUT (Framework Copywriting Avançado):
1. ESCANEABILIDADE MÁXIMA: Parágrafos de no MÁXIMO 2 a 3 linhas.
2. TOM EDITORIAL: Premium, analítico e imparcial.
3. ESTRUTURA CRUCIAL REQUERIDA:
   - INTRODUÇÃO DIRETA
   - RESUMO RÁPIDO PARA IA: Começando com "⚡ Resumo Rápido".
   - FRASE DE CITAÇÃO EXTRA-GIGANTE usando a tag blockquote fornecida.
   - IMAGEM INTERMEÁRIA DINÂMICA: ![{alt_text_secondary}]({secondary_img_url}) exatamente no meio do texto.
   - ENRIQUECIMENTO: H2, H3, tabelas ou listas.
   - LINKAGEM OBRIGATÓRIA DO-FOLLOW: 1 link real para {contextual_link}, 2 links internos relativos, 2 links externos de alta autoridade.
   - CONCLUSÃO E CTA
   - FAQ: 5 a 7 perguntas frequentes.
   - SCHEMA JSON-LD OCULTO em comentário HTML ao final.

CATEGORIA_SELECIONADA: Sua Categoria Aqui
TAGS_SELECIONADAS: tag1, tag2, tag3
Devolva exclusivamente o código estruturado em Markdown do artigo sem delimitadores Front Matter."""

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def gerar_imagem_com_texto(titulo, slug):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚠️ Biblioteca 'Pillow' não instalada. Usando fallback.")
        return CONFIG['URL_IMAGEM_PADRAO']
    try:
        img_data = requests.get(CONFIG['URL_IMAGEM_PADRAO']).content
        img_path = Path("temp_base.jpg")
        with open(img_path, 'wb') as f:
            f.write(img_data)
        
        img = Image.open(img_path).convert("RGBA")
        W, H = img.size
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        faixa_altura = int(H * 0.25)
        y0 = (H - faixa_altura) // 2
        y1 = y0 + faixa_altura
        
        draw.rectangle(((0, y0), (W, y1)), fill=(0, 0, 0, 128))
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(faixa_altura * 0.28))
        except IOError:
            font = ImageFont.load_default()
            
        palavras = titulo.split()
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            test_linha = f"{linha_atual} {palavra}".strip()
            if len(test_linha) * (faixa_altura * 0.18) < W - 60:
                linha_atual = test_linha
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        linhas.append(linha_atual)
        
        draw_txt = ImageDraw.Draw(overlay)
        total_texto_h = len(linhas) * int(faixa_altura * 0.35)
        current_y = y0 + (faixa_altura - total_texto_h) // 2
        
        for linha in linhas:
            draw_txt.text((W // 2, current_y), linha, fill=(255, 255, 255, 255), font=font, anchor="mm")
            current_y += int(faixa_altura * 0.35)
            
        img_final = Image.alpha_composite(img, overlay).convert("RGB")
        assets_folder = RAIZ_PROJETO / "assets/img/posts"
        assets_folder.mkdir(parents=True, exist_ok=True)
        
        final_img_path = assets_folder / f"{slug}.jpg"
        img_final.save(final_img_path, "JPEG")
        
        if img_path.exists():
            img_path.unlink()
            
        return f"/assets/img/posts/{slug}.jpg"
    except Exception as e:
        print(f"⚠️ Erro ao gerar imagem customizada: {e}")
        return CONFIG['URL_IMAGEM_PADRAO']

def solicitar_indexacao_google(target_url):
    if CONFIG_TESTES.get('DESATIVAR_INDEXING_API', False):
        print("🟡 Notificação de indexação pausada pelo painel de controle (CONFIG_TESTES).")
        return False
    if not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
        print("⚠️ Notificação de indexação ignorada: GOOGLE_SERVICE_ACCOUNT_JSON ausente.")
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
        if response.status_code == 200:
            print(f"🚀 Sucesso! Google Search Console notificado: {target_url}")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Erro na Indexing API: {e}")
        return False

def executar_geracao_youtube():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ GEMINI_API_KEY ausente.")
        return False

    canais_disponiveis = sorted(list(YOUTUBE_DATABASE.keys()))
    if not canais_disponiveis:
        return False

    dia_do_ano = datetime.now().timetuple().tm_yday
    canal_escolhido = None
    video_escolhido_url = None
    video_id_escolhido = None

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

    if not video_escolhido_url:
        print("🚨 Todas as pautas de vídeos cadastradas já foram mineradas!")
        enviar_email_alerta()
        return False

    print(f"🎬 Minerando Transcrição do Canal: {canal_escolhido} -> Link: {video_escolhido_url}")
    titulo_video, canal_autor = obter_metadados_youtube(video_escolhido_url)
    
    if not titulo_video:
        titulo_video = f"Análise Prática - Vídeo do {canal_escolhido}"
        canal_autor = canal_escolhido

    transcricao = obter_transcricao(video_id_escolhido)
    if not transcricao:
        print("❌ Transcrição indisponível. Acionando Fallback do Script Principal.")
        return False

    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    alt_text_clean = f"Análise de mídia focada em {keyword} a partir do conteúdo de {canal_autor}."
    alt_text_secondary = f"Gráfico analítico e informativos sobre métricas de {keyword} discutidas no material."

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

    youtube_embed_code = f"""
<div class="youtube-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 35px 0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <iframe src="https://www.youtube.com/embed/{video_id_escolhido}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>
</div>
<p style="font-size: 0.85rem; color: #666; text-align: center; margin-top: -20px; font-style: italic;">Vídeo Original: "{titulo_video}" por {canal_autor}. Disponibilizado via incorporação pública do YouTube para referenciamento educacional do portal.</p>

"""
    if "⚡ Resumo Rápido" in content:
        partes = content.split("⚡ Resumo Rápido")
        content = partes[0] + "⚡ Resumo Rápido" + youtube_embed_code + partes[1]
    else:
        content = youtube_embed_code + content

    today_str = datetime.now().strftime('%Y-%m-%d')
    slug = slugify(titulo_video)
    
    modo = CONFIG['MODO_IMAGEM'].lower()
    image_meta = ""
    if modo == 'unsplash':
        img_url = random.choice(CONFIG['UNSPLASH_POOL'])
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"
    elif modo == 'personalizada':
        img_url = gerar_imagem_com_texto(titulo_video, f"{today_str}-{slug}")
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"

    if CONFIG_TESTES.get('FORCAR_PUBLICACAO_IMEDIATA', False):
        horario_post = "00:01:00"
    else:
        horario_post = "12:00:00"

    front_matter = f"""---
layout: post
title: '{titulo_video} - Análise e Insights'
date: {today_str} {horario_post} -0300
categories: '{selected_category}'
tags: [{selected_tags}]{image_meta}
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
    public_post_url = f"{CONFIG['COMPANY_WEBSITE']}blog/{slug}/"
    solicitar_indexacao_google(public_post_url)
    return True

if __name__ == '__main__':
    import sys
    sucesso = executar_geracao_youtube()
    if not sucesso:
        sys.exit(1)
