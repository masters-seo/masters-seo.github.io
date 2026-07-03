#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Garante que o diretório base esteja no PATH para importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

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

# Carrega a configuração isolando o escopo para evitar execuções acidentais no import
CONFIG_TESTES = {}
try:
    import config_testes
    if hasattr(config_testes, 'CONFIG_TESTES'):
        CONFIG_TESTES = config_testes.CONFIG_TESTES
except Exception as e:
    print(f"⚠️ Erro ao carregar config_testes: {e}")

def rodar_script(nome_script):
    """Executa um script Python em um sub-processo de forma isolada."""
    caminho = os.path.join(script_dir, nome_script)
    if not os.path.exists(caminho):
        print(f"❌ Erro: O arquivo {nome_script} não foi encontrado em {caminho}")
        return False
        
    print(f"🚀 Iniciando execução isolada de: {nome_script}...")
    resultado = subprocess.run([sys.executable, caminho], capture_output=False)
    return resultado.returncode == 0

def main():
    # 🔴 BLOQUEIO TOTAL DE CRÉDITOS: Se o modelo estático for forçado por engano, cancela.
    if CONFIG_TESTES.get('FORCAR_MODELO_ESTATICO', False):
        print("🛑 [Proteção de Créditos]: Geração estática cancelada por diretiva de segurança.")
        sys.exit(0)

    print("🎛️ [Orquestrador]: Modo Exclusivo YouTube Ativo.")

    if CONFIG_TESTES.get('FORCAR_MODELO_YOUTUBE', False):
        print("🎛️ [Painel Ativo]: Forçando Modelo YouTube (Vídeos)...")
        if not rodar_script("youtube_script.py"):
            print("🛑 [Proteção de Créditos]: O script do YouTube falhou. Processo interrompido para salvar tokens.")
            sys.exit(1)
        return

    # Orquestração por dias se nenhum botão estiver forçado
    dia_do_ano = datetime.now().timetuple().tm_yday
    
    if dia_do_ano % 2 == 0:
        print(f"📅 [Dia {dia_do_ano} - Par]: Selecionando Modelo YouTube...")
        if not rodar_script("youtube_script.py"):
            print("🛑 [Proteção de Créditos]: O script do YouTube falhou. Processo interrompido para salvar tokens.")
            sys.exit(1)
    else:
        # Nos dias ímpares, em vez de gastar tokens gerando artigos genéricos, o script pula a execução com segurança.
        print(f"📅 [Dia {dia_do_ano} - Ímpar]: Modelo Estático Ignorado para poupar saldo da API.")
        sys.exit(0)

if __name__ == '__main__':
    main()
