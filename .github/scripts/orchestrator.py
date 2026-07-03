#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Garante que o diretório base esteja no PATH para importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# =====================================================================
# ROTINA DE AUTOLIMPEZA CRÍTICA (Remove arquivos clonados/conflitos e cache)
# =====================================================================
def realizar_limpeza_de_seguranca():
    # 1. Remove arquivos locais que possam mimetizar a biblioteca oficial
    for nome_fantasma in ["youtube_transcript_api.py", "youtube_transcript_api"]:
        caminho_fantasma = os.path.join(script_dir, nome_fantasma)
        if os.path.exists(caminho_fantasma):
            try:
                if os.path.isdir(caminho_fantasma):
                    import shutil
                    shutil.rmtree(caminho_fantasma)
                else:
                    os.remove(caminho_fantasma)
                print(f"🧹 [Autolimpeza]: Arquivo de conflito removido: {nome_fantasma}")
            except Exception as e:
                print(f"⚠️ Falha ao limpar {nome_fantasma}: {e}")

    # 2. Remove caches do Python (__pycache__) para evitar que guarde o erro antigo
    for root, dirs, files in os.walk(script_dir):
        if "__pycache__" in dirs:
            caminho_cache = os.path.join(root, "__pycache__")
            try:
                import shutil
                shutil.rmtree(caminho_cache)
            except:
                pass

# Executa a limpeza imediatamente antes de qualquer importação sensível
realizar_limpeza_de_seguranca()

try:
    # Tenta importar o arquivo de configuração, se não existir, usa dict vazio
    from config_testes import CONFIG_TESTES
except ImportError:
    CONFIG_TESTES = {}

def rodar_script(nome_script):
    """Executa um script Python em um sub-processo."""
    caminho = os.path.join(script_dir, nome_script)
    if not os.path.exists(caminho):
        print(f"❌ Erro: O arquivo {nome_script} não foi encontrado em {caminho}")
        return False
        
    print(f"🚀 Iniciando execução de: {nome_script}...")
    # Executa usando o mesmo interpretador atual
    resultado = subprocess.run([sys.executable, caminho])
    return resultado.returncode == 0

def main():
    # Verifica modos de forçar execução via config
    if CONFIG_TESTES.get('FORCAR_MODELO_ESTATICO', False):
        print("🎛️ [Painel Ativo]: Forçando Modelo Estático (Pautas)...")
        rodar_script("generate_article.py")
        return

    if CONFIG_TESTES.get('FORCAR_MODELO_YOUTUBE', False):
        print("🎛️ [Painel Ativo]: Forçando Modelo YouTube (Vídeos)...")
        if not rodar_script("youtube_script.py"):
            print("🚨 Falha no script do YouTube. Fallback para Modelo Estático...")
            rodar_script("generate_article.py")
        return

    # Orquestração por dias pares/ímpares
    dia_do_ano = datetime.now().timetuple().tm_yday
    
    if dia_do_ano % 2 == 0:
        print(f"📅 [Dia {dia_do_ano} - Par]: Selecionando Modelo YouTube...")
        if not rodar_script("youtube_script.py"):
            print("🚨 Falha no YouTube. Ativando Fallback para Modelo Estático...")
            rodar_script("generate_article.py")
    else:
        print(f"📅 [Dia {dia_do_ano} - Ímpar]: Selecionando Modelo Estático...")
        rodar_script("generate_article.py")

if __name__ == '__main__':
    main()
