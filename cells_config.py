import json
import logging
from typing import List, Dict, Any
from config import Config

class CellConfig:
    def __init__(self, spreadsheet_id: str, worksheet_name: str, cell_id: str, display_name: str):
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name
        self.cell_id = cell_id
        self.display_name = display_name
    
    def __repr__(self):
        return f"CellConfig({self.display_name}: {self.spreadsheet_id}/{self.worksheet_name}!{self.cell_id})"

def load_cells_config() -> List[CellConfig]:
    """Load cell configurations from JSON file."""
    try:
        with open(Config.CELLS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cells = []
        for cell_data in data.get('cells', []):
            cell = CellConfig(
                spreadsheet_id=cell_data['spreadsheet_id'],
                worksheet_name=cell_data['worksheet_name'],
                cell_id=cell_data['cell_id'],
                display_name=cell_data['display_name']
            )
            cells.append(cell)
        
        logging.info(f"Loaded {len(cells)} cell configurations")
        return cells
        
    except FileNotFoundError:
        logging.error(f"Cells config file not found: {Config.CELLS_CONFIG_FILE}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in cells config file: {e}")
        raise
    except KeyError as e:
        logging.error(f"Missing required field in cells config: {e}")
        raise
    except Exception as e:
        logging.error(f"Error loading cells config: {e}")
        raise
