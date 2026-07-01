#!/usr/bin/env python3
import os
import random
import re
import unicodedata
import requests
from datetime import datetime
from pathlib import Path
from google import genai
from PIL import Image, ImageDraw, ImageFont

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Masters SEO'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://masters-seo.github.io/'),
    'OUTPUT_FOLDER': '_posts',
    
    # Mantenha em 'personalizada' para usar sua imagem com título e faixa preta
    'MODO_IMAGEM': 'personalizada', 
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
    ]
}

def build_prompt(topic, keyword):
    return f"""Você é um Copywriter Sênior de Resposta Direta e Analista Principal do {CONFIG['COMPANY_NAME']}.
Crie um artigo de autoridade, profundo e focado em converter e educar o mercado de marketing e empresários.

TÓPICO: {topic}
PALAVRA-CHAVE PRINCIPAL: {keyword}

DIRETRIZES RÍGIDAS DE ESCRITA (Framework Copywriting Avançado):
1. ESCANEABILIDADE: Escreva em parágrafos muito curtos. Cada parágrafo deve ter no MÁXIMO 2 a 3 linhas. Quebre o texto com frequência para manter a leitura fluida e prazerosa no mobile.
2. TOM: Analítico, informativo, premium e imparcial. Evite termos clichês, exagerados ou excessivamente comerciais ("revolucionário", "descubra o segredo", etc.).
3. ESTRUTURA EDITORIAL:
   - Comece direto no conteúdo (introdução curta com gancho forte).
   - Use intertítulos H2 e H3 claros e focados no benefício da leitura.
   - Sempre adicione elementos visuais de texto como: listas úteis com bullet points, analogias simples ou tabelas comparativas se couber no tema.
   - Conclusão sintetizando a análise prática + CTA discreto convidando a ler as demais auditorias do portal {CONFIG['COMPANY_WEBSITE']}.
   - Seção FAQ contendo de 5 a 7 perguntas reais que o público busca sobre o tema com respostas curtas e diretas.
   - No final absoluto do arquivo, inclua uma sugestão de marcação estruturada Schema JSON-LD relevante em formato de comentário HTML ().

IMPORTANTE: Forneça apenas o Markdown puro do artigo. Não inclua blocos de metadados Front Matter (---), pois o sistema irá gerá-los de forma externa."""

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def gerar_imagem_com_texto(titulo, slug):
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
        for palavra in palavras:
            test_linha = f"{linha_atual} {palavra}".strip()
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
    
    # Define a URL da imagem baseada na regra do Modo 3
    img_url = gerar_imagem_com_texto(title_clean, f"{today_str}-{slug}")
    
    # Geração automatizada do Alt Text amigável usando a palavra-chave sorteada
    alt_text_clean = f"Análise sobre {topic} focando em {keyword} - Portal Masters SEO"
    
    # Front Matter do Jekyll expandido com suporte nativo a caminhos de imagem e Alt Text otimizado
    jekyll_front_matter = f"""---
layout: post
title: "{title_clean}"
date: {today_str} 12:00:00 -0300
image:
  path: {img_url}
  alt: "{alt_text_clean}"
---

"""
    final_markdown = jekyll_front_matter + content
    
    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)
    
    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
        
    print(f"✅ Artigo Jekyll gerado de acordo com as diretrizes em: {file_path}")
    return True

if __name__ == '__main__':
    main()
