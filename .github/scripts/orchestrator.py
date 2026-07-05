#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

# Tenta ler o painel de testes se ele existir na mesma pasta
try:
    from config_testes import CONFIG_TESTES
except ImportError:
    CONFIG_TESTES = {}

def rodar_script(nome_script):
    caminho = os.path.join(os.path.dirname(__file__), nome_script)
    return subprocess.run(["python", caminho]).returncode == 0

def main():
    # 1. Verifica se há botões forçados no Painel de Testes
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

    # 2. Se nenhum botão estiver forçado, segue a regra padrão de par/ímpar do dia do ano
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
