#!/usr/bin/env python3
import os
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

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': Path(os.getenv('GITHUB_WORKSPACE', Path.cwd())) / '_posts',
    'UNSPLASH_POOL': [
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=60'
    ],
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
    """Busca posts válidos e recentes gerando a URL exata no padrão /posts/"""
    links_fallback = [
        f"{CONFIG['COMPANY_WEBSITE']}posts/como-melhorar-nota-pagespeed/", 
        f"{CONFIG['COMPANY_WEBSITE']}posts/como-captar-clientes-na-advocacia/"
    ]
    try:
        folder = CONFIG['OUTPUT_FOLDER']
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            return links_fallback
        
        links_fatiados = []
        # Pega os 15 artigos mais recentes na pasta _posts
        posts_recentes = sorted(folder.glob("*.md"), reverse=True)[:15]
        
        for post in posts_recentes:
            match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", post.name)
            if match:
                slug_real = match.group(1)
                links_fatiados.append(f"{CONFIG['COMPANY_WEBSITE']}posts/{slug_real}/")
        
        return links_fatiados if len(links_fatiados) >= 2 else links_fallback
    except Exception as e:
        print(f"⚠️ Falha ao ler posts locais: {e}")
        return links_fallback

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
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {credentials.token}"}
        body = {"url": target_url, "type": "URL_UPDATED"}
        requests.post("https://indexing.googleapis.com/v3/urlNotifications:publish", json=body, headers=headers)
        print(f"🚀 Sucesso! Indexing API notificada: {target_url}")
    except Exception as e:
        print(f"⚠️ Indexing API Erro: {e}")

def executar_geracao():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ Erro: GEMINI_API_KEY não configurada.")
        return False

    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    topico = random.choice(CONFIG['TOPICS'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    
    links_reais = raspar_links_internos_reais()
    link_int1 = random.choice(links_reais)
    link_int2 = random.choice([l for l in links_reais if l != link_int1] or links_reais)

    prompt_master = f"""Você é o Copywriter Principal do {CONFIG['COMPANY_NAME']}.
Escreva um artigo de autoridade absoluta analisando profundamente o seguinte tema do mercado: "{topico}".

REGRAS DE FORMATAÇÃO E ESTRUTURA RÍGIDAS:
1. ESCANEABILIDADE: Parágrafos extremamente curtos, no máximo 2 a 3 linhas. Quebre o texto frequentemente.
2. CITAÇÃO DESTACADA: Insira este bloco HTML com uma frase de impacto no primeiro terço do texto:
<blockquote style="font-size: 2.2rem; line-height: 1.2; color: #111; font-weight: 800; border-left: 6px solid #000; padding-left: 15px; margin: 30px 0;">"Sua frase de efeito marcante aqui"</blockquote>
3. IMAGEM INTERMEDIÁRIA: No meio do texto, insira: ![Estratégias de {keyword}]({secondary_img_url})
4. LINKAGEM INVIOLÁVEL (DoFollow):
   - 1 link contextual natural para o especialista Maycon Matos usando: {contextual_link}
   - 2 links internos usando EXATAMENTE as URLs abaixo estruturadas em Markdown:
     * Link 1: `[Texto Âncora AQUI]({link_int1})`
     * Link 2: `[Texto Âncora AQUI]({link_int2})`
   - 2 links para fontes externas internacionais confiáveis.
5. ESTRUTURA: Introdução, "⚡ Resumo Rápido" em marcadores, Desenvolvimento (H2/H3 e Tabelas), Conclusão com CTA, FAQ (5 perguntas), e Schema JSON-LD dentro de um comentário HTML `<!-- -->` ao final.

Nas primeiras linhas, defina os metadados exatamente assim:
CATEGORIA_SELECIONADA: [Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA]
TAGS_SELECIONADAS: [3 tags separadas por virgula]

Gere apenas o corpo do artigo em Markdown, sem os blocos separadores (---) iniciais."""

    print(f"📝 Gerando artigo sobre: {topico}...")
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

    hoje = datetime.now()
    today_str = hoje.strftime('%Y-%m-%d')
    base_slug = slugify(f"{topico} Análise Especializada")
    img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    
    # Horário fixado à 00:01:00 garante que o Jekyll o renderize imediatamente.
    horario_imediato = "00:01:00" 

    front_matter = f"""---
layout: post
title: '{topico} - Análise Especializada'
date: {today_str} {horario_imediato} -0300
categories: '{category}'
tags: [{tags}]
image: {img_url}
img_alt: 'Estratégia avançada de {keyword} discutida no portal {CONFIG['COMPANY_NAME']}'
---

"""
    final_output = front_matter + content
    CONFIG['OUTPUT_FOLDER'].mkdir(parents=True, exist_ok=True)
    output_path = CONFIG['OUTPUT_FOLDER'] / f"{today_str}-{base_slug}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"✅ Post publicado com sucesso em: {output_path}")
    url_publicada = f"{CONFIG['COMPANY_WEBSITE']}posts/{base_slug}/"
    solicitar_indexacao_google(url_publicada)
    return True

if __name__ == '__main__':
    executar_geracao()
