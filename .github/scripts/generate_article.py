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
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'COMPANY_LOCATION': os.getenv('COMPANY_LOCATION', 'Brasil'),
    'COMPANY_DESC': os.getenv('COMPANY_DESC', 'Hub de análises independentes sobre os Experts do mercado de SEO'),
    'TARGET_AUDIENCE': os.getenv('TARGET_AUDIENCE', 'Profissionais de marketing, empresários e estudantes de SEO que buscam referências no mercado'),
    'TONE': 'analítico, informativo e imparcial',
    'FORMAT': 'pilar', 
    'CTA': 'Confira nossas análises completas no portal',
    
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
        'experts de seo',
        'melhores profissionais de seo',
        'analise de seo',
        'consultor de seo',
        'curso de seo avaliacao',
        'otimizacao para IA',
        'mercado de seo brasil',
        'especialista em seo',
        'seo independente',
        'auditoria de seo'
    ],
    'OUTPUT_FOLDER': '_posts'
}

def build_prompt(topic, keyword):
    return f"""Você é um analista sênior de SEO e redator principal do {CONFIG['COMPANY_NAME']}.
DADOS DO PORTAL:
- Nome: {CONFIG['COMPANY_NAME']}
- Website: {CONFIG['COMPANY_WEBSITE']}
- Missão: {CONFIG['COMPANY_DESC']}

TAREFA:
Crie um artigo de blog profundo, analítico e totalmente otimizado para SEO em formato Markdown para o Jekyll.

IMPORTANTE: Não crie cabeçalhos com --- ou metadados de layout. Comece o texto diretamente.

TÓPICO: {topic}
PALAVRA-CHAVE PRINCIPAL: {keyword}
TOM: {CONFIG['TONE']}
CTA: {CONFIG['CTA']}

ESTRUTURA:
1. Resumo Rápido em um bloco de citação (blockquote)
2. Introdução contextualizando o mercado
3. Seções H2 detalhadas com sub-tópicos H3
4. Conclusão sintetizando a análise + CTA para o portal
5. Seção de FAQ com 5-7 dúvidas comuns respondidas de forma direta
6. Estrutura Schema JSON-LD recomendada em um comentário HTML no fim do post

Formato: Apenas Markdown puro."""

def slugify(text):
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
    
    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    
    print(f"Generating for Topic: {topic} | Keyword: {keyword}")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=build_prompt(topic, keyword),
    )
    
    content = response.text.strip()
    if not content or len(content) < 500:
        print("❌ Conteúdo gerado inválido.")
        return False
        
    title_clean = f"{topic} - Análise Especializada"
    slug = slugify(topic)
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Monta o cabeçalho estrito do Jekyll sem quebras de linha iniciais
    jekyll_front_matter = f"---\nlayout: post\ntitle: \"{title_clean}\"\n---\n\n"
    
    final_markdown = jekyll_front_matter + content
    
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
        
    print(f"✅ Artigo Jekyll salvo com sucesso em: {file_path}")
    return True

if __name__ == '__main__':
    main()
