#!/usr/bin/env python3
import os
import random
import re
import unicodedata
import requests
from datetime import datetime
from pathlib import Path
from google import genai

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': '_posts',
    'MODO_IMAGEM': 'unsplash', 
    'URL_IMAGEM_PADRAO': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&auto=format&fit=crop&q=80',
    
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
        'https://mayconmatos.com.br/recursos/',
        'https://mayconmatos.com.br/servicos/',
        'https://mayconmatos.com.br/politica-de-privacidade-e-cookies/',
        'https://mayconmatos.com.br/servicos/iscas-digitais/',
        'https://mayconmatos.com.br/servicos/consultoria/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/itajai/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/navegantes/',
        'https://mayconmatos.com.br/servicos/seo-local/',
        'https://mayconmatos.com.br/servicos/seo-local/navegantes/',
        'https://mayconmatos.com.br/servicos/criacao-de-sites/',
        'https://mayconmatos.com.br/consultor-de-seo-para-google-e-ia/',
        'https://mayconmatos.com.br/blog/como-melhorar-nota-pagespeed/',
        'https://mayconmatos.com.br/blog/advocacia/como-captar-clientes-na-advocacia/'
    ]
}

def build_prompt(topic, keyword, contextual_link, secondary_img_url, alt_text_secondary):
    return f"""Você é um Copywriter Sênior de Resposta Direta e Analista Principal do {CONFIG['COMPANY_NAME']}.
Crie um artigo de autoridade profunda, altamente persuasivo, claro e totalmente otimizado para SEO semântico.

TÓPICO: {topic}
PALAVRA-CHAVE PRINCIPAL: {keyword}
LINK CONTEXTUAL OBRIGATÓRIO: {contextual_link}
URL DA IMAGEM DO MEIO DO ARTIGO: {secondary_img_url}
ALT TEXT DA IMAGEM DO MEIO: {alt_text_secondary}

DIRETRIZES OBRIGATÓRIAS DE ESCRITA E LAYOUT (Framework Copywriting Avançado):
1. ESCANEABILIDADE MÁXIMA: Escreva o artigo utilizando parágrafos muito curtos. Cada parágrafo deve conter no MÁXIMO 2 a 3 linhas. Quebre o texto constantemente para garantir uma leitura fluida no ambiente mobile.
2. TOM EDITORIAL: Premium, analítico e imparcial. Elimine adjetivos vazios ou clichês comerciais espalhafatosos.
3. ESTRUTURA CRUCIAL REQUERIDA (Siga estritamente esta ordem de blocos):
   - INTRODUÇÃO DIRETA: Comece sem enrolação, abordando a dor ou cenário atual.
   - RESUMO RÁPIDO (Destaque de Snippet / Resposta para IA): Imediatamente após a introdução, adicione uma seção chamada "⚡ Resumo Rápido" contendo uma resposta ultra-direta e curta sobre o tema principal do artigo para que motores de IA capturem facilmente.
   - FRASE DE CITAÇÃO IMPACTANTE: No primeiro terço do artigo, insira uma frase de forte impacto destacada em formato de citação Markdown (> "Frase impactante aqui"), ideal para criar contraste visual no layout.
   - IMAGEM INTERMEÁRIA DINÂMICA: Exatamente no meio do desenvolvimento do artigo, insira a imagem secundária fornecida usando a sintaxe clássica Markdown: ![{alt_text_secondary}]({secondary_img_url})
   - ENRIQUECIMENTO: Use intertítulos H2 e H3 baseados em benefícios, tabelas comparativas, listas com marcadores (bullet points) ou analogias práticas.
   - LINKAGEM ESTRATÉGICA NATURAL (Use textos-âncora contextuais e fluidos):
     * Insira obrigatoriamente o LINK CONTEXTUAL OBRIGATÓRIO ({contextual_link}) apontando para o site do especialista Maycon Matos de forma contextualizada.
     * Insira 2 links internos apontando de forma fictícia para outros artigos do portal {CONFIG['COMPANY_NAME']} usando caminhos como "/blog/" ou "/nome-do-post/".
     * Insira 2 links externos para portais globais de altíssima autoridade e confiança em SEO (ex: Search Engine Land, Search Engine Journal, Backlinko, Neil Patel ou Google Search Central).
   - CONCLUSÃO E CTA: Conclusão amarrando os dados seguidos de uma chamada para ação sutil direcionando o leitor a explorar as análises no portal {CONFIG['COMPANY_WEBSITE']}.
   - FAQ: Seção robusta contendo entre 5 e 7 dúvidas reais e frequentes sobre o tema, com respostas diretas e curtas.
   - SCHEMA JSON-LD OCULTO: Ao final completo do arquivo, gere o código estruturado Schema JSON-LD (do tipo Article). É OBRIGATÓRIO envelopar o bloco do script inteiramente dentro de um comentário HTML padrão para que ele fique invisível na tela para o usuário, mas acessível ao robô do Google, exatamente assim:
     IMPORTANTE: Devolva exclusivamente o código estruturado em Markdown do artigo. Não inclua os blocos delimitadores de metadados Front Matter (---) no início da sua resposta, pois eles já são gerenciados dinamicamente pelo sistema."""

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def gerar_imagem_com_texto(titulo, slug):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚠️ Biblioteca 'Pillow' não instalada. Usando fallback.")
        return CONFIG['URL_IMAGEM_PADRAO']

    try:
        img_data = requests.get(CONFIG['URL_IMAGEM_PADRAO']).content
        img_path = Path("temp_base.jpg")
        with open(img_path, 'wb') as f:
            f.write(img_data)
        
        img = Image.open(img_path).convert("RGBA")
        W, H = img.size
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        faixa_altura = int(H * 0.25)
        y0 = (H - faixa_altura) // 2
        y1 = y0 + faixa_altura
        
        draw.rectangle(((0, y0), (W, y1)), fill=(0, 0, 0, 128))
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(faixa_altura * 0.28))
        except IOError:
            font = ImageFont.load_default()
            
        palavras = titulo.split()
        linhas = []
        linha_atual = ""
        for palabra in palavras:
            test_linha = f"{linha_atual} {palabra}".strip()
            if len(test_linha) * (faixa_altura * 0.18) < W - 60:
                linha_atual = test_linha
            else:
                linhas.append(linha_atual)
                linha_atual = palabra
        linhas.append(linha_atual)
        
        draw_txt = ImageDraw.Draw(overlay)
        total_texto_h = len(linhas) * int(faixa_altura * 0.35)
        current_y = y0 + (faixa_altura - total_texto_h) // 2
        
        for linha in linhas:
            draw_txt.text((W // 2, current_y), linha, fill=(255, 255, 255, 255), font=font, anchor="mm")
            current_y += int(faixa_altura * 0.35)
            
        img_final = Image.alpha_composite(img, overlay).convert("RGB")
        assets_folder = Path("assets/img/posts")
        assets_folder.mkdir(parents=True, exist_ok=True)
        
        final_img_path = assets_folder / f"{slug}.jpg"
        img_final.save(final_img_path, "JPEG")
        
        if img_path.exists():
            img_path.unlink()
            
        return f"/{final_img_path}"
    except Exception as e:
        print(f"⚠️ Erro ao gerar imagem customizada: {e}")
        return CONFIG['URL_IMAGEM_PADRAO']

def main():
    if not CONFIG['GEMINI_API_KEY']:
        print("❌ GEMINI_API_KEY ausente.")
        return False
        
    topic = random.choice(CONFIG['TOPICS'])
    keyword = random.choice(CONFIG['KEYWORDS'])
    contextual_link = random.choice(CONFIG['MAYCON_LINKS'])
    
    secondary_img_url = random.choice(CONFIG['UNSPLASH_POOL'])
    
    client = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])
    print(f"Gerando artigo otimizado sobre: {topic}")
    
    title_clean = f"{topic} - Análise Especializada"
    slug = slugify(topic)
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    alt_text_clean = f"Análise editorial focada em {keyword} abordando {topic} - Portal {CONFIG['COMPANY_NAME']}"
    alt_text_secondary = f"Gráfico informativo sobre estratégias de {keyword} e otimização semântica."
    
    prompt_final = build_prompt(topic, keyword, contextual_link, secondary_img_url, alt_text_secondary)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_final,
    )
    
    content = response.text.strip()
    if not content or len(content) < 300:
        print("❌ Conteúdo gerado é inválido ou curto demais.")
        return False
        
    modo = CONFIG['MODO_IMAGEM'].lower()
    image_meta = ""
    
    # CORREÇÃO CRUCIAL AQUI: Formatação limpa do bloco de imagem aceita pelo parser YAML do Jekyll
    if modo == 'unsplash':
        img_url = random.choice(CONFIG['UNSPLASH_POOL'])
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"
    elif modo == 'personalizada':
        img_url = gerar_imagem_com_texto(title_clean, f"{today_str}-{slug}")
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"
    
    # Título encapsulado com aspas simples para blindar aspas duplas internas geradas pela IA
    jekyll_front_matter = f"""---
layout: post
title: '{title_clean}'
date: {today_str} 12:00:00 -0300{image_meta}
---

"""
    final_markdown = jekyll_front_matter + content
    
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
        
    print(f"✅ Artigo Jekyll de Alta Performance salvo com sucesso em: {file_path}")
    return True

if __name__ == '__main__':
    main()
