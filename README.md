# Chatbot de Dúvidas Técnicas para Equipamentos de Segurança Eletrônica Hikvision

## 1. Sobre o projeto

Este projeto consiste no desenvolvimento de um chatbot de suporte técnico especializado em equipamentos Hikvision.

O objetivo é fornecer respostas a dúvidas técnicas frequentes, auxiliando os usuários na identificação de problemas e na consulta de orientações relacionadas aos equipamentos.

O chatbot utiliza técnicas de Processamento de Linguagem Natural (PLN) para interpretar perguntas e recuperar respostas a partir de uma base de conhecimento própria.

## 2. Objetivos

- Automatizar respostas para dúvidas técnicas frequentes.
- Facilitar o acesso a informações sobre equipamentos Hikvision.
- Reduzir o tempo necessário para encontrar soluções para problemas comuns.
- Utilizar técnicas próprias de PLN, sem depender de serviços pagos de inteligência artificial.
- Evitar respostas inadequadas por meio de um mecanismo de fallback.

## 3. Escopo do chatbot

O sistema trabalha com três categorias principais de dúvidas:

| Intenção | Descrição |
|---|---|
| `configuracao` | Configuração e instalação dos equipamentos. |
| `erros` | Identificação de erros, falhas e problemas de funcionamento. |
| `senhas` | Segurança e procedimentos relacionados a senhas e recuperação de acesso. |

### Fora do escopo

O chatbot não tem como objetivo responder sobre:

- Comparações entre fabricantes concorrentes.
- Orçamentos e preços de equipamentos.
- Reparos físicos e manutenção de componentes.

Perguntas fora do escopo devem receber uma resposta de fallback, informando que o sistema não possui conhecimento suficiente para responder.

## 4. Tecnologias utilizadas

- **Python:** linguagem principal do projeto.
- **Scikit-learn:** implementação da vetorização TF-IDF e cálculo de similaridade.
- **TF-IDF:** representação numérica das perguntas.
- **Similaridade do cosseno:** comparação entre a pergunta do usuário e as perguntas cadastradas.
- **Streamlit:** interface de interação com o chatbot.
- **Pandas e NumPy:** apoio ao processamento e à análise dos dados.

## 5. Arquitetura e funcionamento

O projeto utiliza uma abordagem de recuperação de informações baseada em TF-IDF e similaridade do cosseno.

O funcionamento previsto é:

1. O usuário envia uma pergunta.
2. O sistema realiza o pré-processamento do texto.
3. A pergunta é transformada em uma representação vetorial usando TF-IDF.
4. O sistema compara a pergunta com os registros da base de conhecimento.
5. A similaridade do cosseno identifica a pergunta mais próxima.
6. O sistema verifica se a pontuação atingiu o limite mínimo de confiança.
7. Se atingir o limite, retorna a resposta correspondente.
8. Caso contrário, apresenta uma mensagem de fallback.

**Importante:** o limite de confiança deve ser definido e padronizado pela equipe, conforme os critérios da especificação e os resultados dos testes.

## 6. Estrutura do projeto

```text
A3-CHATBOT-IT/
│
├── data/
│   ├── base_conhecimento.json
│   └── test_cases.csv
│
├── src/
│   ├── __init__.py
│   ├── preprocessor.py
│   ├── retriever.py
│   ├── engine.py
│   └── metrics.py
│
├── .venv/
│
├── app.py
├── validar_base.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Responsabilidade dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `base_conhecimento.json` | Armazenar perguntas, intenções e respostas. |
| `test_cases.csv` | Armazenar os casos utilizados na avaliação. |
| `preprocessor.py` | Realizar o pré-processamento das perguntas. |
| `retriever.py` | Executar a busca utilizando TF-IDF e similaridade do cosseno. |
| `engine.py` | Controlar a resposta e o mecanismo de fallback. |
| `metrics.py` | Calcular as métricas de avaliação. |
| `app.py` | Disponibilizar a interface do chatbot. |
| `validar_base.py` | Verificar a estrutura e consistência da base de conhecimento. |
| `requirements.txt` | Registrar as dependências do projeto. |

## 7. Instalação e configuração

### Pré-requisitos

- Python 3.14 ou versão compatível.
- Git instalado.
- Visual Studio Code ou outro editor de código.

### Clonar o repositório

```bash
git clone https://github.com/LucasRobertodaRosa/A3-CHATBOT-IT.git
cd A3-CHATBOT-IT
```

### Criar o ambiente virtual

```powershell
python -m venv .venv
```

### Ativar o ambiente virtual

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso a execução de scripts esteja bloqueada, é possível
utilizar diretamente o Python do ambiente virtual, sem ativá-lo.

### Instalar as dependências

Com o ambiente virtual ativado:

```powershell
python -m pip install -r requirements.txt
```

Sem ativar o ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Verificar as dependências

```powershell
.\.venv\Scripts\python.exe -m pip check
```

A instalação foi validada em ambiente Windows com Python 3.14.10.

## 8. Validação da base de conhecimento

Para verificar a estrutura e a consistência dos registros cadastrados, execute:

```bash
python validar_base.py
```

O validador verifica os campos obrigatórios, a identificação dos registros, as intenções permitidas e o preenchimento das informações.

## 9. Execução do chatbot

Após a implementação dos módulos e da interface, execute:

```bash
streamlit run app.py
```

A interface será disponibilizada localmente pelo Streamlit.


## 10. Avaliação do sistema

A avaliação do chatbot utiliza 20 casos de teste armazenados
no arquivo `data/test_cases.csv`.

### Distribuição dos testes

- 10 perguntas diretas.
- 4 perguntas reformuladas.
- 3 perguntas ambíguas.
- 3 perguntas fora do escopo.

### Executar os testes

A partir da pasta raiz do projeto, execute:

```powershell
.\.venv\Scripts\python.exe -m src.metrics
```

O programa envia cada pergunta ao chatbot e compara a intenção
ou o comportamento de fallback com o resultado esperado.

### Métricas calculadas

- **Acurácia:** percentual de testes classificados corretamente.
- **Acertos:** quantidade de resultados iguais aos esperados.
- **Erros:** quantidade de resultados diferentes dos esperados.
- **Falsos positivos:** casos em que o chatbot respondeu quando
  deveria utilizar fallback.
- **Falsos negativos:** casos em que o chatbot utilizou fallback
  quando deveria responder.
- **Abstenções:** quantidade de vezes que o chatbot utilizou fallback.
- **Taxa de abstenção:** percentual de testes com fallback.

Os falsos positivos e negativos são definidos em relação à
decisão de responder ou utilizar fallback, não à classificação
multiclasse das intenções.

### Resultados da avaliação inicial

| Métrica | Resultado |
|---|---:|
| Total de testes | 20 |
| Acertos | 14 |
| Erros | 6 |
| Acurácia | 70,00% |
| Falsos positivos | 3 |
| Falsos negativos | 1 |
| Abstenções | 4 |
| Taxa de abstenção | 20,00% |

### Análise dos resultados

O chatbot apresentou 70% de acurácia na avaliação inicial.

Foram identificados seis casos com resultados diferentes
dos esperados:

- Testes 7 e 11: classificação de intenção incorreta.
- Teste 13: fallback utilizado quando era esperada uma resposta.
- Testes 15, 16 e 17: respostas produzidas para perguntas
  consideradas ambíguas na massa de testes.

Os resultados demonstram que o mecanismo de recuperação
consegue identificar diversas perguntas da base de conhecimento,
mas ainda apresenta limitações na interpretação de perguntas
reformuladas e ambíguas.

O limiar de confiança utilizado na avaliação foi de 0.40.

Os resultados representam uma avaliação inicial com uma massa
limitada de 20 casos e não devem ser interpretados como uma
medida definitiva de desempenho do sistema.

## 11. Organização e versionamento

O desenvolvimento é organizado por meio de branches no Git, permitindo que cada integrante trabalhe em suas responsabilidades sem modificar diretamente a branch principal.

As alterações devem ser registradas por commits e integradas à branch principal por meio de Pull Requests, conforme o fluxo definido pela equipe.

## 12. Status do projeto

Projeto acadêmico em desenvolvimento, com implementação modular e divisão de responsabilidades entre os integrantes da equipe.