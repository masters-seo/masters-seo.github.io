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
    'MODO_IMAGEM': 'dinamico_gratuito', 

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
    ]
}

def raspar_links_internos_reais():
    """Garante links internos válidos do portal para evitar caminhos quebrados na home."""
    links_fallback = [
        "/blog/seo-local/",
        "/blog/seo-tecnico/",
        "/blog/estrategia/",
        "/blog/inteligencia-artificial/",
        "/blog/analise-de-mercado/"
    ]
    output_path = Path(CONFIG['OUTPUT_FOLDER'])
    if not output_path.exists():
        return links_fallback
    
    arquivos_md = list(output_path.glob("*.md"))
    if not arquivos_md:
        return links_fallback

    links_descobertos = []
    for arquivo in arquivos_md:
        nome_limpo = arquivo.stem
        # Extrai o slug removendo a data YYYY-MM-DD-
        slug_match = re.match(r"\d{{4}}-\d{{2}}-\d{{2}}-(.+)", nome_limpo)
        if slug_match:
            links_descobertos.append(f"/blog/{slug_match.group(1)}/")
    
    return list(set(links_descobertos)) if links_descobertos else links_fallback

def obter_imagem_contextual_gratuita(termo_busca):
    """Fallback dinâmico usando LoremFlickr para evitar imagens repetidas na home."""
    slug_termo = termo_busca.replace(" ", ",")
    # Retorna uma URL de imagem de tecnologia/negócios não repetida baseada em ID aleatório
    rand_id = random.randint(1, 1000)
    return f"https://loremflickr.com/1200/630/business,tech,data?lock={rand_id}"

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def solicitar_indexacao_google(target_url):
    if CONFIG_TESTES.get('DESATIVAR_INDEXING_API', False):
        print("⚠️ Notificação de indexação ignorada: DESATIVAR_INDEXING_API está ativo.")
        return False
    if not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
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
        return response.status_code == 200
    except Exception:
        return False

def enviar_email_alerta_topicos():
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    if not smtp_user or not smtp_pass:
        return False
    try:
        msg = EmailMessage()
        msg.set_content("A lista estática de tópicos acabou. Rodando em modo dinâmico.")
        msg['Subject'] = "⚠️ Alerta: Lista de Tópicos Esgotada - Masters SEO"
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception:
        return False

def buscar_topicos_tendencia_google(client):
    try:
        prompt_fallback = "Forneça 5 tópicos em alta sobre SEO no Brasil. Retorne apenas as frases em linhas limpas."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_fallback)
        return [l.strip() for l in response.text.strip().split('\n') if len(l.strip()) > 10]
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
        topico = random.choice(topicos_dinamicos)
        if current_index == len(lista_topicos_padrao):
            enviar_email_alerta_topicos()
    else:
        topico = lista_topicos_padrao[current_index]

    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    
    # Geração de imagens únicas por execução eliminando a repetição na Home
    img_capa_url = obter_imagem_contextual_gratuita(keyword)
    secondary_img_url = obter_imagem_contextual_gratuita(f"{keyword} analytics")

    links_reais = raspar_links_internos_reais()
    link_int1 = random.choice(links_reais)
    link_int2 = random.choice([l for l in links_reais if l != link_int1] or links_reais)

    alt_text_secondary = f"Infográfico analítico cobrindo métricas e performance de {keyword}."
    prefixo_titulo = f"{topico} - Análise Especializada"
    base_slug = slugify(topico)

    # AJUSTE DE DATA COPIADO DO SEU FRAMEWORK DE SUCESSO: Força fuso de Brasília sem atrasos
    fuso_brasil = timezone(timedelta(hours=-3))
    today_str = datetime.now(fuso_brasil).strftime('%Y-%m-%d')
    horario = "00:01:00" if CONFIG_TESTES.get('FORCAR_PUBLICACAO_IMEDIATA', False) else "12:00:00"

    prompt_master = f"""Você é o Copywriter Principal do {CONFIG['COMPANY_NAME']}.
Escreva um artigo de autoridade absoluta sobre o seguinte tema do mercado: {topico}

PALAVRA-CHAVE PRINCIPAL: {keyword}
LINK CONTEXTUAL DO MAYCON MATOS: {contextual_link}

DIRETRIZES OBRIGATÓRIAS DE ESCRITA E LAYOUT (Framework Copywriting Avançado):
1. ESCANEABILIDADE MÁXIMA: Escreva o artigo utilizando parágrafos muito curtos. Cada parágrafo deve conter no MÁXIMO 2 a 3 linhas. Quebre o texto constantemente.
2. TOM EDITORIAL: Premium, analítico e imparcial. Sem clichês corporativos vazios.
3. ESTRUTURA CRUCIAL REQUERIDA (Siga estritamente esta ordem de blocos):
   - INTRODUÇÃO DIRETA: Comece abordando a dor latente e o cenário prático do tema. Parágrafos curtos.
   - RESUMO RÁPIDO PARA IA: Imediatamente após os primeiros parágrafos introdutórios, adicione a seção "## ⚡ Resumo Rápido". Não faça blocos corridos aqui. Escreva de 3 a 5 frases soltas usando listas de marcadores (*), trazendo insights ultra-impactantes.
   - FRASE DE CITAÇÃO EXTRA-GIGANTE: No primeiro terço do artigo, insira exatamente a tag HTML abaixo com uma frase de altíssimo impacto mercadológico:
     <blockquote style="font-size: 2.2rem; line-height: 1.2; color: #111; font-weight: 800; border-left: 6px solid #000; padding-left: 15px; margin: 30px 0;">"Sua frase de efeito marcante aqui sobre o tema"</blockquote>
   - DESENVOLVIMENTO COM INTERTÍTULOS (H2 e H3): Divida o raciocínio de forma aprofundada explorando intenção de busca e métricas reais.
   - IMAGEM INTERMEÁRIA DINÂMICA: Exatamente no meio do desenvolvimento do artigo, insira a imagem secundária fornecida: ![{alt_text_secondary}]({secondary_img_url})
   - REGRAS PARA TABELAS (EVITAR QUEBRA DE LAYOUT): Gere uma tabela comparativa detalhada em Markdown e OBRIGATORIAMENTE encapsule-a no seguinte HTML responsivo com quebra de linha ativa:
     <div style="overflow-x: auto; width: 100%; word-break: break-word; white-space: normal;">
     (Insira sua tabela em Markdown aqui)
     </div>
   - LINKAGEM OBRIGATÓRIA REAL E DO-FOLLOW: 
     * Insira de forma totalmente orgânica no texto 1 ÚNICO link para o especialista Maycon Matos usando a correspondência exata: [{keyword}]({contextual_link})
     * Use OBRIGATORIAMENTE os dois caminhos de links internos exatos mapeados abaixo usando Markdown clássico:
       Link 1: [Texto Âncora Contextual]({link_int1})
       Link 2: [Texto Âncora Contextual]({link_int2})
     * Insira ao longo do artigo exatamente 2 links externos para portais de autoridade global de SEO (ex: Search Engine Land, Search Engine Journal ou Backlinko).
   - CONCLUSÃO E CTA: Amarrada de forma analítica e convidando o leitor a continuar consumindo os conteúdos ricos do portal.
   - FAQ COMPLETO: Adicione a seção "## FAQ: Perguntas Frequentes" contendo de 5 a 7 dúvidas reais e frequentes utilizando H3 para as perguntas e respostas curtas de até 3 linhas logo abaixo.
   - SCHEMA JSON-LD OCULTO: Ao fim completo de sua resposta, monte os dados estruturados em JSON-LD dentro de um comentário HTML padrão: INSTRUÇÕES DE METADADOS:
Escreva as duas tags de controle nas primeiras linhas absolutas da resposta de forma crua:
CATEGORIA_SELECIONADA: [Escolha uma: Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA]
TAGS_SELECIONADAS: tag1, tag2, tag3

IMPORTANTE: Devolva exclusivamente o corpo do artigo estruturado em Markdown. Não inclua os blocos separadores (---) do Jekyll Front Matter."""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_master
    )
    content = response.text.strip()

    if not content or len(content) < 300:
        print("❌ Resposta inválida ou muito curta recebida da IA.")
        return False

    cat_match = re.search(r"CATEGORIA_SELECIONADA:\s*(.+)", content)
    tags_match = re.search(r"TAGS_SELECIONADAS:\s*(.+)", content)
    
    category = cat_match.group(1).replace('[', '').replace(']', '').strip() if cat_match else "Análises"
    tags = tags_match.group(1).replace('[', '').replace(']', '').strip() if tags_match else "seo, otimizacao"

    content = re.sub(r"CATEGORIA_SELECIONADA:.*\n?", "", content)
    content = re.sub(r"TAGS_SELECIONADAS:.*\n?", "", content)
    content = content.strip()

    # Jekyll Front Matter idêntico ao framework estável original
    front_matter = f"""---
layout: post
title: '{prefixo_titulo}'
date: {today_str} {horario} -0300
categories: '{category}'
tags: [{tags}]
image: {img_capa_url}
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
    
    file_index_path.write_text(str(current_index + 1), encoding='utf-8')
    return True

if __name__ == '__main__':
    main()
