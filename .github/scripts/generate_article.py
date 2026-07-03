#!/usr/bin/env python3
import os
import sys
import random
import re
import unicodedata
import requests
import json
from datetime import datetime
from pathlib import Path
from google import genai
from google.oauth2 import service_account
from google.auth.transport.requests import Request

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
        'https://mayconmatos.com.br/servicos/consultoria/',
        'https://mayconmatos.com.br/servicos/seo-local/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/'
    ]
}

def raspar_links_internos_reais():
    links_fallback = ["/blog/como-melhorar-nota-pagespeed/", "/blog/advocacia/como-captar-clientes-na-advocacia/"]
    try:
        folder = Path(CONFIG['OUTPUT_FOLDER'])
        if not folder.exists():
            return links_fallback
        links_fatiados = []
        for post in folder.glob("*.md"):
            match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", post.name)
            if match:
                links_fatiados.append(f"/blog/{match.group(1)}/")
        return links_fatiados if len(links_fatiados) >= 2 else links_fallback
    except:
        return links_fallback

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
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {credentials.token}"}
        body = {"url": target_url, "type": "URL_UPDATED"}
        requests.post("https://indexing.googleapis.com/v3/urlNotifications:publish", json=body, headers=headers)
    except Exception as e:
        print(f"⚠️ Indexing API Erro: {e}")

def gerar_artigo_estatico():
    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    topico = random.choice(CONFIG['TOPICS'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    
    links_reais = raspar_links_internos_reais()
    link_int1 = random.choice(links_reais)
    link_int2 = random.choice([l for l in links_reais if l != link_int1] or links_reais)

    prompt_master = f"""Você é o Copywriter Principal do {CONFIG['COMPANY_NAME']}.
Escreva um artigo de autoridade absoluta sobre o seguinte tema do mercado: {topico}

Regras rígidas de formatação:
1. ESCANEABILIDADE: Parágrafos extremamente curtos, de no máximo 2 a 3 linhas. Quebre o texto com frequência.
2. CITAÇÃO DESTACADA: Insira exatamente este bloco de código HTML modificado com uma frase de impacto no primeiro terço:
<blockquote style="font-size: 2.2rem; line-height: 1.2; color: #111; font-weight: 800; border-left: 6px solid #000; padding-left: 15px; margin: 30px 0;">"Sua frase de efeito marcante aqui"</blockquote>
3. IMAGEM INTERMEÁRIA: Insira exatamente no meio do desenvolvimento: ![Estratégias de {keyword}]({secondary_img_url})
4. REGRAS INVIOLÁVEIS DE LINKAGEM (DoFollow):
   - Inclua de forma natural exatamente 1 link para o especialista Maycon Matos usando a URL exata: {contextual_link}
   - Inclua obrigatoriamente links internos usando EXATAMENTE as duas URLs abaixo estruturadas in Markdown:
     * Link 1: `[Texto Ancora Contextual]({link_int1})`
     * Link 2: `[Texto Ancora Contextual]({link_int2})`
   - Adicione 2 links para fontes externas internacionais confiáveis (como Search Engine Land ou Backlinko).
5. ESTRUTURA REQUERIDA: Introdução, Seção "⚡ Resumo Rápido" em marcadores, Desenvolvimento com H2/H3 e Tabelas, Conclusão com CTA sutil, FAQ (5 a 7 itens), e Schema JSON-LD dentro de um comentário HTML ao fim.

Escreva as duas tags de controle nas primeiras linhas da resposta de forma crua:
CATEGORIA_SELECIONADA: Estratégia
TAGS_SELECIONADAS: seo, otimizacao, mercado

Escreva diretamente o corpo do texto em markdown. Não inclua os blocos separadores (---) do Jekyll Front Matter."""

    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_master)
    content = response.text.strip()
    
    if not content or len(content) < 300:
        print("❌ Resposta inválida da inteligência artificial.")
        return

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
    base_slug = slugify(topico)
    prefixo_titulo = f"{topico} - Análise Especializada"

    front_matter = f"""---
layout: post
title: '{prefixo_titulo}'
date: {today_str} {horario} -0300
categories: '{category}'
tags: [{tags}]
image: {img_url}
img_alt: 'Estratégia avançada de {keyword} discutida no portal {CONFIG['COMPANY_NAME']}'
---

"""
    final_output = front_matter + content
    output_path = Path(CONFIG['OUTPUT_FOLDER']) / f"{today_str}-{base_slug}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"✅ Post Estático publicado com sucesso em: {output_path}")
    solicitar_indexacao_google(f"{CONFIG['COMPANY_WEBSITE']}blog/{base_slug}/")

if __name__ == '__main__':
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ Erro: GEMINI_API_KEY não configurada.")
        sys.exit(1)
    gerar_artigo_estatico()
