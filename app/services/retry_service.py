import time
from typing import Any, Callable


class RetryService:
    def run(
        self,
        action: Callable[[], Any],
        action_name: str = "ação",
        max_attempts: int = 3,
        delay_seconds: float = 1.5,
    ) -> Any:
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                print("=====================================")
                print(f"Tentativa {attempt}/{max_attempts} para: {action_name}")
                print("=====================================")

                result = action()

                print(f"✅ Sucesso em: {action_name}")
                return result

            except Exception as error:
                last_error = error

                print(f"⚠️ Falha em {action_name}: {error}")

                if attempt < max_attempts:
                    print(f"Aguardando {delay_seconds} segundo(s) para tentar novamente...")
                    time.sleep(delay_seconds)

        print(f"❌ Todas as tentativas falharam para: {action_name}")
        raise last_error