# API DevOps de Tarefas

API REST desenvolvida em Python com FastAPI, integrada a uma pipeline completa de CI/CD utilizando GitHub Actions, Docker, Amazon ECR e Amazon EC2.

---

## Descricao da aplicacao

A **API DevOps de Tarefas** e uma aplicacao HTTP que permite gerenciar uma lista de tarefas em memoria. O projeto foi desenvolvido como atividade pratica da disciplina de **Integracao DevOps**, com o objetivo de demonstrar o fluxo completo de:

- Versionamento com Git e GitHub
- Integracao continua com testes automatizados (GitHub Actions)
- Containerizacao com Docker
- Publicacao de imagens no Amazon ECR
- Deploy automatico em instancia Amazon EC2

---

## Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python 3.13 | Linguagem principal |
| FastAPI | Framework web da API |
| Uvicorn | Servidor ASGI |
| pytest | Testes automatizados |
| pytest-cov | Cobertura de testes |
| Ruff | Analise estatica e formatacao |
| Docker | Containerizacao |
| GitHub Actions | CI/CD pipeline |
| Amazon ECR | Registro de imagens Docker |
| Amazon EC2 | Hospedagem da aplicacao |

---

## Estrutura do repositorio

```
devops-python-api/
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml          # Pipeline de integracao continua (Pull Requests)
|       +-- deploy.yml      # Pipeline de entrega continua (merge na main)
|
+-- app/
|   +-- __init__.py
|   +-- main.py             # API FastAPI
|
+-- tests/
|   +-- test_app.py         # Testes automatizados
|
+-- docs/
|   +-- API.md
|   +-- DOCKER.md
|   +-- GITHUB-ACTIONS.md
|   +-- ROTEIRO-AULA.md
|
+-- .dockerignore
+-- .gitignore
+-- .python-version
+-- compose.yaml
+-- Dockerfile
+-- pyproject.toml
+-- README.md
+-- requirements.txt
+-- requirements-dev.txt
```

---

## Endpoints da API

| Metodo | Caminho | Descricao | Status |
|---|---|---|---|
| GET | `/` | Apresenta a API | 200 |
| GET | `/health` | Verifica saude e versao | 200 |
| GET | `/tasks` | Lista todas as tarefas | 200 |
| POST | `/tasks` | Cria uma nova tarefa | 201 |
| PATCH | `/tasks/{id}/done` | Conclui uma tarefa | 200 / 404 |

---

## Execucao local

### Pre-requisitos

- Git
- Python 3.13
- Docker (opcional para execucao em container)

### Linux e macOS

```bash
git clone https://github.com/matheus277353/devops-python-api.git
cd devops-python-api

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

### Windows (PowerShell)

```powershell
git clone https://github.com/matheus277353/devops-python-api.git
cd devops-python-api

py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

Acesse:
- API: http://localhost:8000
- Documentacao Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Testando os endpoints

```bash
# Verificar saude da API
curl http://localhost:8000/health

# Criar uma tarefa
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Estudar GitHub Actions"}'

# Listar tarefas
curl http://localhost:8000/tasks

# Concluir tarefa
curl -X PATCH http://localhost:8000/tasks/1/done
```

---

## Execucao com Docker

### Build e execucao manual

```bash
# Construir a imagem
docker build -t devops-python-api:latest .

# Executar o container
docker run --rm -p 8000:8000 --name devops-python-api devops-python-api:latest

# Verificar se esta funcionando
curl http://localhost:8000/health
```

### Com Docker Compose

```bash
docker compose up --build
docker compose down
```

### Verificar container em execucao

```bash
docker ps
docker logs devops-python-api
```

---

## Testes automatizados

```bash
# Executar todos os testes com cobertura
pytest --cov=app --cov-report=term-missing

# Verificar analise estatica
ruff check .

# Verificar formatacao
ruff format --check .
```

Cobertura minima exigida: **90%** (configurado em `pyproject.toml`).

---

## Pipeline de Integracao Continua (CI)

Arquivo: `.github/workflows/ci.yml`

**Aciona:** Abertura ou atualizacao de Pull Request para a branch `main`

**Etapas:**

1. **Obter o codigo** - checkout do repositorio
2. **Preparar Python** - configura Python 3.13 com cache de dependencias
3. **Instalar dependencias** - instala `requirements-dev.txt`
4. **Analise estatica** - executa `ruff check .`
5. **Verificacao de formatacao** - executa `ruff format --check .`
6. **Testes e cobertura** - executa pytest com relatorio de cobertura e JUnit XML
7. **Salvar relatorios** - faz upload dos artefatos de cobertura
8. **Build do container** - constroi a imagem Docker
9. **Smoke test** - inicia o container e verifica o endpoint `/health`

> A etapa de deploy **nao e executada** quando os testes falham.

---

## Pipeline de Entrega Continua (CD)

Arquivo: `.github/workflows/deploy.yml`

**Aciona:** Merge (push) na branch `main`

**Etapas:**

1. **Testes automatizados** - re-executa todos os testes (gate obrigatorio)
2. **Build e push ECR:**
   - Autentica na AWS via GitHub Secrets
   - Faz login no Amazon ECR
   - Constroi a imagem Docker
   - Aplica tag com o SHA do commit e tag `latest`
   - Envia ambas as tags ao ECR
3. **Deploy na EC2:**
   - Conecta via SSH na instancia EC2
   - Autentica no ECR usando a IAM Role da instancia
   - Para e remove o container antigo
   - Baixa a nova imagem do ECR
   - Inicia o novo container com `--restart unless-stopped`
   - Verifica se a API esta respondendo

---

## Arquitetura de implantacao

```
Desenvolvedor
     |
     | git push / Pull Request
     v
+------------------+
|   GitHub         |
|  (repositorio)   |
+--------+---------+
         |
         | Trigger (PR --> CI / merge --> CD)
         v
+------------------+
| GitHub Actions   |
| Runner           |
|                  |
| 1. Testes pytest |
| 2. Build Docker  |
| 3. Push ECR      |
| 4. SSH deploy    |
+--------+---------+
         |                        |
         | push imagem            | SSH deploy
         v                        v
+------------------+    +------------------+
| Amazon ECR       |    | Amazon EC2       |
| (registro        |    | (instancia       |
|  privado)        |    |  Linux + Docker) |
+------------------+    +--------+---------+
                                  |
                                  | porta 8000
                                  v
                         +------------------+
                         | Aplicacao        |
                         | devops-python-api|
                         | (container)      |
                         +------------------+
```

**Fluxo completo:**
`Codigo alterado` -> `Branch` -> `Pull Request` -> `Testes CI` -> `Merge main` -> `Build Docker` -> `Push ECR` -> `Deploy EC2` -> `Aplicacao atualizada`

---

## Configuracao da AWS

### GitHub Secrets necessarios

Configure os seguintes Secrets em **Settings > Secrets and variables > Actions** do repositorio:

| Secret | Descricao |
|---|---|
| `AWS_ACCESS_KEY_ID` | ID da chave de acesso IAM |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta IAM |
| `AWS_ACCOUNT_ID` | ID da conta AWS (12 digitos) |
| `EC2_HOST` | IP publico ou DNS da instancia EC2 |
| `EC2_USER` | Usuario SSH (ex: `ubuntu` ou `ec2-user`) |
| `EC2_SSH_KEY` | Chave privada SSH (.pem) para acesso a EC2 |

> **Importante:** Nenhuma credencial deve ser inserida diretamente no codigo ou nos arquivos de configuracao versionados.

### IAM Role da instancia EC2

A instancia EC2 deve ter uma IAM Role com a policy `AmazonEC2ContainerRegistryReadOnly` para permitir o pull de imagens do ECR sem necessidade de credenciais estaticas no servidor.

### Configuracao da EC2

A instancia EC2 deve ter:
- Sistema operacional Linux (Ubuntu 22.04+ recomendado)
- Docker instalado e em execucao
- Regra de Security Group: porta **8000** liberada (HTTP inbound)
- Regra de Security Group: porta **22** liberada para o runner do GitHub Actions

---

## Verificar versao implantada

```bash
# Via HTTP
curl http://<EC2-PUBLIC-IP>:8000/health

# Resposta esperada:
# {"status": "ok", "version": "1.0.0"}

# Verificar container em execucao na EC2 (via SSH)
ssh -i sua-chave.pem ubuntu@<EC2-PUBLIC-IP>
docker ps
docker logs devops-python-api
```

---

## Evidencias das pipelines

As evidencias de execucao das pipelines estao disponiveis na aba **Actions** do repositorio GitHub:

- **CI Pipeline:** execucao a cada Pull Request para `main`
- **CD Pipeline:** execucao a cada merge na `main`

Cada execucao registra:
- Resultado dos testes automatizados
- Relatorios de cobertura de codigo (artefatos)
- Log completo do build e push Docker
- Log do deploy na EC2

---

## Fluxo de desenvolvimento

```
1. git checkout -b feature/minha-funcionalidade
2. # Implementar alteracoes
3. git add . && git commit -m "feat: descricao clara da alteracao"
4. git push origin feature/minha-funcionalidade
5. # Abrir Pull Request no GitHub (CI aciona automaticamente)
6. # Aguardar aprovacao dos testes
7. # Merge na main (CD aciona automaticamente o deploy)
8. # Verificar aplicacao atualizada na EC2
```

---

## Referencias

- [GitHub Actions - Python](https://docs.github.com/pt/actions/tutorials/build-and-test-code/building-and-testing-python)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Amazon ECR](https://docs.aws.amazon.com/ecr/)
- [Docker para Python](https://docs.docker.com/language/python/)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
- [aws-actions/amazon-ecr-login](https://github.com/aws-actions/amazon-ecr-login)
- [appleboy/ssh-action](https://github.com/appleboy/ssh-action)
