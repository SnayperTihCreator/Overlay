from typing import Protocol, runtime_checkable

@runtime_checkable
class Closed(Protocol):
    def close(self): ...
    
    
class A:
    def close(self):
        print("close")
        
        
print(issubclass(A, Closed))