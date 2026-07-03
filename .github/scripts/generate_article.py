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
# Nova biblioteca para autenticação automática com a API do Google
from google.oauth2 import service_account
from google.auth.transport.requests import Request
# Tenta ler o painel de testes se ele existir na pasta
try:
    from config_testes import CONFIG_TESTES
except ImportError:
    CONFIG_TESTES = {}

CONFIG = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    # Guarde o conteúdo do JSON da sua Conta de Serviço do Google Cloud nesta variável de ambiente
    'GOOGLE_SERVICE_ACCOUNT_JSON': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', ''),
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
        'Análise independente: O impacto das updates do Google',
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
LINK CONTEXTUAL DO MAYCON MATOS: {contextual_link}
URL DA IMAGEM DO MEIO DO ARTIGO: {secondary_img_url}
ALT TEXT DA IMAGEM DO MEIO: {alt_text_secondary}

DIRETRIZES OBRIGATÓRIAS DE ESCRITA E LAYOUT (Framework Copywriting Avançado):
1. ESCANEABILIDADE MÁXIMA: Escreva o artigo utilizando parágrafos muito curtos. Cada parágrafo deve conter no MÁXIMO 2 a 3 linhas. Quebre o texto constantemente.
2. TOM EDITORIAL: Premium, analítico e imparcial. Sem clichês.
3. ESTRUTURA CRUCIAL REQUERIDA (Siga estritamente esta ordem de blocos):
   - INTRODUÇÃO DIRETA: Comece abordando a dor ou cenário atual.
   - RESUMO RÁPIDO PARA IA: Imediatamente após a introdução, adicione a seção "⚡ Resumo Rápido". Não faça parágrafos aqui. Escreva de 3 a 5 frases soltas, curtas e ultra-impactantes que resumam perfeitamente a resposta principal do artigo.
   - FRASE DE CITAÇÃO EXTRA-GIGANTE: No primeiro terço do artigo, escolha uma frase curta de extremo impacto do texto e insira exatamente usando esta tag HTML para garantir que a fonte fique pelo menos 5 vezes maior que o normal e crie contraste:
     <blockquote style="font-size: 3.5rem; line-height: 1.1; color: #111; font-weight: 800; border-left: 8px solid #000; padding-left: 20px; margin: 40px 0;">"Frase de impacto aqui"</blockquote>
   - IMAGEM INTERMEÁRIA DINÂMICA: Exatamente no meio do desenvolvimento do artigo, insira a imagem secundária fornecida usando a sintaxe Markdown: ![{alt_text_secondary}]({secondary_img_url})
   - ENRIQUECIMENTO: Use intertítulos H2 e H3 baseados em benefícios.
   - Tabelas comparativas responsiva com quebra de linha automatica, sem barra de roalagem.
   - Listas com marcadores ou analogias.
   - LINKAGEM OBRIGATÓRIA REAL E DO-FOLLOW: 
     * Todos os links gerados devem ser links reais e clicáveis usando a sintaxe Markdown [Texto Ancora Contextual](URL) ou HTML. É terminantemente proibido deixar o link em formato de texto cru.
     * Nenhum link pode conter "nofollow". Todos devem ser links padrão (DoFollow) para passar autoridade.
     * Insira de forma fluida no texto 1 ÚNICO link para o site do especialista Maycon Matos usando o endereço exato fornecido: {contextual_link}
     * Insira 2 links internos apontando de forma fictícia para outros artigos do portal {CONFIG['COMPANY_NAME']} usando caminhos relativos como "https://masters-seo.github.io/nome-do-post/".
     * Insira 2 links externos para portais de altíssima autoridade global em SEO (ex: Search Engine Land, Search Engine Journal, Backlinko, Neil Patel ou Google Search Central e outros similares com alta autoridade).
   - CONCLUSÃO E CTA: Conclusão amarrada seguidos de uma chamada para ação sutil direcionando o leitor a explorar as análises no portal {CONFIG['COMPANY_WEBSITE']}.
   - FAQ: Seção robusta contendo entre 5 e 7 dúvidas frequentes, com respostas diretas e curtas.
   - SCHEMA JSON-LD OCULTO: Ao final completo do arquivo, gere o código estruturado Schema JSON-LD (do tipo Article) inteiramente embutido dentro de um comentário HTML padrão para que ele fique invisível na tela para o usuário, mas acessível ao robô do Google, exatamente assim:
     IMPORTANTE SOBRE METADADOS DE SEO DO ARTIGO:
Você deve OBRIGATORIAMENTE analisar o Tópico e o Conteúdo gerado para definir inteligentemente duas propriedades cruciais no início do texto (escreva as duas linhas de forma normal no topo da sua resposta para que o script capture):
1. CATEGORIA: Escolha estritamente APENAS UMA entre estas 6 opções que melhor se adapta contextualmente ao assunto: Análises, SEO Local, SEO Técnico, Estratégia, Mercado ou IA. Escreva exatamente no formato: 'CATEGORIA_SELECIONADA: Sua Categoria Aqui'.
2. TAGS: Defina exatamente 3 tags curtas e estratégicas em minúsculas que complementem e façam sentido direto para o artigo. Escreva no formato: 'TAGS_SELECIONADAS: tag1, tag2, tag3'.

IMPORTANTE: Devolva exclusivamente o código estruturado em Markdown do artigo. Não inclua os blocos delimitadores de metadados Front Matter (---) no início da sua resposta."""

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
        for palavra in palavras:
            test_linha = f"{linha_atual} {palavra}".strip()
            if len(test_linha) * (faixa_altura * 0.18) < W - 60:
                linha_atual = test_linha
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
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

# Nova função injetada para automatizar o pedido de rastreio no Google Search
def solicitar_indexacao_google(target_url):
    if not CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON']:
        print("⚠️ Notificação de indexação ignorada: GOOGLE_SERVICE_ACCOUNT_JSON não configurada.")
        return False
    try:
        info = json.loads(CONFIG['GOOGLE_SERVICE_ACCOUNT_JSON'])
        scopes = ['https://www.googleapis.com/auth/indexing']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)

        # Autentica e gera o Token de Acesso temporário
        credentials.refresh(Request())
        token = credentials.token

        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        body = {
            "url": target_url,
            "type": "URL_UPDATED"
        }

        response = requests.post(endpoint, json=body, headers=headers)
        if response.status_code == 200:
            print(f"🚀 Sucesso! Google Search notificado instantaneamente para indexar: {target_url}")
            return True
        else:
            print(f"❌ Falha ao notificar o Google. Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ Erro ao executar a Indexing API do Google: {e}")
        return False

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

    category_match = re.search(r"CATEGORIA_SELECIONADA:\s*(.+)", content)
    tags_match = re.search(r"TAGS_SELECIONADAS:\s*(.+)", content)

    selected_category = category_match.group(1).strip() if category_match else "Análises"
    selected_tags = tags_match.group(1).strip() if tags_match else "seo, marketing-digital, otimizacao"

    content = re.sub(r"CATEGORIA_SELECIONADA:.*\n?", "", content)
    content = re.sub(r"TAGS_SELECIONADAS:.*\n?", "", content)
    content = content.strip()

    modo = CONFIG['MODO_IMAGEM'].lower()
    image_meta = ""

    if modo == 'unsplash':
        img_url = random.choice(CONFIG['UNSPLASH_POOL'])
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"
    elif modo == 'personalizada':
        img_url = gerar_imagem_com_texto(title_clean, f"{today_str}-{slug}")
        image_meta = f"\nimage: {img_url}\nimg_alt: '{alt_text_clean}'"

# Verificação dinâmica do horário com base no painel de controle
    if CONFIG_TESTES.get('FORCAR_PUBLICACAO_IMEDIATA', False):
        horario_post = "00:01:00"
    else:
        horario_post = "12:00:00"

    jekyll_front_matter = f"""---
layout: post
title: '{title_clean}'
date: {today_str} 12:00:00 -0300
date: {today_str} {horario_post} -0300
categories: '{selected_category}'
tags: [{selected_tags}]{image_meta}
---

"""

"""
    final_markdown = jekyll_front_matter + content

    output_folder = Path(CONFIG['OUTPUT_FOLDER'])
    output_folder.mkdir(parents=True, exist_ok=True)

    file_path = output_folder / f"{today_str}-{slug}.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)

    print(f"✅ Artigo Jekyll de Alta Performance salvo com sucesso em: {file_path}")

    # Executa a Indexação Automática enviando a URL pública gerada para o Google
    # Nota: A rota padrão estruturada pelo Jekyll costuma ser o domínio + /categoria/ano/mes/dia/slug.html ou /ano/mes/dia/slug/
    # Ajuste a montagem abaixo se a estrutura de permalinks do seu site for diferente
    public_post_url = f"{CONFIG['COMPANY_WEBSITE']}blog/{slug}/"
    solicitar_indexacao_google(public_post_url)

    return True

if __name__ == '__main__':
    main()
    
    
