import json
import os
import shutil
import tempfile
import time

import win32print
import win32ui

from services.retry_service import RetryService


class PrinterService:
    SETTINGS_FILE = os.path.join("data", "printer_settings.json")

    def print_pdf_file(self, printer_name: str, file_path: str) -> bool:
        retry_service = RetryService()

        def action():
            import win32api

            print("========== DEBUG PRINT PDF ==========")
            print("Arquivo:", file_path)
            print("Impressora:", printer_name)
            print("=====================================")

            if not printer_name:
                raise Exception("Impressora inválida.")

            if not os.path.exists(file_path):
                raise Exception(f"Arquivo não encontrado: {file_path}")

            if not self.printer_exists(printer_name):
                raise Exception(f"Impressora não encontrada: {printer_name}")

            normalized_file_path = os.path.abspath(file_path)

            print("Tentando impressão via printto...")

            win32api.ShellExecute(
                0,
                "printto",
                normalized_file_path,
                f'"{printer_name}"',
                ".",
                0,
            )

            print("Comando printto enviado.")
            time.sleep(2)

            return True

        try:
            result = retry_service.run(
                action=action,
                action_name="impressão de PDF",
                max_attempts=3,
                delay_seconds=2,
            )

            print("✅ Impressão finalizada com sucesso.")
            return result

        except Exception as error:
            print(f"❌ Falha total ao imprimir PDF: {error}")
            return False

    def print_test_page(self, printer_name: str) -> bool:
        try:
            if not printer_name:
                print("❌ Impressora inválida para teste.")
                return False

            if not self.printer_exists(printer_name):
                print(f"❌ Impressora não encontrada no Windows: {printer_name}")
                return False

            print(f"Imprimindo teste via driver Windows: {printer_name}")

            dc = win32ui.CreateDC()
            dc.CreatePrinterDC(printer_name)

            dc.StartDoc("Teste SOFTWARE ML")
            dc.StartPage()

            dc.TextOut(100, 100, "TESTE SOFTWARE ML")
            dc.TextOut(100, 160, "IMPRESSAO VIA DRIVER WINDOWS")
            dc.TextOut(100, 220, printer_name)

            dc.EndPage()
            dc.EndDoc()
            dc.DeleteDC()

            print(f"✅ Teste enviado para impressora: {printer_name}")
            return True

        except Exception as error:
            print(f"❌ Erro ao imprimir teste: {error}")
            return False

    def list_printers(self) -> list[dict]:
        printers = []

        printer_flags = (
            win32print.PRINTER_ENUM_LOCAL
            | win32print.PRINTER_ENUM_CONNECTIONS
        )

        printer_data = win32print.EnumPrinters(printer_flags)

        default_printer = self.get_windows_default_printer()
        selected_printer = self.get_selected_printer_name()

        for printer in printer_data:
            printer_name = printer[2]

            printers.append(
                {
                    "name": printer_name,
                    "is_windows_default": printer_name == default_printer,
                    "is_selected": printer_name == selected_printer,
                }
            )

        return printers

    def get_windows_default_printer(self) -> str | None:
        try:
            return win32print.GetDefaultPrinter()
        except Exception:
            return None

    def get_selected_printer_name(self) -> str | None:
        if not os.path.exists(self.SETTINGS_FILE):
            return None

        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("selected_printer")
        except Exception:
            return None

    def save_selected_printer(self, printer_name: str) -> bool:
        try:
            os.makedirs("data", exist_ok=True)

            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    {"selected_printer": printer_name},
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            return True

        except Exception as error:
            print(f"❌ Erro ao salvar impressora selecionada: {error}")
            return False

    def printer_exists(self, printer_name: str) -> bool:
        printers = self.list_printers()
        return any(printer["name"] == printer_name for printer in printers)