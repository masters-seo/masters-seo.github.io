#!/usr/bin/env python3 
import os
import random
import re
import unicodedata
import requests
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta
from pathlib import Path
from google import genai
from google.oauth2 import service_account
from google.auth.transport.requests import Request

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

def build_prompt(topic, keyword, contextual_link, secondary_img_url, alt_text_secondary):
    return f"""Você é um Copywriter Sênior de Resposta Direta do portal {CONFIG['COMPANY_NAME']}.
Escreva um artigo dinâmico, direto ao ponto e focado na conversão sobre: {topic}.

PALAVRA-CHAVE PRINCIPAL: {keyword}
LINK OBRIGATÓRIO (Maycon Matos): [{keyword}]({contextual_link})
IMAGEM DO MEIO DO ARTIGO: ![{alt_text_secondary}]({secondary_img_url})

DIRETRIZES DE FORMATAÇÃO RIGOROSAS (NÃO ABRA MÃO DE NENHUM DESSES ELEMENTOS):
1. ESCANEABILIDADE: Parágrafos curtos com no MÁXIMO 2 ou 3 linhas. Quebre o texto frequentemente.
2. CITAÇÃO GIGANTE: Na introdução, insira EXATAMENTE esta tag HTML modificando o texto interno:
<blockquote style="font-size: 2.2rem; line-height: 1.2; color: #111; font-weight: 800; border-left: 6px solid #000; padding-left: 15px; margin: 30px 0;">"Frase impactante sobre {keyword}"</blockquote>

3. RESUMO RÁPIDO: Logo após a citação, adicione o intertítulo "## ⚡ Resumo Rápido: Insights dos Experts" seguido de 3 a 5 tópicos em marcadores de asterisco (*).
4. IMAGEM DO MEIO: Insira a sintaxe da imagem fornecida exatamente na metade do artigo.
5. TABELA COMPARATIVA: Monte uma tabela comparativa prática em Markdown relevante para o tema.
6. LINKAGEM: 
   - Use o link obrigatório do Maycon Matos uma vez.
   - Insira 2 links internos relativos como: [/blog/seo-tecnico/](/blog/seo-tecnico/).
   - Insira 2 links externos para sites globais (ex: [Search Engine Land](https://searchengineland.com)).
7. FAQ COMPLETO: Crie a seção "## FAQ: Perguntas Frequentes" usando H3 para 4 a 5 perguntas seguidas de respostas curtas.
8. METADADOS OBRIGATÓRIOS (Insira no início absoluto da resposta para o script ler):
CATEGORIA_SELECIONADA: [Insira uma: Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA]
TAGS_SELECIONADAS: tag1, tag2, tag3

Não envie blocos delimitadores de código (como ```markdown). Comece direto nos metadados."""

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

        total_texto_h = len(linhas) * int(faixa_altura * 0.35)
        current_y = y0 + (faixa_altura - total_texto_h) // 2

        for linha in linhas:
            draw.text((W // 2, current_y), linha, fill=(255, 255, 255, 255), font=font, anchor="mm")
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
    if CONFIG_TESTES.get('DESATIVAR_INDEXING_API', False):
        print("⚠️ Notificação de indexação ignorada: DESATIVAR_INDEXING_API está ativo.")
        return False

    if not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
        print("⚠️ Notificação de indexação ignorada: GOOGLE_SERVICE_ACCOUNT_JSON não configurada.")
        return False
    try:
        info = json.loads(CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON'])
        scopes = ['[https://www.googleapis.com/auth/indexing](https://www.googleapis.com/auth/indexing)']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        credentials.refresh(Request())
        token = credentials.token

        endpoint = "[https://indexing.googleapis.com/v3/urlNotifications:publish](https://indexing.googleapis.com/v3/urlNotifications:publish)"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        body = {"url": target_url, "type": "URL_UPDATED"}

        response = requests.post(endpoint, json=body, headers=headers)
        if response.status_code == 200:
            print(f"🚀 Sucesso! Google Search notificado instantaneamente: {target_url}")
            return True
        else:
            print(f"❌ Falha ao notificar o Google: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Erro ao executar a Indexing API: {e}")
        return False

def enviar_email_alerta_topicos():
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    if not smtp_user or not smtp_pass:
        return False
    try:
        msg = EmailMessage()
        msg.set_content("A lista estática de tópicos esgotou. O script mudou para o modo dinâmico.")
        msg['Subject'] = "⚠️ Alerta: Lista de Tópicos Esgotada - Masters SEO"
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"⚠️ Falha ao enviar e-mail: {e}")
        return False

def buscar_topicos_tendencia_google(client):
    try:
        prompt_fallback = (
            "Forneça uma lista com exatamente 5 tópicos em alta sobre SEO e IA no Brasil. "
            "Devolva APENAS os tópicos em linhas separadas."
        )
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_fallback)
        return [linha.strip() for linha in response.text.strip().split('\n') if len(linha.strip()) > 10]
    except Exception:
        return ["Tendências de SEO Semântico para o Próximo Ano"]

def main():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ GEMINI_API_KEY ausente.")
        return False

    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    
    file_index_path = Path("indice.txt")
    if file_index_path.exists():
        try:
            current_index = int(file_index_path.read_text(encoding='utf-8').strip())
        except ValueError:
            current_index = 0
    else:
        current_index = 0

    lista_topicos_padrao = CONFIG['TOPICS']

    if current_index >= len(lista_topicos_padrao):
        topicos_dinamicos = buscar_topicos_tendencia_google(client)
        topic = random.choice(topicos_dinamicos)
        if current_index == len(lista_topicos_padrao):
            enviar_email_alerta_topicos()
    else:
        topic = lista_topicos_padrao[current_index]

    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])

    title_clean = f"{topic}"
    slug = slugify(topic)

    # AJUSTE DE DATA - Remove o atraso de fuso horário para forçar aparição na Home
    fuso_brasil = timezone(timedelta(hours=-3))
    # Subtraímos 1 hora por segurança matemática para garantir que o post nunca entre como agendado/futuro no Jekyll
    data_ajustada = datetime.now(fuso_brasil) - timedelta(hours=1)
    today_str = data_ajustada.strftime('%Y-%m-%d')

    alt_text_clean = f"Análise sobre {keyword} - {CONFIG['COMPANY_NAME']}"
    alt_text_secondary = f"Gráfico informativo sobre {keyword}."

    prompt_final = build_prompt(topic, keyword, contextual_link, secondary_img_url, alt_text_secondary)

    # AJUSTE DE PARÂMETROS DA API - Define configurações rígidas para evitar estouro de tokens
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_final,
        config={
            "max_output_tokens": 2500,
            "temperature": 0.3
        }
    )

    content = response.text.strip()
    if not content or len(content) < 300:
        print("❌ Conteúdo inválido ou curto demais.")
        return False

    category_match = re.search(r"CATEGORIA_SELECIONADA:\s*(.+)", content)
    tags_match = re.search(r"TAGS_SELECIONADAS:\s*(.+)", content)

    selected_category = category_match.group(1).replace('[', '').replace(']', '').strip() if category_match else "Estratégia"
    selected_tags = tags_match.group(1).replace('[', '').replace(']', '').strip() if tags_match else "seo, ia"

    content = re.sub(r"CATEGORIA_SELECIONADA:.*\n?", "", content)
    content = re.sub(r"TAGS_SELECIONADAS:.*\n?", "", content)
    content = content.strip()

    modo = CONFIG['MODO_IMAGEM'].lower()
    image_meta = ""

    if modo == 'unsplash':
        img_url = random.choice(CONFIG['UNSPLASH_POOL'])
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"
    elif modo == 'personalizada':
        img_url = gerar_imagem_com_texto(title_clean, f"{today_str}-{slug}")
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"

    if CONFIG_TESTES.get('FORCAR_PUBLICACAO_IMEDIATA', False):
        horario_post = "00:01:00"
    else:
        horario_post = "00:05:00"

    jekyll_front_matter = f"""---
layout: post
title: '{title_clean}'
date: {today_str} {horario_post} -0300
categories: '{selected_category}'
tags: [{selected_tags}]{image_meta}
---

"""

    final_markdown = jekyll_front_matter + content

    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)

    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)

    print(f"✅ Artigo Jekyll salvo em: {file_path}")

    public_post_url = f"{CONFIG['COMPANY_WEBSITE']}blog/{slug}/"
    solicitar_indexacao_google(public_post_url)

    file_index_path.write_text(str(current_index + 1), encoding='utf-8')
    return True

if __name__ == '__main__':
    main()
