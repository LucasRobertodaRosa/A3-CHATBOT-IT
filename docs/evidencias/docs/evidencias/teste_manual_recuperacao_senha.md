# Teste manual complementar — Recuperação de senha de DVR

**Projeto:** Chatbot de Dúvidas Técnicas para Equipamentos de Segurança Eletrônica  
**Natureza:** protótipo acadêmico independente; não oficial e não homologado por fabricantes  
**Data do teste:** 26/11/2026  
**Ambiente:** interface Streamlit do projeto A3-CHATBOT-IT  
**Responsável pela execução:** [PREENCHER NOME DO INTEGRANTE]  
**Objetivo:** examinar adequação da resposta sobre recuperação de senha e continuidade conversacional.

## 1. Metodologia

O teste foi realizado manualmente na interface do chatbot. Primeiro, apresentou-se uma pergunta sobre redefinição de senha de DVR; em seguida, uma frase de continuação dependente do contexto anterior. Por fim, foi submetida uma pergunta independente, com todas as informações relevantes incluídas no próprio texto. Foram registrados o conteúdo retornado, a categoria e a similaridade exibidas na interface.

**Importante:** este ensaio é **adicional** aos 20 casos de `data/test_cases.csv`. Não deve ser incorporado ao cálculo original de 70% de acurácia sem uma nova rodada de avaliação formal. A similaridade exibida é uma medida lexical do TF-IDF, não uma probabilidade de correção técnica.

## 2. Evidências e resultados

### Interação 1 — Pedido inicial

**Pergunta digitada:** “como redefinir a senha do meu dvr”  
**Resposta obtida:** “Acesse o gerenciamento do dispositivo com uma conta autorizada e procure as opções de usuários ou segurança. Defina uma senha forte, exclusiva e armazenada com segurança. Os nomes dos menus podem variar conforme o modelo e a versão do firmware.”  
**Categoria indicada:** `senhas`  
**Similaridade exibida:** 47%  
**Avaliação qualitativa:** **INADEQUADA para o cenário de senha esquecida**, embora relacionada ao tema. Orienta a alterar a senha após login, sem resolver a impossibilidade de acesso administrativo.

### Interação 2 — Mensagem de continuidade

**Pergunta digitada:** “mas nao tenho acesso a essa pagina sem a senha”  
**Resposta obtida:** “Não encontrei uma resposta confiável para essa pergunta na base de conhecimento. Para evitar uma orientação incorreta, recomendo encaminhar sua dúvida ao suporte técnico humano.”  
**Categoria:** fallback (fora do escopo, conforme a implementação e o contexto da consulta)  
**Pontuação exibida:** 0%  
**Avaliação qualitativa:** **LIMITADA QUANTO À CONTINUIDADE**, mas prudente quanto à ausência de resposta segura. A nova frase não explicitou o equipamento; a Engine analisa a pergunta isoladamente, sem aproveitar o histórico de exibição do Streamlit. O 0% sinaliza que a consulta foi rejeitada antes da busca vetorial, e não uma medição semântica nula.

### Interação 3 — Pergunta completa e autossuficiente

**Pergunta digitada:** “Esqueci a senha de administrador do meu DVR Hikvision e não consigo entrar no menu de configurações. Como posso recuperar o acesso pelo procedimento oficial sem estar logado?”  
**Resposta obtida:** “Utilize o procedimento oficial de recuperação de senha indicado para o modelo e a região do equipamento. Poderá ser necessário comprovar autorização para administrar o dispositivo. Não compartilhe senhas, códigos de verificação ou arquivos de recuperação com pessoas não autorizadas.”  
**Categoria indicada:** `senhas`  
**Similaridade exibida:** 53%  
**Avaliação qualitativa:** **ADEQUADA COMO ORIENTAÇÃO INICIAL**, embora genérica. A resposta distingue recuperação de acesso de alteração de senha com login, condiciona o procedimento ao equipamento e evita aconselhamento inseguro.

### Capturas de tela

- [Interações 1 e 2](capturas/recuperacao_senha_interacoes_1_2.png)
- [Interação 3](capturas/recuperacao_senha_pergunta_completa.png)

## 3. Conclusão do ensaio

O chatbot apresentou uma resposta inicial insuficiente para o caso de senha esquecida, rejeitou prudentemente uma mensagem de continuação sem contexto explícito e respondeu adequadamente quando a pergunta foi formulada de forma completa. Esse padrão é compatível com a arquitetura vigente, em que o Streamlit mantém um histórico para apresentação, mas a função `processar_pergunta()` recebe apenas a mensagem atual.

## 4. Melhoria futura proposta

Implementar memória contextual limitada, que mantenha informações explícitas da sessão (equipamento, problema, restrições relevantes) para completar perguntas subsequentes. A mudança deve preservar filtros de escopo, regra de confiança e fallback, além de ser avaliada com testes específicos de conversas com duas ou mais mensagens. **Essa funcionalidade não está implementada na versão analisada.**

## 5. Relação com os entregáveis acadêmicos

Este registro complementa as seções **6.3 — Teste manual complementar de continuidade conversacional** e **7 — Discussão e limitações** do relatório técnico. É evidência qualitativa suplementar e não substitui os 20 testes nem modifica as métricas publicadas: **14 acertos em 20 casos (70%)**.
