from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES: List[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
]
RECIFE_TZ = ZoneInfo("America/Recife")
SPREADSHEET_TIMEZONE = "America/Recife"
SPREADSHEET_LOCALE = "pt_BR"

BISTROL_OPTIONS = {
    "1. duro e separado": 1,
    "2. alongado com caroço": 2,
    "3. alongado e firme": 3,
    "4. alongado e mole": 4,
    "5. bola mole": 5,
    "6. pedaços macios e irregulares": 6,
    "7. diarreia liquida": 7,
}


def get_sheets_service():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=creds)


def ensure_spreadsheet_settings(sheet_id: str) -> None:
    service = get_sheets_service()
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={
            "requests": [
                {
                    "updateSpreadsheetProperties": {
                        "properties": {
                            "timeZone": SPREADSHEET_TIMEZONE,
                            "locale": SPREADSHEET_LOCALE,
                        },
                        "fields": "timeZone,locale",
                    }
                }
            ]
        },
    ).execute()


def append_row(sheet_id: str, day: str, hour: str, stool_type: int) -> None:
    service = get_sheets_service()
    body = {"values": [[day, hour, stool_type]]}
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Registros!A:C",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()


def main() -> None:
    st.set_page_config(page_title="Registro de Fezes do Pet", page_icon="🐾", layout="centered")
    st.title("Registro diário de fezes do pet")
    st.caption("Cada envio grava uma nova linha na planilha do Google Drive.")

    if "sheet_id" not in st.secrets:
        st.error("Defina `sheet_id` em `.streamlit/secrets.toml`.")
        st.stop()

    if "spreadsheet_settings_checked" not in st.session_state:
        try:
            ensure_spreadsheet_settings(st.secrets["sheet_id"])
            st.session_state["spreadsheet_settings_checked"] = True
        except Exception as exc:
            st.warning(
                "Nao foi possivel confirmar timezone/locale da planilha agora. "
                f"Detalhe: {exc}"
            )

    now = datetime.now(RECIFE_TZ)

    with st.form("registro_form"):
        day = st.date_input("Dia", value=now.date(), format="DD/MM/YYYY")
        hour = st.time_input("Hora", value=now.time().replace(second=0, microsecond=0))
        option_label = st.selectbox("Tipo (escala Bistrol)", list(BISTROL_OPTIONS.keys()))
        submitted = st.form_submit_button("Salvar registro")

    if submitted:
        day_str = day.strftime("%Y-%m-%d")
        hour_str = hour.strftime("%H:%M")
        type_value = BISTROL_OPTIONS[option_label]

        try:
            append_row(st.secrets["sheet_id"], day_str, hour_str, type_value)
            st.success("Registro salvo com sucesso.")
        except Exception as exc:
            st.error(f"Erro ao salvar registro: {exc}")


if __name__ == "__main__":
    main()
