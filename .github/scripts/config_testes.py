#!/usr/bin/env python3
# 🎛️ PAINEL DE CONTROLE DE TESTES (TEMPORÁRIO)
# Altere para True (Ligado) ou False (Desligado) para gerenciar o comportamento do robô

CONFIG_TESTES = {
    # 🟢 BOTÃO 1: Forçar Publicação Imediata
    # Se True, muda o horário do post para 00:01:00, burlando o "Future Date Trap" e aparecendo na Home na hora.
    'FORCAR_PUBLICACAO_IMEDIATA': True,

    # 🔵 BOTÃO 2: Forçar Modelo de Texto Estático
    # Se True, ignora o Orquestrador e roda sempre o Script V1 (Tópicos).
    'FORCAR_MODELO_ESTATICO': False,

    # 🔴 BOTÃO 3: Forçar Modelo do YouTube
    # Se True, ignora o Orquestrador e roda sempre o Script V2 (Vídeos).
    'FORCAR_MODELO_YOUTUBE': True,

    # 🟡 BOTÃO 4: Desativar Indexação no Google Search Console
    # Se True, impede que o script gaste sua cota da Indexing API enquanto você faz testes.
    'DESATIVAR_INDEXING_API': False,
}
