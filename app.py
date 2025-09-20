import signal
import sys
import time
import logging
from typing import Optional, Dict, List

from config import Config
from google_sheets import SheetsClient
from telegram_notifier import send_message
from storage import load_state, save_state
from cells_config import load_cells_config, CellConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

_RUNNING = True

def _handle_signal(signum, frame):
    global _RUNNING
    logging.info("Received signal %s; shutting down...", signum)
    _RUNNING = False

signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

def main():
    Config.validate()

    # Load cell configurations
    cell_configs = load_cells_config()
    logging.info("Starting Sheet watch for %d cells, interval=%ss", 
                 len(cell_configs), Config.POLL_INTERVAL_SECONDS)

    sheets = SheetsClient()
    state = load_state(Config.STATE_FILE)
    last_values: Dict[str, str] = state.get("last_values", {})

    # First read - check all cells
    current_values = {}
    for cell_config in cell_configs:
        try:
            value = sheets.read_cell(cell_config)
            current_values[cell_config.display_name] = value
            logging.info("Cell %s (%s): %r", cell_config.display_name, cell_config.cell_id, value)
        except Exception as e:
            logging.exception("Initial read failed for %s: %s", cell_config.display_name, e)
            current_values[cell_config.display_name] = None

    # Check for changes and update state
    changes_detected = False
    for cell_config in cell_configs:
        display_name = cell_config.display_name
        current_value = current_values.get(display_name)
        last_value = last_values.get(display_name)
        
        if current_value is not None:
            if last_value is None:
                logging.info("Seeding state for %s: %r", display_name, current_value)
                last_values[display_name] = current_value
            else:
                if current_value != last_value:
                    logging.info("Change detected in %s: %r -> %r", display_name, last_value, current_value)
                    _notify_change(cell_config, last_value, current_value)
                    last_values[display_name] = current_value
                    changes_detected = True

    if changes_detected or not last_values:
        save_state(Config.STATE_FILE, {"last_values": last_values})

    # Poll loop
    backoff = 1
    while _RUNNING:
        start = time.time()
        changes_detected = False
        
        try:
            for cell_config in cell_configs:
                try:
                    value = sheets.read_cell(cell_config)
                    last_value = last_values.get(cell_config.display_name)
                    
                    if value != last_value:
                        logging.info("Change detected in %s: %r -> %r", 
                                   cell_config.display_name, last_value, value)
                        _notify_change(cell_config, last_value, value)
                        last_values[cell_config.display_name] = value
                        changes_detected = True
                        
                except Exception as e:
                    logging.exception("Error reading cell %s: %s", cell_config.display_name, e)
            
            if changes_detected:
                save_state(Config.STATE_FILE, {"last_values": last_values})
            
            backoff = 1  # reset on success
            
        except Exception as e:
            logging.exception("Poll error: %s", e)
            # Exponential backoff up to 5 minutes
            backoff = min(backoff * 2, 300)

        elapsed = time.time() - start
        sleep_for = max(Config.POLL_INTERVAL_SECONDS if backoff == 1 else backoff, 1)
        # Ensure we don't spin too fast if POLL_INTERVAL_SECONDS < API latency
        if sleep_for > 0 and _RUNNING:
            # Use interruptible sleep - sleep in small chunks and check _RUNNING
            sleep_remaining = sleep_for
            while sleep_remaining > 0 and _RUNNING:
                chunk = min(sleep_remaining, 1.0)  # Sleep in 1-second chunks
                time.sleep(chunk)
                sleep_remaining -= chunk

    logging.info("Exited cleanly.")

def _notify_change(cell_config: CellConfig, prev: Optional[str], curr: Optional[str]) -> None:
    pv = "(empty)" if prev in (None, "") else f"{prev}"
    cv = "(empty)" if curr in (None, "") else f"{curr}"
    message = (
         f"{cell_config.display_name}: {pv} -> *{cv}*"
    )
    logging.info("Change detected in %s: %r -> %r. Notifying Telegram...", 
                cell_config.display_name, prev, curr)
    send_message(message, parse_mode="Markdown")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("Fatal error")
        sys.exit(1)
