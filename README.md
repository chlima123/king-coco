# Registro diario de fezes do pet (Streamlit)

Formulario web para registrar evacuacoes do pet usando a escala Bistrol.
Cada envio grava uma linha com `dia`, `hora` e `tipo` em uma planilha Google dentro da pasta do Drive.

## Arquivos

- `app.py`: app Streamlit com formulario de registro
- `setup_sheet.py`: cria a planilha na pasta do Drive e inicia os cabecalhos
- `requirements.txt`: dependencias do projeto
- `.streamlit/secrets.example.toml`: modelo de secrets para rodar local e no Streamlit Cloud
- `registros_template.csv`: modelo de tabela com colunas `dia,hora,tipo`

## 1) Preparar Google Drive/Sheets

1. Crie (ou use) um projeto no Google Cloud.
2. Ative as APIs:
   - Google Drive API
   - Google Sheets API
3. Crie uma **Service Account** e baixe o JSON de credenciais.
4. Compartilhe a pasta do Drive com o e-mail da service account (permissao de Editor).
   - Pasta alvo: `https://drive.google.com/drive/folders/1uQNz05W73BGl8yFM16dz4UnHLaCR_pcS`
5. Rode o script para criar a planilha dentro da pasta:

```bash
python setup_sheet.py --folder-id "https://drive.google.com/drive/folders/1uQNz05W73BGl8yFM16dz4UnHLaCR_pcS?usp=sharing" --credentials service-account.json
```

O comando imprime `Sheet ID` e `Link` da planilha criada.

## 2) Configurar secrets

Crie `.streamlit/secrets.toml` baseado em `.streamlit/secrets.example.toml` e preencha:

- `sheet_id`: ID retornado pelo script
- `[gcp_service_account]`: conteudo completo da service account

## 3) Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 4) Publicar no GitHub

```bash
git init
git add .
git commit -m "feat: app de registro diario de fezes do pet"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git
git push -u origin main
```

## 5) Publicar no Streamlit Cloud

1. Acesse: https://share.streamlit.io
2. Clique em **New app**.
3. Selecione o repositorio e o arquivo `app.py`.
4. Em **Advanced settings > Secrets**, cole o conteudo do `secrets.toml`.
5. Deploy.

## Escala Bistrol usada

- 1. duro e separado
- 2. alongado com caroco
- 3. alongado e firme
- 4. alongado e mole
- 5. bola mole
- 6. pedacos macios e irregulares
- 7. diarreia liquida
