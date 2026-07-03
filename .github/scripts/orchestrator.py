#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

# Garante que o Python consiga encontrar módulos na mesma pasta deste script
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from config_testes import CONFIG_TESTES
except ImportError:
    CONFIG_TESTES = {}

def rodar_script(nome_script):
    caminho = os.path.join(script_dir, nome_script)
    # Executa o script passando o mesmo interpretador Python atual
    return subprocess.run([sys.executable, caminho]).returncode == 0

def main():
    if CONFIG_TESTES.get('FORCAR_MODELO_ESTATICO', False):
        print("🎛️ [Painel Ativo]: Forçando Modelo Estático (Pautas)...")
        rodar_script("generate_article.py")
        return

    if CONFIG_TESTES.get('FORCAR_MODELO_YOUTUBE', False):
        print("🎛️ [Painel Ativo]: Forçando Modelo YouTube (Vídeos)...")
        sucesso = rodar_script("youtube_script.py")
        if not sucesso:
            print("🚨 Falha no script do YouTube selecionado. Iniciando Fallback para o Modelo Estático...")
            rodar_script("generate_article.py")
        return

    dia_do_ano = datetime.now().timetuple().tm_yday
    
    if dia_do_ano % 2 == 0:
        print("📅 [Dia Par]: Orquestrador selecionou o Modelo YouTube...")
        sucesso = rodar_script("youtube_script.py")
        if not sucesso:
            print("🚨 Falha ou banco de vídeos esgotado. Ativando Fallback para o Modelo Estático...")
            rodar_script("generate_article.py")
    else:
        print("📅 [Dia Ímpar]: Orquestrador selecionou o Modelo Estático (Pautas)...")
        rodar_script("generate_article.py")

if __name__ == '__main__':
    main()
