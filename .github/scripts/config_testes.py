#!/usr/bin/env python3
# 🎛️ PAINEL DE CONTROLE DE TESTES (TEMPORÁRIO)

CONFIG_TESTES = {
    # 🟢 BOTÃO 1: Forçar Publicação Imediata
    'FORCAR_PUBLICACAO_IMEDIATA': True,

    # 🔵 BOTÃO 2: Forçar Modelo de Texto Estático
    'FORCAR_MODELO_ESTATICO': False,

    # 🔴 BOTÃO 3: Forçar Modelo do YouTube
    'FORCAR_MODELO_YOUTUBE': True,

    # 🟡 BOTÃO 4: Desativar Indexação no Google Search Console
    'DESATIVAR_INDEXING_API': False,
}

def solicitar_indexacao_google(target_url):
    """
    TRAVA DE SEGURANÇA: Retorna False imediatamente para impedir envios ao Google Search Console
    durante a fase de homologação e testes da esteira do YouTube.
    """
    print(f"🟡 Indexação pulada (Modo de Testes Ativo) para: {target_url}")
    return False
