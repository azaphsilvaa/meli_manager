import json
import os

import win32print


class PrinterService:
    SETTINGS_FILE = os.path.join("data", "printer_settings.json")
    
    def print_pdf_file(self, printer_name: str, file_path: str):

        try:
            import win32api

            print(f"Enviando PDF para impressão: {file_path}")
            print(f"Impressora: {printer_name}")

            win32api.ShellExecute(
                0,
                "print",
                file_path,
                None,
                ".",
                0,
            )

            print("Comando de impressão enviado.")

        except Exception as error:
            print(f"Erro ao imprimir PDF: {error}")
    
    def print_test_page(self, printer_name: str):

        try:
            handle = win32print.OpenPrinter(printer_name)

            try:
                win32print.StartDocPrinter(
                    handle,
                    1,
                    ("Teste SOFTWARE ML", None, "RAW"),
                )

                win32print.StartPagePrinter(handle)

                content = (
                    "=================================\n"
                    "     TESTE SOFTWARE ML\n"
                    "=================================\n\n"
                    "Se você está vendo isso,\n"
                    "a impressão está funcionando.\n\n"
                    "Proxy Azaph 🚀\n"
                )

                win32print.WritePrinter(
                    handle,
                    content.encode("utf-8"),
                )

                win32print.EndPagePrinter(handle)
                win32print.EndDocPrinter(handle)

                print(f"Teste enviado para impressora: {printer_name}")

            finally:
                win32print.ClosePrinter(handle)

        except Exception as error:
            print(f"Erro ao imprimir teste: {error}")

    def list_printers(self) -> list[dict]:
        printers = []

        printer_flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
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
            print(f"Erro ao salvar impressora selecionada: {error}")
            return False

    def printer_exists(self, printer_name: str) -> bool:
        printers = self.list_printers()
        return any(printer["name"] == printer_name for printer in printers)