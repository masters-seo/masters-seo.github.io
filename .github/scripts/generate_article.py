#!/usr/bin/env python3
import os
import random
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from google import genai

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('https://masters-seo.github.io/', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': '_posts',
    'TOPICS': [
        'Quem são os maiores nomes de SEO Local no Brasil',
        'Análise dos principais cursos de SEO do mercado atual',
        'Como identificar um verdadeiro especialista em SEO',
        'O que os grandes experts dizem sobre a Otimização para IA',
        'Auditoria de SEO: Critérios usados pelos profissionais',
        'Estratégias de Link Building que os experts recomendam',
        'Análise independente: O impacto das atualizações do Google',
        'Como escolher uma consultoria de SEO confiável',
        'Métricas que realmente importam segundo os maiores nomes de SEO',
        'O panorama do mercado de SEO técnico no Brasil'
    ],
    'KEYWORDS': [
        'experts de seo', 'melhores profissionais de seo', 'analise de seo', 
        'consultor de seo', 'curso de seo avaliacao', 'otimizacao para IA'
    ],
    # Lista de imagens profissionais de tecnologia/dados/SEO para rotacionar de forma limpa
    'IMAGES_POOL': [
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60', # Gráficos/SEO
        'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&auto=format&fit=crop&q=60', # Análise de dados
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=60', # Código/IA
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=60', # Rede/Tecnologia
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=60', # Digital/Marketing
        'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=60'  # Dashboards
    ]
}

def build_prompt(topic, keyword):
    return f"""Você é o analista principal do Masters SEO.
Tarefa: Crie um artigo analítico em Markdown sobre: "{topic}" (focado na palavra-chave: {keyword}).
IMPORTANTE: Comece o texto direto na introdução. Não adicione cabeçalhos de metadados ou títulos com # no início."""

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def main():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ GEMINI_API_KEY ausente.")
        return False
        
    topic = random.choice(CONFIG['TOPICS'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    selected_image = random.choice(CONFIG['IMAGES_POOL'])
    
    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    print(f"Gerando artigo sobre: {topic}")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=build_prompt(topic, keyword),
    )
    
    content = response.text.strip()
    if not content or len(content) < 300:
        return False
        
    title_clean = f"{topic} - Análise Especializada"
    slug = slugify(topic)
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Adicionando o suporte a imagens que o Jekyll usa para renderizar na Home e no artigo
    jekyll_front_matter = f"""---
layout: post
title: "{title_clean}"
date: {today_str} 12:00:00 -0300
image: {selected_image}
---

"""
    final_markdown = jekyll_front_matter + content
    
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
        
    print(f"✅ Salvo com imagem em: {file_path}")
    return True

if __name__ == '__main__':
    main()
