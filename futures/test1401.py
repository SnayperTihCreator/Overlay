import asyncio
from rope import SmartRope, AsyncWire, support_ropes


class CacheAsyncWire(AsyncWire):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
    
    async def _async_wrapper(self, *args, **kwargs):
        key = (args, tuple(kwargs.items()))
        if key not in self._cache:
            print(f"[Log] Считаем {self._name}...")
            self._cache[key] = await super()._async_wrapper(*args, **kwargs)
        return self._cache[key]
    
    def clear(self):
        self._cache.clear()

@support_ropes
class UserAPI:
    __slots__ = ('user_id', )  # Работает даже со слотами
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    @SmartRope(CacheAsyncWire)
    async def get_profile(self):
        await asyncio.sleep(0.5)  # Имитация сети
        return {"id": self.user_id, "name": "Admin"}


# Тест
async def main():
    api = UserAPI(42)
    
    # Первый вызов (долгий)
    print(await api.get_profile())
    
    # Второй вызов (мгновенный, из кэша обертки)
    print(await api.get_profile())
    
    # Очистка кэша через "преблуду"
    api.get_profile.clear()
    
    # Снова долгий вызов
    print(await api.get_profile())


if __name__ == "__main__":
    asyncio.run(main())
