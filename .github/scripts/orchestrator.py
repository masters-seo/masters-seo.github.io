import os
import sys
from google import genai

# Configuração simples
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Masters SEO')

if not GEMINI_API_KEY:
    print("❌ Erro: GEMINI_API_KEY não encontrada.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

def gerar_conteudo(tema):
    """Gera o artigo estruturado com base em um tema."""
    print(f"🤖 Gerando artigo sobre: {tema}...")
    prompt = f"""
    Crie um artigo completo em Markdown para o blog {COMPANY_NAME}.
    Tema: {tema}
    O artigo deve ser profundo, profissional e focado em SEO.
    Use H2 e H3 para subtítulos. Inclua uma conclusão e uma seção de FAQ no final.
    Não use delimitadores de código (```).
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt
    )
    return response.text

def obter_temas_em_alta():
    """Busca sugestões de SEO caso não haja tópicos definidos."""
    print("🔍 Nenhum tópico definido, buscando tendências de SEO...")
    prompt = "Liste 3 tópicos de SEO em alta no mercado brasileiro hoje. Responda apenas com os temas, separados por vírgula."
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    temas = [t.strip() for t in response.text.split(',')]
    return temas[:1] # Pega o primeiro tema da lista

def salvar_artigo(titulo, conteudo):
    """Salva o conteúdo na pasta _posts/."""
    nome_arquivo = f"_posts/{titulo.lower().replace(' ', '-')}.md"
    os.makedirs('_posts', exist_ok=True)
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"✅ Artigo salvo em: {nome_arquivo}")

def main():
    # Aqui você pode definir seus tópicos fixos ou deixar vazio para buscar tendências
    topicos = [] 
    
    if not topicos:
        topicos = obter_temas_em_alta()
    
    for tema in topicos:
        artigo = gerar_conteudo(tema)
        salvar_artigo(tema, artigo)

if __name__ == "__main__":
    main()
