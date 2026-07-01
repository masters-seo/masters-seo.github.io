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
    'OUTPUT_FOLDER': '_posts'  # Alterado de 'content/blog' para '_posts' (Padrão Jekyll)
}

def build_prompt(topic, keyword):
    return f"""Você é um analista sênior de SEO e redator principal do {CONFIG['COMPANY_NAME']}.
DADOS DO PORTAL:
- Nome: {CONFIG['COMPANY_NAME']}
- Website: {CONFIG['COMPANY_WEBSITE']}
- Localização: {CONFIG['COMPANY_LOCATION']}
- Missão: {CONFIG['COMPANY_DESC']}
- Público-alvo: {CONFIG['TARGET_AUDIENCE']}

TAREFA:
Crie um artigo de blog profundo, analítico e totalmente otimizado para SEO em formato Markdown para o Jekyll.

TÓPICO: {topic}
PALAVRA-CHAVE PRINCIPAL: {keyword}
TOM: {CONFIG['TONE']}
CTA: {CONFIG['CTA']}

ESTRUTURA COMPATÍVEL COM O BLOG:
1. Título SEO (≤60 caracteres) no formato: # Título
2. Meta description em comentário HTML
3. Slug em comentário HTML
4. Resumo Rápido em um bloco de citação (blockquote)
5. Introdução contextualizando o mercado de forma neutra e precisa
6. Seções H2 detalhadas com sub-tópicos H3
7. Conclusão sintetizando a análise + CTA para o portal
8. Seção de FAQ com 5-7 dúvidas comuns respondidas de forma direta
9. Estrutura Schema JSON-LD recomendada em um comentário HTML no fim do post

Formato: Apenas Markdown puro. Comece diretamente com # Título.
Crie o artigo agora:"""

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
    
    content = response.text
    
    if not content or len(content) < 500:
        print("❌ Conteúdo gerado inválido.")
        return False
        
    match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    title = match.group(1).strip() if match else f"analise-{datetime.now().strftime('%Y%m%d')}"
    
    slug = slugify(title)
    
    # Formata a data de hoje no padrão exigido pelo Jekyll: ANO-MES-DIA
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo agora inclui a data no início (Ex: 2026-07-01-nome-do-post.md)
    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"✅ Artigo salvo com sucesso em: {file_path}")
    return True

if __name__ == '__main__':
    main()
