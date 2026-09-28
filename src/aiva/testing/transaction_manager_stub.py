from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


class TransactionManagerStub:
    """Cumple el Protocol TransactionManager de cualquier módulo; cuenta commits y rollbacks."""

    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        try:
            yield
            self.commits += 1
        except BaseException:
            self.rollbacks += 1
            raise
