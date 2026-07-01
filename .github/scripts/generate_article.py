#!/usr/bin/env python3
"""
Blog Article Generator Script
Executa automaticamente no GitHub Actions ou localmente
"""

import os
import json
import random
import re
from datetime import datetime
from pathlib import Path

# Tentar importar as bibliotecas de IA
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from anthropic import Anthropic
    HAS_CLAUDE = True
except ImportError:
    HAS_CLAUDE = False

# ===== CONFIGURAÇÃO =====

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY', ''),
    
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Maycon M. Agência'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'mayconmatos.com.br'),
    'COMPANY_LOCATION': os.getenv('COMPANY_LOCATION', 'Navegantes, SC - Brasil'),
    'COMPANY_DESC': os.getenv('COMPANY_DESC', 'Consultoria de SEO e Marketing Digital'),
    'TARGET_AUDIENCE': os.getenv('TARGET_AUDIENCE', 'Pequenas empresas locais'),
    
    'TONE': 'profissional',
    'FORMAT': 'pilar',  # pilar, guia, rapido, faq
    'CTA': 'Agende sua consultoria gratuita',
    'DEFAULT_AI': 'gemini',  # ou 'claude'
    
    'TOPICS': [
        'Como aparecer no Google Maps',
        'SEO local para pequenas empresas',
        'Criar site que converte clientes',
        'Otimização para inteligência artificial',
        'Estratégias de SEO para negócios locais',
        'Google My Business - Guia Completo',
        'Link Building para Negócios Locais',
        'Schema.org e Dados Estruturados para SEO',
        'Content Marketing para PMEs',
        'Análise de Concorrentes em SEO'
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
    
    'OUTPUT_FOLDER': 'content/blog',
    'LOG_FILE': '.github/logs/articles.json'
}

def build_prompt(topic, keyword):
    """Construir prompt otimizado para IA"""
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

REGRAS CRÍTICAS:
- Sem keyword stuffing
- Parágrafos curtos (3-4 linhas máximo)
- Listas com ≤5 itens
- Exemplos práticos
- Links internos naturais
- Otimizado para featured snippets
- Foco em E-E-A-T

Formato: Apenas Markdown. Comece com # Título.
Tipo de formato: {CONFIG['FORMAT']} (2000-3000 palavras para pilar)

Crie o artigo agora:"""


def generate_with_gemini(prompt):
    """Chamar Google Gemini"""
    if not HAS_GEMINI:
        print("❌ google-generativeai não instalado")
        return None
    
    try:
        genai.configure(api_key=CONFIG['GEMINI_API_KEY'])
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Erro Gemini: {e}")
        return None


def generate_with_claude(prompt):
    """Chamar Anthropic Claude"""
    if not HAS_CLAUDE:
        print("❌ anthropic não instalado")
        return None
    
    try:
        client = Anthropic(api_key=CONFIG['CLAUDE_API_KEY'])
        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"❌ Erro Claude: {e}")
        return None


def generate_article(topic, keyword):
    """Gerar artigo usando IA"""
    prompt = build_prompt(topic, keyword)
    
    print(f"\n📝 Gerando artigo...")
    print(f"  Tópico: {topic}")
    print(f"  Palavra-chave: {keyword}")
    
    content = None
    
    if CONFIG['DEFAULT_AI'] == 'gemini' and CONFIG['GEMINI_API_KEY']:
        print("  IA: Gemini")
        content = generate_with_gemini(prompt)
    elif CONFIG['DEFAULT_AI'] == 'claude' and CONFIG['CLAUDE_API_KEY']:
        print("  IA: Claude")
        content = generate_with_claude(prompt)
    else:
        print("❌ Nenhuma IA configurada!")
        return None
    
    if not content or len(content) < 500:
        print("❌ Conteúdo muito curto ou vazio")
        return None
    
    print(f"✅ Artigo gerado ({len(content)} caracteres)")
    return content


def extract_title(content):
    """Extrair título do markdown"""
    match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    return match.group(1).strip() if match else f"Artigo {datetime.now().strftime('%Y%m%d')}"


def sanitize_slug(text):
    """Converter texto em slug"""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:60]


def save_article(content):
    """Salvar artigo em arquivo"""
    title = extract_title(content)
    slug = sanitize_slug(title)
    
    # Criar pasta se não existir
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Preparar arquivo com frontmatter
    frontmatter = f"""---
title: "{title.replace('"', '\\"')}"
date: {datetime.now().isoformat()}
slug: "{slug}"
---

"""
    
    file_path = output_folder / f"{slug}.md"
    
    # Evitar sobrescrita
    if file_path.exists():
        counter = 1
        while (output_folder / f"{slug}-{counter}.md").exists():
            counter += 1
        file_path = output_folder / f"{slug}-{counter}.md"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    
    print(f"💾 Salvo em: {file_path}")
    return str(file_path), title


def log_article(title, topic, keyword, filename):
    """Registrar no log"""
    log_folder = Path(CONFIG['LOG_FILE']).parent
    log_folder.mkdir(parents=True, exist_ok=True)
    
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'title': title,
        'topic': topic,
        'keyword': keyword,
        'filename': filename,
        'status': 'success'
    }
    
    # Ler log existente
    log_path = Path(CONFIG['LOG_FILE'])
    articles = []
    
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        except:
            articles = []
    
    articles.append(log_data)
    
    # Escrever log
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Registrado no log")


def main():
    """Executar geração"""
    print("=" * 60)
    print("🚀 BLOG ARTICLE GENERATOR")
    print("=" * 60)
    
    # Validar configuração
    if not CONFIG['GEMINI_API_KEY'] and not CONFIG['CLAUDE_API_KEY']:
        print("\n❌ Configure GEMINI_API_KEY ou CLAUDE_API_KEY")
        print("   No GitHub: Settings > Secrets > New repository secret")
        return False
    
    # Selecionar tópico e palavra-chave aleatórios
    topic = random.choice(CONFIG['TOPICS'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    
    print(f"\n📋 Configuração:")
    print(f"   Empresa: {CONFIG['COMPANY_NAME']}")
    print(f"   Tópico: {topic}")
    print(f"   Palavra-chave: {keyword}")
    print(f"   Pasta de saída: {CONFIG['OUTPUT_FOLDER']}")
    
    # Gerar artigo
    content = generate_article(topic, keyword)
    
    if not content:
        print("\n❌ Falha na geração")
        return False
    
    # Salvar arquivo
    try:
        filename, title = save_article(content)
        log_article(title, topic, keyword, filename)
        print(f"\n✅ SUCESSO!")
        print(f"   Título: {title}")
        print(f"   Arquivo: {filename}")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao salvar: {e}")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
