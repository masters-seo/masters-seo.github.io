# 🚀 Blog Content AI Generator

Gerador automático de artigos de blog usando IA (Gemini, Claude, Grok) com publicação automática no GitHub. **Configure uma vez, gere infinitos artigos sem interação manual.**

---

## 📋 Características

✅ **Totalmente Autônomo** - Roda agendado, sem sua interação  
✅ **Múltiplas IAs** - Gemini (grátis), Claude, Grok  
✅ **GitHub Integrado** - Publica automaticamente em pull requests ou commits  
✅ **Painel Web** - Interface intuitiva para configuração  
✅ **Google Sheets** - Histórico e logs automáticos  
✅ **SEO-Otimizado** - Segue seu framework "SEO Local Strategist"  
✅ **Framework Profissional** - Template de artigo pilar estruturado  

---

## 🎯 Opções de Uso

Você tem **3 formas** de usar este gerador:

### 1️⃣ **Painel Web + Google Apps Script** (Recomendado para você)
- Painel visual em HTML (blog-generator-dashboard.html)
- Google Apps Script para automação
- Roda em horários agendados
- Logs em Google Sheets
- **Ideal para: Controle total + interface amigável**

### 2️⃣ **GitHub Actions** (Automação pura)
- Workflow YAML no repositório
- Roda no servidor do GitHub
- Zero custo, automático
- Publica direto em Pull Requests
- **Ideal para: Publicação contínua**

### 3️⃣ **Script Python Local** (Desenvolvimento/Testes)
- Rode localmente na sua máquina
- Gere artigos sob demanda
- **Ideal para: Testes e customização**

---

## ⚙️ SETUP - Opção 1️⃣ (Google Sheets + Google Apps Script)

Esta é a opção **mais completa e fácil** para você.

### Passo 1: Obter as Chaves de API

#### 🔑 Google Gemini (GRÁTIS)
1. Vá para https://aistudio.google.com/apikey
2. Clique em "Get API Key"
3. Crie uma nova chave de projeto
4. **Copie a chave** (você vai usar)

#### 🔑 Anthropic Claude (Opcional)
1. Vá para https://console.anthropic.com/keys
2. Crie uma nova chave
3. **Copie a chave**

#### 🔑 GitHub Token
1. Vá para https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Permissões necessárias: ✅ `repo` (acesso completo)
4. **Copie o token**

### Passo 2: Criar Google Sheet + Google Apps Script

1. Crie um novo Google Sheet em https://sheets.google.com
2. Renomeie para "Blog Generator"
3. Copie o ID da URL (está entre `/d/` e `/edit`)
   ```
   https://docs.google.com/spreadsheets/d/AQUI-ESTA-O-ID/edit
   ```

4. Vá em **Extensões > Apps Script**
5. Cole todo o código de `GAS-BlogGenerator.gs`
6. Procure por `const CONFIG` e edite:

```javascript
const CONFIG = {
  GEMINI_API_KEY: 'sua-chave-gemini-aqui', // ← Cole aqui
  CLAUDE_API_KEY: 'sua-chave-claude-aqui', // ← Cole aqui
  GITHUB_TOKEN: 'seu-token-github-aqui',    // ← Cole aqui
  GITHUB_REPO: 'seu-usuario/seu-repositorio', // Ex: maycon/blog
  // ... resto da config
};

const SHEET_ID = 'AQUI-ESTA-O-ID-DO-SHEET'; // ← Cole o ID
```

7. **Salve** (Ctrl+S)

### Passo 3: Abrir o Painel

1. Salve o arquivo `blog-generator-dashboard.html` em um lugar seguro
2. Abra no navegador (double-click)
3. Preencha todos os campos:
   - ✏️ Dados da Empresa
   - 🔑 Configuração de APIs
   - 📝 Estratégia de Conteúdo

4. Clique em **"💾 Salvar Configurações"**

### Passo 4: Configurar Automação

No Google Sheets:

1. Vá em **Extensões > Apps Script**
2. Execute a função `setupTrigger()`:
   - Clique no ▶️ play
   - Selecione `setupTrigger`
   - Clique ▶️ novamente

3. **Autorize** quando solicitado

✅ **Pronto!** Seu gerador vai rodar **todos os dias às 9:00 AM** automaticamente.

### Testar Manualmente

No painel dashboard:
1. Selecione um **Tópico**
2. Selecione uma **Palavra-Chave**
3. Clique em **"✨ Gerar com Gemini"** ou **"✨ Gerar com Claude"**
4. Após gerar, clique em **"🚀 Publicar no GitHub"**

---

## ⚙️ SETUP - Opção 2️⃣ (GitHub Actions)

Para automação **pura no GitHub** (sem Google Sheets).

### Passo 1: Preparar Repositório

1. Clone/crie um repositório para seu blog
2. Crie a pasta `.github/workflows/`
3. Crie a pasta `.github/scripts/`
4. Cole o arquivo `github-workflow.yml` em `.github/workflows/blog-generator.yml`
5. Cole o arquivo `generate_article.py` em `.github/scripts/generate_article.py`

### Passo 2: Adicionar Segredos

No repositório GitHub:

1. Vá em **Settings > Secrets and variables > Actions**
2. Clique em **"New repository secret"**
3. Adicione:
   - Nome: `GEMINI_API_KEY` | Valor: sua chave Gemini
   - Nome: `CLAUDE_API_KEY` | Valor: sua chave Claude (opcional)

### Passo 3: Estrutura do Repositório

```
seu-blog/
├── .github/
│   ├── workflows/
│   │   └── blog-generator.yml      (← Cole aqui)
│   └── scripts/
│       └── generate_article.py     (← Cole aqui)
├── content/
│   └── blog/                       (← Artigos vão aqui)
│       ├── artigo-1.md
│       └── artigo-2.md
└── README.md
```

### Passo 4: Testar

1. Vá na aba **Actions** do seu repositório
2. Clique em **"blog-generator"**
3. Clique em **"Run workflow"** (botão azul)
4. Escolha uma branch
5. Clique em **"Run workflow"**

✅ Ele vai gerar um artigo e criar um commit automaticamente!

---

## 🎮 Como Usar o Painel Dashboard

### Interface Principal

```
┌─────────────────────────────────────────┐
│  🚀 Blog Content AI Generator           │
├─────────────────────────────────────────┤
│                                         │
│  🏢 Dados da Empresa                    │
│  ├─ Nome da Empresa                     │
│  ├─ Website                             │
│  ├─ Localização                         │
│  └─ Descrição + Público-alvo            │
│                                         │
│  🔑 Configuração de APIs                │
│  ├─ Gemini                              │
│  ├─ Claude                              │
│  └─ GitHub                              │
│                                         │
│  📝 Estratégia de Conteúdo              │
│  ├─ Tópicos Principais                  │
│  ├─ Palavras-Chave                      │
│  ├─ Tom de Voz                          │
│  └─ CTA Padrão                          │
│                                         │
│  ⚡ Gerador de Artigos                  │
│  ├─ Selecionar Tópico                   │
│  ├─ Selecionar Palavra-chave            │
│  └─ Gerar com IA → Publicar GitHub      │
│                                         │
└─────────────────────────────────────────┘
```

### Fluxo Típico

1. **Preencher Configuração** (uma única vez)
   - Nome da empresa
   - Chaves de API
   - Tópicos e palavras-chave

2. **Salvar Configurações**
   - Dados são salvos no navegador (localStorage)

3. **Gerar Artigos**
   - Manualmente via painel
   - Ou automático via Google Apps Script

4. **Publicar no GitHub**
   - Clique em "🚀 Publicar"
   - Artigo sobe em segundos

5. **Ver Histórico**
   - Aba "📊 Histórico de Artigos"
   - Todos os artigos gerados

---

## 🎬 Exemplos de Fluxos

### Fluxo 1: Geração Manual (Você controla)

```
Abrir painel → Selecionar tópico + keyword →
Gerar com Gemini → Revisar → Publicar GitHub
```

### Fluxo 2: Automação Completa (Sem interação)

```
Google Apps Script dispara às 9:00 AM →
Seleciona tópico/keyword aleatório →
Chama API Gemini →
Publica no GitHub →
Registra log no Sheet
```

### Fluxo 3: Geração Contínua (GitHub Actions)

```
Agenda GitHub Actions (diário) →
Script Python roda →
Gera artigo →
Cria Pull Request/Commit
```

---

## 🛠️ Personalização

### Mudar Horário de Execução

**Google Apps Script:**
```javascript
ScriptApp.newTrigger('runDailyGeneration')
  .timeBased()
  .atHour(19)  // ← Mude para 19:00 (7 PM)
  .everyDays(1)
  .create();
```

**GitHub Actions:**
```yaml
schedule:
  - cron: '0 19 * * *'  # ← 19:00 UTC
```

### Mudar Frequência

**2 vezes por dia:**
```yaml
schedule:
  - cron: '0 9,19 * * *'  # 9:00 AM e 7:00 PM
```

**Apenas segunda, quarta, sexta:**
```yaml
schedule:
  - cron: '0 9 * * 1,3,5'  # Mon, Wed, Fri
```

### Adicionar Mais Tópicos

No CONFIG:
```javascript
TOPICS: [
  'Como aparecer no Google Maps',
  'SEO local para pequenas empresas',
  // ← Adicione mais aqui
  'Novo tópico aqui',
]
```

### Mudar Rede da IA

No CONFIG:
```javascript
DEFAULT_AI: 'claude'  // mude de 'gemini' para 'claude'
```

---

## 📊 Estrutura de Artigos Gerados

Cada artigo segue este template (baseado no seu framework):

```markdown
# Título SEO (≤60 caracteres)

<!-- meta description: até 155 caracteres -->
<!-- slug: /url-amigavel-do-artigo -->

> **Resumo Rápido**
> ► O que é
> ► Para quem
> ► Como funciona
> ► Próximo passo

## Introdução
...

## Seção 1
### Subsecção 1.1
...

## Conclusão + CTA

## FAQ
1. Pergunta 1?
   Resposta...

<!-- Schema JSON-LD recomendado aqui -->
```

---

## 🐛 Troubleshooting

### Erro: "API Key não configurada"

```
❌ GEMINI_API_KEY não encontrada
```

**Solução:**
1. Vá em https://aistudio.google.com/apikey
2. Gere uma nova chave
3. Cole no painel (ou no CONFIG do GAS)

### Erro: "GitHub publish failed"

```
❌ Erro ao publicar: 401 Unauthorized
```

**Solução:**
1. Verifique se o token é válido
2. Verifique se tem permissão `repo`
3. Verifique se o repositório existe

### Erro: "Content too short"

```
❌ Conteúdo gerado muito curto (< 500 chars)
```

**Solução:**
1. Tente novamente (APIs podem ser lentas)
2. Mude para um modelo maior (claude-opus vs claude-sonnet)
3. Ajuste o prompt para ser mais descritivo

### Artigos duplicados

**Solução:**
- Sistema trata automaticamente adicionando sufixo `-1`, `-2`, etc.

---

## 📈 Monitoramento

### Checar Execução no Google Sheets

1. Vá em **Extensões > Apps Script**
2. Clique em **"Execução"** (lado esquerdo)
3. Veja histórico de execuções
4. Status: ✅ Completado ou ❌ Erro

### Checar Logs

Na aba **"Log de Artigos"** do Sheet:
- Data/Hora
- Título gerado
- Tópico e Palavra-chave
- Status (Publicado/Erro)
- URL no GitHub

### Checar no GitHub

No repositório:
1. Vá em **Commits**
2. Procure por mensagens com "Add article"
3. Clique para ver o artigo publicado

---

## 🚀 Deploy em Produção

### Checklist Final

- [ ] Todas as chaves de API configuradas
- [ ] GitHub repository criado e acessível
- [ ] Google Sheets ID correto no CONFIG
- [ ] Pasta de saída existe no repositório
- [ ] Teste manual funcionando
- [ ] Trigger agendado configurado
- [ ] Logs aparecendo no Sheet

### Otimizações

1. **Cache de Requisições** - Evitar calls repetidas
2. **Rate Limiting** - Respeitar limites de API
3. **Fallback** - Se Gemini falhar, tentar Claude
4. **Validação** - Verificar qualidade antes de publicar

---

## 📚 Referências

- [Google Gemini API](https://aistudio.google.com/apikey)
- [Anthropic Claude API](https://console.anthropic.com/)
- [GitHub API](https://docs.github.com/en/rest)
- [Google Apps Script Docs](https://developers.google.com/apps-script/guides)

---

## 💡 Dicas de Uso

### Para Máximo Impacto

1. **Adicione muitas palavras-chave** - Quanto mais, melhor
2. **Atualize tópicos regularmente** - Siga tendências
3. **Revise alguns artigos** - Nem todos precisam ser automáticos
4. **Monitore rankings** - Veja quais artigos convertem
5. **Ajuste o tom** - Teste diferentes estilos

### Ideias de Conteúdo

Para **Maycon M.**, adicione tópicos como:

```javascript
TOPICS: [
  'Como aparecer no Google Maps em Navegantes',
  'SEO Local: Guia Prático para 2025',
  'Google My Business - Checklist Completo',
  'Local SEO vs SEO Global: Diferenças',
  'Como Gerar Leads com SEO Local',
  'Otimização para IA: O Futuro do SEO',
  'Schema.org e Dados Estruturados',
  'Link Building Local: Estratégias',
  'Content Marketing para Consultores',
  'Análise de Concorrentes em SEO Local'
]
```

---

## ⚖️ Boas Práticas

### SEO

✅ Não republique artigos muito similares  
✅ Use internallinks naturais  
✅ Diversifique palavras-chave  
✅ Mantenha qualidade mínima  

### Ética

✅ Sempre disclose de IA (opcional, mas recomendado)  
✅ Não publique conteúdo inadequado  
✅ Respeite direitos autorais  
✅ Valide informações críticas  

---

## 📞 Suporte

### Se não funcionar:

1. **Verifique logs** - Google Sheets > Extensões > Apps Script > Execução
2. **Teste conexão** - Clique em "🧪 Testar Conexões" no painel
3. **Revise chaves** - Confira se as chaves estão ativas/válidas
4. **Tente GitHub Actions** - Se GAS não funcionar

---

## 🎉 Pronto!

Agora você tem um **gerador de artigos totalmente automático**. 

Próximos passos:
1. ✅ Configure as APIs
2. ✅ Abra o painel dashboard
3. ✅ Preencha dados da empresa
4. ✅ Configure automação
5. ✅ Sente, relaxe e veja artigos sendo gerados! 🚀

**Boa sorte com seu blog!**

---

*Feito com ❤️ para Maycon M. Agência*
