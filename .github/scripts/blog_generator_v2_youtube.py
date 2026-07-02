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
# Tenta ler o painel de testes se ele existir na pasta
try:
    from config_testes import CONFIG_TESTES
except ImportError:
    CONFIG_TESTES = {}

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': '_posts',
    'MODO_IMAGEM': 'unsplash', 
    'URL_IMAGEM_PADRAO': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&auto=format&fit=crop&q=80',
    
    # Configurações do Sistema de Alerta por E-mail
    'EMAIL_NOTIFICACAO': 'mayconmatosdigital@gmail.com',
    'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
    'SMTP_USER': os.getenv('SMTP_USER', ''), 
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''), 
    
    # 100% DAS LISTAS ORIGINAIS MANIFESTADAS E INTEGRADAS
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

# =========================================================================
# 📝 PAUTA DO YOUTUBE: CADASTRE SEUS CANAIS E SUAS RESPECTIVAS URLS AQUI
# =========================================================================
YOUTUBE_DATABASE = {
    "@youtubecanal1": [
        "https://www.youtube.com/watch?v=ExemploID1",
        "https://www.youtube.com/watch?v=ExemploID2"
    ],
    "@youtubecanal2": [
        "https://www.youtube.com/watch?v=ExemploID3"
    ],
    "@youtubecanal3": [
        "https://www.youtube.com/watch?v=ExemploID4"
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
- IDIOMA: Todo o conteúdo gerado (incluindo o título do artigo, introdução, resumo, corpo do texto, FAQ, CATEGORIA_SELECIONADA, TAGS_SELECIONADAS e metadados ocultos do Schema JSON-LD) deve ser escrito em PORTUGUÊS DO BRASIL fluído, natural e gramaticalmente impecável.
- ADAPTAÇÃO CULTURAL E CONTEXTUALIZAÇÃO: Se a transcrição original mencionar ferramentas, leis, moedas, comportamento de mercado ou exemplos específicos dos Estados Unidos/Europa que não se aplicam ou não fazem sentido direto para o público brasileiro, você deve ADAPTAR E LOCALIZAR essas informações para o contexto e a realidade do mercado de SEO e marketing digital no BRASIL (ex: converter referências de dólares para reais se aplicável, adaptar termos puramente americanos para equivalentes práticos do ecossistema brasileiro).

DIRETRIZES OBRIGATÓRIAS DE ESCRITA E LAYOUT (Framework Copywriting Avançado):
1. ESCANEABILIDADE MÁXIMA: Escreva o artigo utilizando parágrafos muito curtos. Cada parágrafo deve conter no MÁXIMO 2 a 3 linhas. Quebre o texto constantemente.
2. TOM EDITORIAL: Premium, analítico e imparcial. Sem clichês.
3. ESTRUTURA CRUCIAL REQUERIDA (Siga estritamente esta ordem de blocos):
   - INTRODUÇÃO DIRETA: Comece abordando a dor ou cenário atual discutido no vídeo.
   - RESUMO RÁPIDO PARA IA: Imediatamente após a introdução, adicione a seção "⚡ Resumo Rápido". Não faça parágrafos aqui. Escreva de 3 a 5 frases soltas, curtas e ultra-impactantes que resumam perfeitamente a resposta principal do artigo.
   - FRASE DE CITAÇÃO EXTRA-GIGANTE: No primeiro terço do artigo, escolha uma frase curta de extremo impacto extraída ou baseada no vídeo e insira exatamente usando esta tag HTML:
     <blockquote style="font-size: 3.5rem; line-height: 1.1; color: #111; font-weight: 800; border-left: 8px solid #000; padding-left: 20px; margin: 40px 0;">"Frase de impacto aqui"</blockquote>
   - IMAGEM INTERMEÁRIA DINÂMICA: Exatamente no meio do desenvolvimento do artigo, insira a imagem secundária fornecida usando a sintaxe Markdown: ![{alt_text_secondary}]({secondary_img_url})
   - ENRIQUECIMENTO: Use intertítulos H2 e H3 baseados em benefícios, tabelas comparativas, listas com marcadores ou analogias sobre as percepções de {canal_autor}.
   - LINKAGEM OBRIGATÓRIA REAL E DO-FOLLOW: 
     * Todos os links gerados devem ser links reais e clicáveis usando a sintaxe Markdown [Texto Ancora Contextual](URL) ou HTML. É terminantemente proibido deixar o link em formato de texto cru.
     * Nenhum link pode conter "nofollow". Todos devem ser links padrão (DoFollow) para passar autoridade.
     * Insira de forma fluida no texto 1 ÚNICO link para o site do especialista Maycon Matos usando o endereço exato fornecido: {contextual_link}
     * Insira 2 links internos apontando de forma fictícia para outros artigos do portal {CONFIG['COMPANY_NAME']} usando caminhos relativos como "/blog/nome-do-post/".
     * Insira 2 links externos para portais de altíssima autoridade global em SEO (ex: Search Engine Land, Search Engine Journal, Backlinko, Neil Patel ou Google Search Central).
   - CONCLUSÃO E CTA: Conclusão amarrada seguidos de uma chamada para ação sutil direcionando o leitor a explorar as análises no portal {CONFIG['COMPANY_WEBSITE']}.
   - FAQ: Seção robusta contendo entre 5 e 7 dúvidas frequentes, com respostas diretas e curtas.
   - SCHEMA JSON-LD OCULTO: Ao final completo do arquivo, gere o código estruturado Schema JSON-LD (do tipo Article) inteiramente embutido dentro de um comentário HTML padrão para que ele fique invisível na tela para o usuário, mas acessível ao robô do Google, exatamente assim:

IMPORTANTE SOBRE METADADOS DE SEO DO ARTIGO:
Você deve OBRIGATORIAMENTE analisar o Tópico e o Conteúdo gerado para definir inteligentemente duas propriedades cruciais no início do texto (escreva as duas linhas de forma normal no topo da sua resposta para que o script capture):
1. CATEGORIA: Escolha estritamente APENAS UMA entre estas 6 opções que melhor se adapta contextualmente ao assunto: Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA. Escreva exatamente no formato: 'CATEGORIA_SELECIONADA: Sua Categoria Aqui'.
2. TAGS: Defina exatamente 3 tags curtas e estratégicas em minúsculas que complementem e façam sentido direto para o artigo. Escreva no formato: 'TAGS_SELECIONADAS: tag1, tag2, tag3'.

IMPORTANTE: Devolva exclusivamente o código estruturado em Markdown do artigo. Não inclua os blocos delimitadores de metadados Front Matter (---) no início da sua resposta."""
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
                linha_atual = palabra
        linhas.append(linha_atual)
        
        draw_txt = ImageDraw.Draw(overlay)
        total_texto_h = len(linhas) * int(faixa_altura * 0.35)
        current_y = y0 + (faixa_altura - total_texto_h) // 2
        
        for linha in linhas:
            draw_txt.text((W // 2, current_y), linha, fill=(255, 255, 255, 255), font=font, anchor="mm")
            current_y += int(faixa_altura * 0.35)
            
        img_final = Image.alpha_composite(img, overlay).convert("RGB")
        assets_folder = Path("assets/img/posts")
        assets_folder.mkdir(parents=True, exist_ok=True)
        
        final_img_path = assets_folder / f"{slug}.jpg"
        img_final.save(final_img_path, "JPEG")
        
        if img_path.exists():
            img_path.unlink()
            
        return f"/{final_img_path}"
    except Exception as e:
        print(f"⚠️ Erro ao gerar imagem customizada: {e}")
        return CONFIG['URL_IMAGEM_PADRAO']

def solicitar_indexacao_google(target_url):
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

    # Algoritmo de revezamento circular entre os canais com base no dia do ano
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

    # Se a pauta de vídeos terminou, aciona e-mail e retorna falso para o orquestrador ativar o Fallback
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

    # Bloco do reprodutor do YouTube integrado com citação técnica obrigatória
    youtube_embed_code = f"""
<div class="youtube-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 35px 0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <iframe src="https://www.youtube.com/embed/{video_id_escolhido}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>
</div>
<p style="font-size: 0.85rem; color: #666; text-align: center; margin-top: -20px; font-style: italic;">Vídeo Original: "{titulo_video}" por {canal_autor}. Disponibilizado via incorporação pública do YouTube para referenciamento educacional do portal.</p>

"""
    # Injeta dinamicamente o player de vídeo logo abaixo do resumo rápido de IA
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

    front_matter = f"""---
layout: post
title: '{titulo_video} - Análise e Insights'
date: {today_str} 12:00:00 -0300
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
    executar_geracao_youtube()
