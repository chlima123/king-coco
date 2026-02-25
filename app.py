import argparse
import re
from typing import Dict, List

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES: List[str] = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]
SPREADSHEET_TIMEZONE = "America/Recife"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cria uma planilha de registros na pasta do Google Drive e adiciona cabeçalhos."
    )
    parser.add_argument("--folder-id", required=True, help="ID da pasta no Google Drive")
    parser.add_argument(
        "--title",
        default="Registros Fezes Pet",
        help="Titulo da planilha",
    )
    parser.add_argument(
        "--credentials",
        default="service-account.json",
        help="Caminho para o JSON da service account",
    )
    return parser.parse_args()


def extract_folder_id(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{20,}", value):
        return value
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", value)
    if match:
        return match.group(1)
    raise ValueError("Nao foi possivel extrair o ID da pasta do Drive.")


def create_services(credentials_path: str):
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds)
    sheets = build("sheets", "v4", credentials=creds)
    return drive, sheets


def create_sheet_in_folder(drive, folder_id: str, title: str) -> Dict:
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [folder_id],
    }
    return (
        drive.files()
        .create(body=metadata, fields="id, name, webViewLink")
        .execute()
    )


def init_headers(sheets, spreadsheet_id: str) -> None:
    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="A1:C1",
        valueInputOption="RAW",
        body={"values": [["dia", "hora", "tipo"]]},
    ).execute()

    requests = [
        {
            "updateSpreadsheetProperties": {
                "properties": {
                    "timeZone": SPREADSHEET_TIMEZONE,
                    "locale": "pt_BR",
                },
                "fields": "timeZone,locale",
            }
        },
        {
            "addSheet": {
                "properties": {
                    "title": "Registros",
                }
            }
        }
    ]
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests},
    ).execute()

    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Registros!A1:C1",
        valueInputOption="RAW",
        body={"values": [["dia", "hora", "tipo"]]},
    ).execute()


def main() -> None:
    args = parse_args()
    folder_id = extract_folder_id(args.folder_id)
    drive, sheets = create_services(args.credentials)

    created = create_sheet_in_folder(drive, folder_id, args.title)
    init_headers(sheets, created["id"])

    print("Planilha criada com sucesso")
    print(f"Nome: {created['name']}")
    print(f"Sheet ID: {created['id']}")
    print(f"Link: {created['webViewLink']}")


if __name__ == "__main__":
    main()
