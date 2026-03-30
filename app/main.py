import sqlite3
import sys
import threading
import webbrowser

from services.meli_label_service import MercadoLivreLabelService
from services.printer_service import PrinterService
from services.operation_log_service import OperationLogService
from services.label_print_control_service import LabelPrintControlService
from services.live_monitor_service import LiveMonitorService
from services.label_file_service import LabelFileService

processed_shipments = set()

from PySide6.QtCore import QTimer
from services.account_service import AccountService
from services.meli_order_service import MercadoLivreOrderService
from PySide6.QtWidgets import QApplication
from services.shipment_service import ShipmentService

from api.webhook_server import AppWebhookServer
from config.settings import settings
from core.database import Base, engine
from services.meli_auth_service import MercadoLivreAuthService
from services.order_service import OrderService
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen


oauth_running = False
window_instance = None
webhook_server = None

def test_download_label():
    from services.account_service import AccountService
    from services.shipment_service import ShipmentService
    from services.meli_label_service import MercadoLivreLabelService

    account_service = AccountService()
    shipment_service = ShipmentService()
    label_service = MercadoLivreLabelService()

    accounts = account_service.list_accounts()
    shipments = shipment_service.list_shipments()

    if not accounts:
        print("Nenhuma conta.")
        return

    if not shipments:
        print("Nenhum shipment.")
        return

    account = accounts[0]

    real_shipments = [
        shipment
        for shipment in shipments
        if str(shipment.ml_shipment_id).isdigit()
    ]

    if not real_shipments:
        print("Nenhum shipment REAL encontrado.")
        return

    printable_shipments = [
        shipment
        for shipment in real_shipments
        if shipment.shipping_status == "ready_to_ship"
    ]

    if not printable_shipments:
        print("Nenhum shipment imprimível encontrado no banco.")
        print("Shipments encontrados:")
        for shipment in real_shipments[:10]:
            print(
                "SHIPMENT:",
                shipment.ml_shipment_id,
                "| STATUS:",
                shipment.shipping_status,
                "| SUBSTATUS:",
                shipment.shipping_substatus,
            )
        return

    shipment = printable_shipments[0]

    print("TESTANDO DOWNLOAD ETIQUETA")
    print("SHIPMENT REAL:", shipment.ml_shipment_id)
    print("STATUS:", shipment.shipping_status)
    print("SUBSTATUS:", shipment.shipping_substatus)

    label_service.download_label(
        access_token=account.access_token,
        shipment_id=shipment.ml_shipment_id,
    )

def test_connected_account_identity():
    account_service = AccountService()
    auth_service = MercadoLivreAuthService()
    order_service = MercadoLivreOrderService()

    accounts = account_service.list_accounts()

    print("\n=== TESTE DE IDENTIDADE DA CONTA ===")

    if not accounts:
        print("Nenhuma conta encontrada no banco.")
        return

    print(f"TOTAL DE CONTAS NO BANCO: {len(accounts)}")

    for index, account in enumerate(accounts, start=1):
        print(f"\n--- CONTA {index} ---")
        print("ID INTERNO:", account.id)
        print("USER_ID SALVO:", account.user_id)
        print("NICKNAME SALVO:", account.nickname)
        print("CUSTOM_NAME:", account.custom_name)
        print("ACCOUNT_LABEL:", account.account_label)
        print("E-MAIL SALVO:", account.seller_email)
        print("ATIVA:", account.is_active)
        print("PADRÃO:", account.is_default)

        try:
            profile = auth_service.get_current_user_profile(account.access_token)

            print("\n[USERS/ME PELO TOKEN]")
            print("ID REAL DO TOKEN:", profile.get("id"))
            print("NICKNAME REAL DO TOKEN:", profile.get("nickname"))
            print("E-MAIL REAL DO TOKEN:", profile.get("email"))

            seller_id = str(profile.get("id"))

            result = order_service.search_orders_by_seller(
                access_token=account.access_token,
                seller_id=seller_id,
            )

            if not result:
                print("\n[ORDERS/SEARCH]")
                print("Não foi possível buscar pedidos dessa conta.")
                continue

            results = result.get("results", [])

            print(f"\n[ORDERS/SEARCH] TOTAL RETORNADO: {len(results)}")

            for order in results[:5]:
                print(
                    "ORDER_ID:",
                    order.get("id"),
                    "| STATUS:",
                    order.get("status"),
                    "| TOTAL:",
                    order.get("total_amount"),
                )

        except Exception as error:
            print("\n[ERRO AO VALIDAR TOKEN/CONTA]")
            print(str(error))

def test_shipment_base():
    shipment_service = ShipmentService()

    shipment = shipment_service.create_test_shipment()

    print("SHIPMENT TESTE CRIADO:")
    print("SHIPMENT_ID:", shipment.ml_shipment_id)
    print("STATUS:", shipment.shipping_status)
    print("SUBSTATUS:", shipment.shipping_substatus)

def test_list_real_orders():
    account_service = AccountService()
    meli_order_service = MercadoLivreOrderService()

    accounts = account_service.list_accounts()

    if not accounts:
        print("Nenhuma conta conectada para testar pedidos reais.")
        return

    account = accounts[0]

    print("TESTANDO PEDIDOS REAIS DA CONTA:")
    print("USER_ID:", account.user_id)
    print("NICKNAME:", account.nickname)

    result = meli_order_service.search_orders_by_seller(
        access_token=account.access_token,
        seller_id=account.user_id,
    )

    if not result:
        print("Não foi possível listar pedidos reais.")
        return

    results = result.get("results", [])

    print(f"TOTAL RETORNADO: {len(results)}")

    for order in results[:5]:
        print("ORDER_ID:", order.get("id"))


def initialize_database():
    Base.metadata.create_all(bind=engine)
    ensure_account_table_columns()


def ensure_account_table_columns():
    connection = sqlite3.connect(settings.DB_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(mercado_livre_accounts)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        if "custom_name" not in existing_columns:
            cursor.execute(
                "ALTER TABLE mercado_livre_accounts ADD COLUMN custom_name VARCHAR(180)"
            )

        if "description" not in existing_columns:
            cursor.execute(
                "ALTER TABLE mercado_livre_accounts ADD COLUMN description TEXT"
            )

        connection.commit()

    finally:
        connection.close()
        
def try_download_label_for_shipment(user_id: str, shipment_id: str | None):
    global processed_shipments
    global window_instance

    if not shipment_id:
        print("Sem shipment_id para etiqueta.")
        return

    if shipment_id in processed_shipments:
        print(f"Shipment {shipment_id} já processado. Ignorando.")
        return

    try:
        account_service = AccountService()
        label_service = MercadoLivreLabelService()
        printer_service = PrinterService()
        monitor_service = LiveMonitorService()
        print_control_service = LabelPrintControlService()

        if not monitor_service.get_status():
            print("Monitoramento OFF -> não baixar/imprimir.")
            return

        account = account_service.get_account_by_user_id(user_id)

        if not account:
            print("Conta não encontrada.")
            return

        print(f"Baixando etiqueta do shipment {shipment_id}...")

        label_path = label_service.download_label(
            access_token=account.access_token,
            shipment_id=str(shipment_id),
        )

        if not label_path:
            print("Falha ao baixar etiqueta.")
            return

        processed_shipments.add(shipment_id)

        print("Etiqueta baixada com sucesso.")
        print("ARQUIVO:", label_path)

        log_service = OperationLogService()
        log_service.set_last_label(label_path)

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_labels_page)
            QTimer.singleShot(0, window_instance.refresh_dashboard_page)


        selected_printer = printer_service.get_selected_printer_name()

        if not selected_printer:
            print("Nenhuma impressora selecionada.")
            return

        print("Imprimindo automaticamente...")

        printer_service.print_pdf_file(
            printer_name=selected_printer,
            file_path=label_path,
        )

        print_control_service.mark_as_printed(label_path)
        
        log_service.set_last_print(selected_printer, label_path)

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_labels_page)

    except Exception as error:
        print(f"Erro no fluxo automático: {error}")

        log_service = OperationLogService()
        log_service.set_last_error(f"Fluxo automático: {error}")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_dashboard_page)


def process_webhook_event(event_data: dict):
    global window_instance

    try:
        monitor_service = LiveMonitorService()

        if not monitor_service.get_status():
            print("Monitoramento OFF -> webhook recebido, mas automação bloqueada.")
            return

        body = event_data.get("body", {}) or {}

        topic = body.get("topic") or body.get("type") or ""
        resource = body.get("resource", "") or ""
        user_id = str(body.get("user_id"))
        
        log_service = OperationLogService()
        log_service.set_last_notification(topic, resource, user_id)

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_dashboard_page)

        if not topic:
            print("Webhook sem tópico identificado.")
            return

        if topic == "orders_v2" or "orders/" in resource:
            order_id = resource.split("/")[-1]

            print(f"Buscando pedido real: {order_id}")

            order_service = OrderService()
            order = order_service.create_or_update_from_meli_api(order_id, user_id)

            if not order:
                print("Falha ao salvar pedido real.")
                return

            print("Pedido REAL salvo:")
            print("ORDER_ID:", order.ml_order_id)
            print("ITEM:", order.item_title)
            
            log_service.set_last_order(order.ml_order_id, order.item_title)

            if window_instance is not None:
                QTimer.singleShot(0, window_instance.refresh_dashboard_page)

            if order.ml_shipment_id:
                shipment_service = ShipmentService()

                shipment = shipment_service.create_or_update_from_meli_api(
                    shipment_id=order.ml_shipment_id,
                    user_id=user_id,
                    ml_order_id=order.ml_order_id,
                )

                if shipment:
                    print("SHIPMENT REAL salvo:")
                    print("SHIPMENT_ID:", shipment.ml_shipment_id)
                    print("STATUS:", shipment.shipping_status)
                    print("SUBSTATUS:", shipment.shipping_substatus)
                    
                    log_service.set_last_shipment(
                        shipment.ml_shipment_id,
                        shipment.shipping_status,
                        shipment.shipping_substatus,
                    )

                    if window_instance is not None:
                        QTimer.singleShot(0, window_instance.refresh_dashboard_page)

                    if shipment.shipping_status == "ready_to_ship":
                        print("Shipment pronto para etiqueta.")
                        try_download_label_for_shipment(
                            user_id=user_id,
                            shipment_id=shipment.ml_shipment_id,
                        )
                    else:
                        print(
                            "Shipment não está pronto para etiqueta:",
                            shipment.shipping_status,
                        )
                else:
                    print("Pedido salvo, mas shipment não pôde ser carregado.")
            else:
                print("Pedido salvo sem shipment_id.")

            if window_instance is not None:
                QTimer.singleShot(0, window_instance.refresh_sales_page)

            return

        if topic == "shipments" or "shipments/" in resource:
            shipment_id = resource.split("/")[-1]

            print(f"Buscando shipment real: {shipment_id}")

            shipment_service = ShipmentService()
            shipment = shipment_service.create_or_update_from_meli_api(
                shipment_id=shipment_id,
                user_id=user_id,
                ml_order_id=None,
            )

            if not shipment:
                print("Falha ao salvar shipment real.")
                return

            print("SHIPMENT REAL salvo via webhook:")
            print("SHIPMENT_ID:", shipment.ml_shipment_id)
            print("STATUS:", shipment.shipping_status)
            print("SUBSTATUS:", shipment.shipping_substatus)

            if shipment.ml_order_id:
                print("Shipment vinculado ao ORDER_ID:", shipment.ml_order_id)

                order_service = OrderService()
                order = order_service.create_or_update_from_meli_api(
                    shipment.ml_order_id,
                    user_id,
                )

                if order:
                    print("Pedido relacionado atualizado pelo shipment.")
                    print("ORDER_ID:", order.ml_order_id)
                    print("ITEM:", order.item_title)

                    if window_instance is not None:
                        QTimer.singleShot(0, window_instance.refresh_sales_page)

            if shipment.shipping_status == "ready_to_ship":
                print("Shipment pronto para etiqueta.")
                try_download_label_for_shipment(
                    user_id=user_id,
                    shipment_id=shipment.ml_shipment_id,
                )
            else:
                print(
                    "Shipment não está pronto para etiqueta:",
                    shipment.shipping_status,
                )

            return

        print("Webhook recebido, mas sem tratamento para esse tópico ainda.")
        print("TOPIC:", topic)
        print("RESOURCE:", resource)

    except Exception as error:
        print(f"Erro ao processar webhook: {error}")


def start_webhook_server():
    global webhook_server

    if webhook_server is not None:
        return

    webhook_server = AppWebhookServer(host="127.0.0.1", port=8765)
    webhook_server.start(webhook_callback=process_webhook_event)


def run_oauth_flow():
    global oauth_running
    global window_instance
    global webhook_server

    if oauth_running:
        print("OAuth já está em execução. Aguarde finalizar.")
        return

    oauth_running = True

    try:
        auth_service = MercadoLivreAuthService()
        account_service = AccountService()

        is_valid, message = auth_service.validate_environment()
        print("OAUTH CONFIG:", message)

        if not is_valid:
            return

        state = auth_service.generate_state()
        auth_url = auth_service.build_authorization_url(state)

        print("Abrindo navegador para autorização...")
        print("STATE:", state)
        print("AUTH URL:", auth_url)

        webbrowser.open(auth_url)

        callback_data = webhook_server.wait_for_oauth_callback(timeout=180)

        if not callback_data.received.is_set():
            print("Tempo esgotado aguardando callback.")
            return

        if callback_data.error:
            print("Erro retornado pelo Mercado Livre:", callback_data.error)
            return

        if not callback_data.code:
            print("Nenhum code recebido.")
            return

        if callback_data.state != state:
            print("State inválido. Possível callback inconsistente.")
            return

        print("Code recebido com sucesso.")

        token_data = auth_service.exchange_code_for_token(callback_data.code)
        print("Token recebido para user_id:", token_data.user_id)

        profile = auth_service.get_current_user_profile(token_data.access_token)

        nickname = profile.get("nickname") or f"Conta ML {token_data.user_id}"
        seller_email = profile.get("email")
        account_label = nickname

        token_expires_at = auth_service.calculate_token_expires_at(token_data.expires_in)

        saved_account = account_service.create_or_update_account(
            user_id=str(profile.get("id", token_data.user_id)),
            access_token=token_data.access_token,
            refresh_token=token_data.refresh_token,
            token_type=token_data.token_type,
            nickname=nickname,
            account_label=account_label,
            seller_email=seller_email,
            token_expires_at=token_expires_at,
            is_active=True,
        )

        print("Conta salva com sucesso:")
        print("ID:", saved_account.id)
        print("USER_ID:", saved_account.user_id)
        print("NICKNAME:", saved_account.nickname)

        webhook_server.oauth_callback_data.received.clear()
        webhook_server.oauth_callback_data.code = None
        webhook_server.oauth_callback_data.state = None
        webhook_server.oauth_callback_data.error = None

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_accounts_page)

    except Exception as error:
        print("Erro no fluxo OAuth:", str(error))

    finally:
        oauth_running = False


def refresh_single_account_token(account_id: int):
    global window_instance

    try:
        auth_service = MercadoLivreAuthService()
        account_service = AccountService()

        account = account_service.get_account_by_id(account_id)

        if not account:
            print(f"Conta {account_id} não encontrada.")
            return

        print(f"Atualizando token da conta {account_id}...")

        token_data = auth_service.refresh_access_token(account.refresh_token)
        token_expires_at = auth_service.calculate_token_expires_at(token_data.expires_in)

        account_service.update_account_tokens(
            account_id=account.id,
            access_token=token_data.access_token,
            refresh_token=token_data.refresh_token,
            token_type=token_data.token_type,
            token_expires_at=token_expires_at,
        )

        try:
            profile = auth_service.get_current_user_profile(token_data.access_token)
            account_service.update_account_profile(
                account_id=account.id,
                nickname=profile.get("nickname"),
                seller_email=profile.get("email"),
                account_label=profile.get("nickname"),
            )
        except Exception as profile_error:
            print(f"Token atualizado, mas não foi possível atualizar perfil: {profile_error}")

        print(f"Refresh token da conta {account_id} concluído.")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_accounts_page)

    except Exception as error:
        print(f"Erro ao atualizar token da conta {account_id}: {error}")


def refresh_all_accounts_tokens():
    try:
        account_service = AccountService()
        accounts = account_service.list_accounts()

        if not accounts:
            print("Nenhuma conta para atualizar.")
            return

        print(f"Iniciando refresh global de {len(accounts)} conta(s)...")

        for account in accounts:
            refresh_single_account_token(account.id)

        print("Refresh global concluído.")

    except Exception as error:
        print(f"Erro no refresh global: {error}")


def remove_account(account_id: int):
    global window_instance

    try:
        account_service = AccountService()
        removed = account_service.delete_account(account_id)

        if removed:
            print(f"Conta {account_id} removida com sucesso.")
        else:
            print(f"Conta {account_id} não encontrada para remoção.")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_accounts_page)

    except Exception as error:
        print(f"Erro ao remover conta {account_id}: {error}")


def edit_account(account_id: int, custom_name: str, description: str):
    global window_instance

    try:
        account_service = AccountService()
        updated = account_service.update_custom_fields(
            account_id=account_id,
            custom_name=custom_name,
            description=description,
        )

        if updated:
            print(f"Conta {account_id} editada com sucesso.")
        else:
            print(f"Conta {account_id} não encontrada para edição.")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_accounts_page)

    except Exception as error:
        print(f"Erro ao editar conta {account_id}: {error}")


def create_test_order():
    global window_instance

    try:
        order_service = OrderService()
        order = order_service.create_test_order()

        print("Venda teste criada com sucesso:")
        print("ORDER_ID:", order.ml_order_id)
        print("ITEM:", order.item_title)

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_sales_page)

    except Exception as error:
        print(f"Erro ao criar venda teste: {error}")


def remove_order(ml_order_id: str):
    global window_instance

    try:
        order_service = OrderService()
        removed = order_service.delete_order_by_ml_id(ml_order_id)

        if removed:
            print(f"Venda {ml_order_id} removida com sucesso.")
        else:
            print(f"Venda {ml_order_id} não encontrada para remoção.")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_sales_page)

    except Exception as error:
        print(f"Erro ao remover venda {ml_order_id}: {error}")


def start_oauth_in_background():
    thread = threading.Thread(target=run_oauth_flow, daemon=True)
    thread.start()


def start_refresh_single_token_in_background(account_id: int):
    thread = threading.Thread(
        target=refresh_single_account_token,
        args=(account_id,),
        daemon=True,
    )
    thread.start()


def start_refresh_all_tokens_in_background():
    thread = threading.Thread(
        target=refresh_all_accounts_tokens,
        daemon=True,
    )
    thread.start()


def start_remove_account_in_background(account_id: int):
    thread = threading.Thread(
        target=remove_account,
        args=(account_id,),
        daemon=True,
    )
    thread.start()


def start_edit_account_in_background(account_id: int, custom_name: str, description: str):
    thread = threading.Thread(
        target=edit_account,
        args=(account_id, custom_name, description),
        daemon=True,
    )
    thread.start()


def start_create_test_order_in_background():
    thread = threading.Thread(
        target=create_test_order,
        daemon=True,
    )
    thread.start()


def start_remove_order_in_background(ml_order_id: str):
    thread = threading.Thread(
        target=remove_order,
        args=(ml_order_id,),
        daemon=True,
    )
    thread.start()

def select_printer(printer_name: str):
    global window_instance

    try:
        printer_service = PrinterService()

        if not printer_service.printer_exists(printer_name):
            print(f"Impressora não encontrada: {printer_name}")
            return

        saved = printer_service.save_selected_printer(printer_name)

        if saved:
            print(f"Impressora selecionada com sucesso: {printer_name}")
        else:
            print(f"Falha ao selecionar impressora: {printer_name}")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_printers_page)

    except Exception as error:
        print(f"Erro ao selecionar impressora: {error}")

def start_select_printer_in_background(printer_name: str):
    thread = threading.Thread(
        target=select_printer,
        args=(printer_name,),
        daemon=True,
    )
    thread.start()

def toggle_live_monitor():
    global window_instance

    try:
        monitor_service = LiveMonitorService()
        new_status = monitor_service.toggle_status()

        print("Monitoramento ao vivo alterado.")
        print("NOVO STATUS:", "ON" if new_status else "OFF")

        if window_instance is not None:
            window_instance.refresh_dashboard_page()

    except Exception as error:
        print(f"Erro ao alternar monitoramento: {error}")
        
def start_toggle_live_monitor_in_background():
    toggle_live_monitor()
    
def reprocess_order(ml_order_id: str, user_id: str):
    global window_instance

    try:
        print("Reprocessando venda manualmente...")
        print("ORDER_ID:", ml_order_id)
        print("USER_ID:", user_id)

        order_service = OrderService()
        order = order_service.create_or_update_from_meli_api(ml_order_id, user_id)

        if not order:
            print("Falha ao reprocessar pedido.")
            return

        print("Pedido reprocessado com sucesso.")
        print("ITEM:", order.item_title)

        if order.ml_shipment_id:
            shipment_service = ShipmentService()

            shipment = shipment_service.create_or_update_from_meli_api(
                shipment_id=order.ml_shipment_id,
                user_id=user_id,
                ml_order_id=order.ml_order_id,
            )

            if shipment:
                print("Shipment reprocessado com sucesso.")
                print("SHIPMENT_ID:", shipment.ml_shipment_id)
                print("STATUS:", shipment.shipping_status)
                print("SUBSTATUS:", shipment.shipping_substatus)

                if shipment.shipping_status == "ready_to_ship":
                    print("Shipment pronto para etiqueta.")
                    try_download_label_for_shipment(
                        user_id=user_id,
                        shipment_id=shipment.ml_shipment_id,
                    )
                else:
                    print(
                        "Shipment não está pronto para etiqueta:",
                        shipment.shipping_status,
                    )
            else:
                print("Não foi possível atualizar shipment no reprocessamento.")
        else:
            print("Pedido reprocessado sem shipment_id.")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_sales_page)

    except Exception as error:
        print(f"Erro ao reprocessar venda {ml_order_id}: {error}")

def start_reprocess_order_in_background(ml_order_id: str, user_id: str):
    thread = threading.Thread(
        target=reprocess_order,
        args=(ml_order_id, user_id),
        daemon=True,
    )
    thread.start()
    
def reprint_label(file_path: str):
    global window_instance

    try:
        printer_service = PrinterService()
        print_control_service = LabelPrintControlService()

        selected_printer = printer_service.get_selected_printer_name()

        if not selected_printer:
            print("Nenhuma impressora selecionada para reimpressão.")
            return

        if not file_path:
            print("Arquivo de etiqueta inválido.")
            return

        print("Reimprimindo etiqueta...")
        print("ARQUIVO:", file_path)
        print("IMPRESSORA:", selected_printer)

        printer_service.print_pdf_file(
            printer_name=selected_printer,
            file_path=file_path,
        )

        print_control_service.mark_as_printed(file_path)

        log_service = OperationLogService()
        log_service.set_last_print(selected_printer, file_path)

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_labels_page)
            QTimer.singleShot(0, window_instance.refresh_dashboard_page)

    except Exception as error:
        print(f"Erro ao reimprimir etiqueta: {error}")

        log_service = OperationLogService()
        log_service.set_last_error(f"Reimpressão: {error}")

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_dashboard_page)


def remove_label(file_path: str):
    global window_instance

    try:
        label_service = LabelFileService()
        print_control_service = LabelPrintControlService()

        removed = label_service.delete_label(file_path)

        if removed:
            print_control_service.remove_label_record(file_path)

            print("Etiqueta removida com sucesso.")
            print("ARQUIVO:", file_path)
        else:
            print("Etiqueta não encontrada para remoção.")
            print("ARQUIVO:", file_path)

        if window_instance is not None:
            QTimer.singleShot(0, window_instance.refresh_labels_page)

    except Exception as error:
        print(f"Erro ao remover etiqueta: {error}")


def start_reprint_label_in_background(file_path: str):
    thread = threading.Thread(
        target=reprint_label,
        args=(file_path,),
        daemon=True,
    )
    thread.start()


def start_remove_label_in_background(file_path: str):
    thread = threading.Thread(
        target=remove_label,
        args=(file_path,),
        daemon=True,
    )
    thread.start()

def main():
    global window_instance

    initialize_database()
    start_webhook_server()

    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    window = MainWindow()
    window_instance = window

    window.sync_requested.connect(start_oauth_in_background)
    window.dashboard_page.toggle_monitor_requested.connect(start_toggle_live_monitor_in_background)
    window.accounts_page.connect_account_requested.connect(start_oauth_in_background)
    window.accounts_page.refresh_all_tokens_requested.connect(start_refresh_all_tokens_in_background)
    window.accounts_page.refresh_token_requested.connect(start_refresh_single_token_in_background)
    window.accounts_page.remove_account_requested.connect(start_remove_account_in_background)
    window.accounts_page.edit_account_requested.connect(start_edit_account_in_background)
    window.sales_page.create_test_order_requested.connect(start_create_test_order_in_background)
    window.sales_page.remove_order_requested.connect(start_remove_order_in_background)
    window.sales_page.reprocess_order_requested.connect(start_reprocess_order_in_background)
    window.labels_page.reprint_label_requested.connect(start_reprint_label_in_background)
    window.labels_page.remove_label_requested.connect(start_remove_label_in_background)
    window.printers_page.select_printer_requested.connect(start_select_printer_in_background)

    def open_main_window():
        splash.close()
        window.show()

    QTimer.singleShot(2600, open_main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()