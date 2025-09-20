import gspread
from google.oauth2.service_account import Credentials
from config import Config
from cells_config import CellConfig
from typing import Dict, Optional

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

class SheetsClient:
    def __init__(self):
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_APPLICATION_CREDENTIALS,
            scopes=_SCOPES
        )
        self.gc = gspread.authorize(creds)
        self._worksheet_cache: Dict[str, gspread.Worksheet] = {}

    def _get_worksheet(self, spreadsheet_id: str, worksheet_name: str) -> gspread.Worksheet:
        """Get worksheet with caching."""
        cache_key = f"{spreadsheet_id}:{worksheet_name}"
        
        if cache_key not in self._worksheet_cache:
            sh = self.gc.open_by_key(spreadsheet_id)
            self._worksheet_cache[cache_key] = sh.worksheet(worksheet_name)
        
        return self._worksheet_cache[cache_key]

    def read_cell(self, cell_config: CellConfig) -> str:
        """Read a specific cell using cell configuration."""
        ws = self._get_worksheet(cell_config.spreadsheet_id, cell_config.worksheet_name)
        val = ws.acell(cell_config.cell_id, value_render_option="FORMATTED_VALUE").value
        # Normalize to string so comparisons are consistent
        return "" if val is None else str(val)
