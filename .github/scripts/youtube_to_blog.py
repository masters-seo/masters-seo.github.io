#!/usr/bin/env python3
"""
Auto Blog Generator - YouTube Version
Extrai transcrições de vídeos YouTube e gera artigos automaticamente via Gemini AI.
Executa 1 vídeo por dia da fila configurada.
"""

import os
import sys
import random
import re
import unicodedata
import requests
import json
import subprocess
from datetime import datetime
from pathlib import Path
import traceback
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== INSTALAÇÃO DE DEPENDÊNCIAS ====================

def instalar_dependencias():
    """Instala as bibliotecas necessárias."""
    dependencias = [
        'google-generativeai',
        'requests',
        'youtube-transcript-api',
    ]
    for lib in dependencias:
        try:
            __import__(lib.replace('-', '_'))
        except ImportError:
            logger.info(f"Instalando {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "-q"])

instalar_dependencias()

# Agora importa após garantir que estão instaladas
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    import google.generativeai as genai
except ImportError as e:
    logger.error(f"Erro ao importar bibliotecas: {e}")
    sys.exit(1)

# ==================== CONFIGURAÇÃO ====================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = Path(SCRIPT_DIR).parent.parent

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': RAIZ_PROJETO / '_posts',
    
    'KEYWORDS': [
        'experts de seo', 'melhores profissionais de seo', 'analise de seo', 
        'consultor de seo', 'curso de seo avaliacao', 'otimizacao para IA'
    ],
    
    'UNSPLASH_POOL': [
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&auto=format&fit=crop&q=60',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=60',
    ],
    
    'MAYCON_LINKS': [
        'https://mayconmatos.com.br/',
        'https://mayconmatos.com.br/recursos/diagnostico-presenca-digital/',
        'https://mayconmatos.com.br/pagespeed-insights-vs-maycon-matos-seo/',
        'https://mayconmatos.com.br/servicos/seo-local/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/'
    ]
}

# ==================== BANCO DE VÍDEOS YOUTUBE ====================

YOUTUBE_DATABASE = {
    "neilpatel": [
        "https://www.youtube.com/watch?v=H7m6myWuwII",
        "https://www.youtube.com/watch?v=k8aFgaUTe_I",
        "https://www.youtube.com/watch?v=WQHJcSiTc7s"
    ],
    "@RankMath": [
        "https://www.youtube.com/watch?v=VBRgIcXIxB0",
        "https://www.youtube.com/watch?v=T1iqDNgkxeI",
        "https://www.youtube.com/watch?v=sWpPqXXmi8o"
    ],
    "@AhrefsCom": [
        "https://www.youtube.com/watch?v=Sk8MAbD39Qw",
        "https://www.youtube.com/watch?v=uza9GX0E2mw"
    ]
}

# ==================== FUNÇÕES UTILITÁRIAS ====================

def extrair_video_id(url):
    """Extrai ID do vídeo da URL."""
    match = re.search(r"(?:v=|\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def video_ja_processado(video_id):
    """Verifica se o vídeo já foi processado antes."""
    folder = Path(CONFIG['OUTPUT_FOLDER'])
    if not folder.exists():
        return False

    for post in folder.glob("*.md"):
        try:
            content = post.read_text(encoding='utf-8')
            if f"youtube_id: {video_id}" in content:
                logger.info(f"📌 Vídeo {video_id} já processado (arquivo: {post.name})")
                return True
        except Exception as e:
            logger.warning(f"Erro ao ler {post.name}: {e}")
            continue
    return False

def obter_metadados_youtube(url):
    """Obtém título e autor do vídeo via API oEmbed do YouTube."""
    try:
        res = requests.get(
            f"https://www.youtube.com/oembed?url={url}&format=json",
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            return data.get('title'), data.get('author_name')
    except Exception as e:
        logger.warning(f"Erro ao obter metadados: {e}")
    return None, None

def obter_transcricao(video_id):
    """Obtém a transcrição do vídeo."""
    try:
        logger.info(f"📝 Requisitando transcrição para vídeo: {video_id}")
        
        # Tenta português primeiro, depois inglês
        for idioma in ['pt', 'en']:
            try:
                lista = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=[idioma]
                )
                transcricao = " ".join([item['text'] for item in lista])
                logger.info(f"✅ Transcrição obtida em {idioma} ({len(transcricao)} caracteres)")
                return transcricao
            except Exception:
                continue
        
        # Se nenhum idioma específico funcionar, tenta qualquer um
        try:
            lista = YouTubeTranscriptApi.get_transcript(video_id)
            transcricao = " ".join([item['text'] for item in lista])
            logger.info(f"✅ Transcrição obtida (qualquer idioma) ({len(transcricao)} caracteres)")
            return transcricao
        except Exception as e:
            logger.error(f"❌ Nenhuma transcrição disponível: {e}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao obter transcrição: {e}")
        return None

def build_youtube_prompt(titulo_video, canal_autor, transcricao, keyword):
    """Constrói o prompt para o Gemini."""
    
    # Limita a transcrição se for muito longa (economiza tokens)
    if len(transcricao) > 8000:
        transcricao = transcricao[:8000] + "... [conteúdo truncado]"
    
    return f"""Você é um Copywriter Sênior especializado em SEO e Marketing Digital para o {CONFIG['COMPANY_NAME']}.

Crie um artigo de blog profissional, claro e totalmente otimizado para SEO adaptando o conteúdo de uma transcrição de vídeo.

**INFORMAÇÕES DO VÍDEO:**
- Título: {titulo_video}
- Autor/Canal: {canal_autor}
- Palavra-chave principal: {keyword}

**TRANSCRIÇÃO DO VÍDEO:**
{transcricao}

**INSTRUÇÕES:**
1. Reescreva o conteúdo em formato de artigo completo (1500-2500 palavras)
2. Use linguagem clara e profissional, focada em {keyword}
3. Estruture com H2 e H3 para subtítulos
4. Incluir listas com bullet points onde apropriado
5. Adicione uma seção de FAQ no final
6. Mantenha o contexto do mercado brasileiro
7. Termine com um resumo e chamada para ação
8. NÃO inclua delimitadores YAML ou Front Matter no texto

Comece direto no conteúdo do artigo."""

def slugify(text):
    """Converte texto em slug válido para URL."""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def encontrar_proximo_video():
    """Encontra o próximo vídeo não processado da fila."""
    canais_disponiveis = sorted(list(YOUTUBE_DATABASE.keys()))
    
    # Usa dia do ano para rodar diferentes vídeos em diferentes dias
    dia_do_ano = datetime.now().timetuple().tm_yday
    
    logger.info(f"🔍 Procurando próximo vídeo não processado (dia {dia_do_ano})...")
    
    # Tenta encontrar um vídeo que ainda não foi processado
    for i in range(len(canais_disponiveis)):
        idx = (dia_do_ano + i) % len(canais_disponiveis)
        canal = canais_disponiveis[idx]
        urls = YOUTUBE_DATABASE[canal]
        
        for url in urls:
            video_id = extrair_video_id(url)
            if video_id and not video_ja_processado(video_id):
                logger.info(f"🎯 Vídeo encontrado: {video_id} (Canal: {canal})")
                return url, video_id, canal
    
    logger.warning("⚠️ Nenhum vídeo novo disponível na fila!")
    return None, None, None

def gerar_artigo_youtube(video_url, video_id, canal):
    """Gera artigo a partir de um vídeo YouTube."""
    try:
        logger.info(f"🎬 Processando vídeo: {video_url}")
        
        # 1. Obter metadados
        titulo_video, canal_autor = obter_metadados_youtube(video_url)
        if not titulo_video:
            titulo_video = f"Insights de SEO - {canal}"
            canal_autor = canal
        
        logger.info(f"📌 Título: {titulo_video}")
        logger.info(f"👤 Autor: {canal_autor}")
        
        # 2. Obter transcrição
        transcricao = obter_transcricao(video_id)
        if not transcricao or len(transcricao) < 100:
            logger.error("❌ Transcrição inválida ou muito curta")
            return False
        
        logger.info(f"📊 Transcrição: {len(transcricao)} caracteres")
        
        # 3. Gerar conteúdo com Gemini
        if not CONFIG['GEMINI_API_KEY']:
            logger.error("❌ GEMINI_API_KEY não configurada")
            return False
        
        logger.info("🤖 Gerando conteúdo com Gemini AI...")
        
        keyword = random.choice(CONFIG['KEYWORDS'])
        prompt = build_youtube_prompt(titulo_video, canal_autor, transcricao, keyword)
        
        genai.configure(api_key=CONFIG['GEMINI_API_KEY'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        if not content or len(content) < 300:
            logger.error("❌ Conteúdo gerado é inválido ou muito curto")
            return False
        
        logger.info(f"✅ Conteúdo gerado: {len(content)} caracteres")
        
        # 4. Criar iframe do YouTube
        youtube_embed = f"""
<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 2rem 0; border-radius: 8px;">
  <iframe src="https://www.youtube.com/embed/{video_id}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe>
</div>

> **Vídeo original:** "{titulo_video}" por {canal_autor}

---

"""
        content = youtube_embed + content
        
        # 5. Criar Front Matter
        today = datetime.now().strftime('%Y-%m-%d')
        slug = slugify(titulo_video)[:50]  # Limita comprimento
        
        front_matter = f"""---
layout: post
title: '{titulo_video}'
date: {today}
categories: 'análises'
tags: [seo, youtube, análise]
youtube_id: {video_id}
---

"""
        
        # 6. Salvar arquivo
        output_folder = Path(CONFIG['OUTPUT_FOLDER'])
        output_folder.mkdir(parents=True, exist_ok=True)
        
        file_path = output_folder / f"{today}-{slug}.md"
        
        # Evita sobrescrita
        if file_path.exists():
            logger.warning(f"⚠️ Arquivo já existe: {file_path}")
            file_path = output_folder / f"{today}-{slug}-{datetime.now().strftime('%H%M%S')}.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(front_matter + content)
        
        logger.info(f"✅ Artigo salvo: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar artigo: {e}")
        traceback.print_exc()
        return False

# ==================== MAIN ====================

def main():
    logger.info("=" * 60)
    logger.info("🚀 Auto Blog Generator - YouTube Version")
    logger.info("=" * 60)
    
    # Encontrar próximo vídeo
    video_url, video_id, canal = encontrar_proximo_video()
    
    if not video_url:
        logger.info("ℹ️ Nenhum vídeo pendente. Encerrando.")
        return 0
    
    # Gerar artigo
    sucesso = gerar_artigo_youtube(video_url, video_id, canal)
    
    logger.info("=" * 60)
    if sucesso:
        logger.info("✅ Pipeline executado com sucesso!")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("❌ Falha ao gerar artigo")
        logger.info("=" * 60)
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
