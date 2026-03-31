import queue
import threading
import time


class WebhookQueueService:
    def __init__(self):
        self._queue = queue.Queue()
        self._is_running = False
        self._worker_thread = None
        self._lock = threading.Lock()

    def start(self, processor_callback):
        with self._lock:
            if self._is_running:
                return

            self._is_running = True

            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                args=(processor_callback,),
                daemon=True,
            )
            self._worker_thread.start()

            print("✅ Fila de webhook iniciada.")

    def stop(self):
        with self._lock:
            self._is_running = False

        print("🛑 Fila de webhook sinalizada para parar.")

    def enqueue(self, event: dict):
        self._queue.put(event)
        print(f"📥 Evento adicionado na fila. Tamanho atual: {self._queue.qsize()}")

    def _worker_loop(self, processor_callback):
        while self._is_running:
            try:
                event = self._queue.get(timeout=1)

                try:
                    print("▶️ Processando evento da fila...")
                    processor_callback(event)
                    print("✅ Evento processado pela fila.")

                except Exception as error:
                    print(f"❌ Erro ao processar evento da fila: {error}")

                finally:
                    self._queue.task_done()

            except queue.Empty:
                time.sleep(0.1)

    def get_queue_size(self) -> int:
        return self._queue.qsize()