#!/usr/bin/env python3
import os
import json
import random
import re
import unicodedata
from datetime import datetime
from pathlib import Path

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Maycon M. Agência'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'mayconmatos.com.br'),
    'COMPANY_LOCATION': os.getenv('COMPANY_LOCATION', 'Navegantes, SC - Brasil'),
    'COMPANY_DESC': os.getenv('COMPANY_DESC', 'Consultoria de SEO e Marketing Digital'),
    'TARGET_AUDIENCE': os.getenv('TARGET_AUDIENCE', 'Pequenas empresas locais e prestadores de serviço'),
    'TONE': 'profissional',
    'FORMAT': 'pilar', 
    'CTA': 'Agende sua consultoria gratuita',
    
    'TOPICS': [
        'Como aparecer no Google Maps em Navegantes',
        'SEO Local: Guia Prático de Otimização',
        'Google My Business - Checklist Completo',
        'Local SEO vs SEO Global: Diferenças',
        'Como Gerar Leads com SEO Local',
        'Otimização para IA: O Futuro do SEO',
        'Schema.org e Dados Estruturados',
        'Link Building Local: Estratégias',
        'Content Marketing para Consultores',
        'Análise de Concorrentes em SEO Local'
    ],
    
    'KEYWORDS': [
        'consultor de seo',
        'consultoria de seo',
        'seo local',
        'google maps otimização',
        'site de conversão',
        'otimização para IA',
        'seo navegantes',
        'seo santa catarina',
        'google business profile',
        'local seo tips'
    ],
    'OUTPUT_FOLDER': 'content/blog'
}

def build_prompt(topic, keyword):
    return f"""Você é um especialista em SEO e criação de conteúdo de alta qualidade.
DADOS DA EMPRESA:
- Nome: {CONFIG['COMPANY_NAME']}
- Website: {CONFIG['COMPANY_WEBSITE']}
- Localização: {CONFIG['COMPANY_LOCATION']}
- Descrição: {CONFIG['COMPANY_DESC']}
- Público-alvo: {CONFIG['TARGET_AUDIENCE']}

TAREFA:
Crie um artigo de blog {CONFIG['FORMAT']} otimizado para SEO em formato Markdown.

TÓPICO: {topic}
PALAVRA-CHAVE PRINCIPAL: {keyword}
TOM: {CONFIG['TONE']}
CTA: {CONFIG['CTA']}

ESTRUTURA:
1. Título SEO (≤60 caracteres) como # Título
2. Meta description em comentário HTML
3. Slug em comentário HTML
4. Resumo Rápido em blockquote
5. Introdução + CTA âncora
6. Seções H2 com H3 quando apropriado
7. Conclusão + CTA
8. FAQ com 5-7 perguntas
9. Schema JSON-LD sugerido em comentário

Formato: Apenas Markdown. Comece com # Título.
Crie o artigo agora:"""

def slugify(text):
    # Remove acentos e caracteres especiais de forma segura para f-strings
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def main():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ GEMINI_API_KEY não configurada nos Secrets.")
        return False
        
    topic = random.choice(CONFIG['TOPICS'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    
    genai.configure(api_key=CONFIG['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    print(f"Generating for Topic: {topic} | Keyword: {keyword}")
    response = model.generate_content(build_prompt(topic, keyword))
    content = response.text
    
    if not content or len(content) < 500:
        print("❌ Conteúdo gerado inválido.")
        return False
        
    match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    title = match.group(1).strip() if match else f"artigo-{datetime.now().strftime('%Y%m%d')}"
    
    # Gera o slug de forma limpa usando a função auxiliar externa
    slug = slugify(title)
    
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_path = output_folder / f"{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"✅ Artigo salvo com sucesso em: {file_path}")
    return True

if __name__ == '__main__':
    main()
