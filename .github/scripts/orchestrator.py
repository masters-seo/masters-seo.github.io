#!/usr/bin/env python3
from datetime import datetime
import subprocess
import os

def main():
    dia_do_ano = datetime.now().timetuple().tm_yday
    
    # Se o dia do ano for Par, a prioridade é o YouTube. Se for Ímpar, o Modelo 1 por Pautas de Texto.
    if dia_do_ano % 2 == 0:
        print("📅 [Dia Par]: Escolhido Modelo 2 (YouTube)...")
        # Executa o Script do YouTube apontando para a pasta correta de scripts
        sucesso = subprocess.run(["python", ".github/scripts/blog_generator_v2_youtube.py"]).returncode == 0
        
        # MODO FALLBACK: Se o script do YouTube falhar ou estiver sem conteúdo, roda o V1 imediatamente
        if not sucesso:
            print("🚨 Falha no Modelo YouTube (ou banco de vídeos esgotado). Iniciando Fallback Automático para o Modelo 1...")
            subprocess.run(["python", ".github/scripts/blog_generator_v1.py"])
            
    else:
        print("📅 [Dia Ímpar]: Escolhido Modelo 1 (Textos estruturados padrão)...")
        subprocess.run(["python", ".github/scripts/blog_generator_v1.py"])

if __name__ == '__main__':
    main()
