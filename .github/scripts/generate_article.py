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

# =====================================================================
# ⚙️ PAINEL DE CONTROLE (OPÇÕES DE AUTOMAÇÃO)
# =====================================================================
CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', ''),
    
    # 1. TAREFA: Ligar/Desligar envio automático para o Google Indexing.
    # Mude para False se não quiser que ele avise o Google imediatamente.
    'ENVIAR_PARA_GOOGLE': True, 
    
    # 2. TAREFA: Piloto Automático de Tendências.
    # Se True, quando o arquivo "temas.txt" estiver vazio, a IA vai pesquisar 
    # tendências dos EUA e criar um tema em alta automaticamente.
    # Se False, o script vai parar de postar quando acabar os temas do txt.
    'MODO_TENDENCIAS_EUA': True, 
    
    # Caminhos e Dados Fixos
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': Path(os.getenv('GITHUB_WORKSPACE', Path.cwd())) / '_posts',
    'ARQUIVO_TEMAS': Path(os.getenv('GITHUB_WORKSPACE', Path.cwd())) / '.github' / 'scripts' / 'temas.txt',
    
    'UNSPLASH_POOL': [
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=60'
    ],
    'KEYWORDS': ['experts de seo', 'melhores profissionais de seo', 'analise de seo', 'consultor de seo', 'curso de seo avaliacao', 'otimizacao para IA'],
    'MAYCON_LINKS': [
        'https://mayconmatos.com.br/',
        'https://mayconmatos.com.br/recursos/diagnostico-presenca-digital/',
        'https://mayconmatos.com.br/pagespeed-insights-vs-maycon-matos-seo/',
        'https://mayconmatos.com.br/servicos/consultoria/',
        'https://mayconmatos.com.br/servicos/seo-local/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/'
    ]
}

# =====================================================================
# FUNÇÕES DE APOIO
# =====================================================================

def obter_tema_inteligente(client):
    """
    GERENCIADOR DE TEMAS:
    Primeiro, tenta ler do arquivo temas.txt. Se encontrar, usa o primeiro da fila
    e o apaga. Se o arquivo estiver vazio e a opção MODO_TENDENCIAS_EUA estiver ativada,
    gera um novo tema do zero usando IA.
    """
    tema_escolhido = ""
    arquivo = CONFIG['ARQUIVO_TEMAS']
    
    # 1. Tentativa de ler a fila no arquivo temas.txt
    if arquivo.exists():
        with open(arquivo, 'r', encoding='utf-8') as f:
            # Pega todas as linhas que não estão em branco
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
        
        if linhas:
            # Pega o primeiro tema da lista (posição 0)
            tema_escolhido = linhas.pop(0) 
            
            # Sobrescreve o arquivo com os temas restantes (apagando o que foi usado)
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write("\n".join(linhas) + "\n")
            
            print(f"📖 Tema obtido do arquivo temas.txt: {tema_escolhido}")
            print(f"📉 Temas restantes na fila: {len(linhas)}")
            return tema_escolhido
            
    # 2. Se a fila acabou, entra no Piloto Automático (Trending Topics)
    print("⚠️ Fila do arquivo temas.txt está vazia ou não existe.")
    
    if CONFIG['MODO_TENDENCIAS_EUA']:
        print("🌐 Piloto Automático ativado! Pesquisando tendência atual nos EUA via IA...")
        prompt_trend = """Atue como um Analista de Tendências Globais de SEO e Marketing.
        Pesquise um assunto quente e altamente debatido HOJE no mercado dos EUA (ex: novas atualizações do Google, impacto da IA, novas métricas).
        Adapte essa tendência para o público brasileiro e crie UM título de artigo altamente clicável.
        REGRA ABSOLUTA: Retorne APENAS o título, sem aspas, sem pontuação no final e sem explicações."""
        
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_trend)
            tema_gerado = response.text.strip().replace('"', '').replace("'", "")
            print(f"🚀 Tendência Gerada: {tema_gerado}")
            return tema_gerado
        except Exception as e:
            print(f"❌ Erro ao gerar tendência via IA: {e}")
            
    # 3. Fallback (Plano de emergência caso tudo dê errado e o modo automático esteja desligado)
    print("❌ Sem temas disponíveis. Retornando falso para cancelar postagem.")
    return False

def raspar_links_internos_reais():
    """Busca posts válidos e recentes na pasta para fazer a linkagem interna automática."""
    links_fallback = [
        f"{CONFIG['COMPANY_WEBSITE']}posts/como-melhorar-nota-pagespeed/", 
        f"{CONFIG['COMPANY_WEBSITE']}posts/como-captar-clientes-na-advocacia/"
    ]
    try:
        folder = CONFIG['OUTPUT_FOLDER']
        if not folder.exists(): return links_fallback
        
        links_fatiados = []
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
    """Envia a URL para o Google Search Console via Indexing API"""
    if not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']: return False
    try:
        info = json.loads(CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON'])
        scopes = ['https://www.googleapis.com/auth/indexing']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        credentials.refresh(Request())
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {credentials.token}"}
        body = {"url": target_url, "type": "URL_UPDATED"}
        requests.post("https://indexing.googleapis.com/v3/urlNotifications:publish", json=body, headers=headers)
        print(f"🚀 Sucesso! Indexing API avisou o Google sobre: {target_url}")
    except Exception as e:
        print(f"⚠️ Indexing API Erro: {e}")

# =====================================================================
# MOTOR PRINCIPAL
# =====================================================================

def executar_geracao():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ Erro: GEMINI_API_KEY não configurada.")
        return False

    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    
    # 1. Definir o Tópico (via arquivo temas.txt ou Inteligência Artificial)
    topico = obter_tema_inteligente(client)
    if not topico:
        print("🛑 Geração abortada: Faltou tema para postar.")
        return False

    # 2. Definir variáveis extras (Palavras-chave, Imagens, Links)
    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    
    links_reais = raspar_links_internos_reais()
    link_int1 = random.choice(links_reais)
    link_int2 = random.choice([l for l in links_reais if l != link_int1] or links_reais)

    # 3. Prompt de Escrita para IA
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

    print(f"📝 Gerando corpo do artigo sobre: {topico}...")
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_master)
    content = response.text.strip()
    
    if not content or len(content) < 300:
        print("❌ Resposta inválida da inteligência artificial.")
        return False

    # 4. Tratamento dos Metadados da IA
    cat_match = re.search(r"CATEGORIA_SELECIONADA:\s*(.+)", content)
    tags_match = re.search(r"TAGS_SELECIONADAS:\s*(.+)", content)
    category = cat_match.group(1).strip() if cat_match else "Análises"
    tags = tags_match.group(1).strip() if tags_match else "seo, otimizacao"
    
    content = re.sub(r"CATEGORIA_SELECIONADA:.*\n?", "", content)
    content = re.sub(r"TAGS_SELECIONADAS:.*\n?", "", content)
    content = content.strip()

    # 5. Sanitização de Segurança do Jekyll (Restaurada)
    # Impede que aspas, dois pontos ou colchetes quebrem o deploy do GitHub Pages
    titulo_seguro = topico.replace(":", "").replace("'", "").replace('"', '').replace("[", "").replace("]", "")
    category_safe = category.replace(":", "").replace("'", "").replace('"', '').replace("[", "").replace("]", "")
    tags_safe = tags.replace(":", "").replace("'", "").replace('"', '').replace("[", "").replace("]", "")

    hoje = datetime.now()
    today_str = hoje.strftime('%Y-%m-%d')
    base_slug = slugify(f"{topico} Análise Especializada")
    img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    horario_imediato = "00:01:00" 

    # 6. Montagem do Arquivo Final
    front_matter = f"""---
layout: post
title: "{titulo_seguro} - Análise Especializada"
date: {today_str} {horario_imediato} -0300
categories: ["{category_safe}"]
tags: ["{tags_safe}"]
image: "{img_url}"
img_alt: "Estratégia avançada de {keyword} discutida no portal {CONFIG['COMPANY_NAME']}"
---

"""
    final_output = front_matter + content
    CONFIG['OUTPUT_FOLDER'].mkdir(parents=True, exist_ok=True)
    output_path = CONFIG['OUTPUT_FOLDER'] / f"{today_str}-{base_slug}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"✅ Post publicado com sucesso em: {output_path}")
    url_publicada = f"{CONFIG['COMPANY_WEBSITE']}posts/{base_slug}/"
    
    # 7. Disparo para o Google dependendo da Chave de Controle
    if CONFIG['ENVIAR_PARA_GOOGLE']:
        solicitar_indexacao_google(url_publicada)
    else:
        print("⚠️ Envio para o Google Indexing está DESATIVADO no painel de controle.")
        
    return True

if __name__ == '__main__':
    executar_geracao()
