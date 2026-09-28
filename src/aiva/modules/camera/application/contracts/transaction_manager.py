from contextlib import AbstractAsyncContextManager
from typing import Protocol


class TransactionManager(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]:
        """Commit al salir del bloque sin errores; rollback si se lanza una excepción."""
        ...
