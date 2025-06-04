from enum import Enum, IntEnum

class A(IntEnum):
    VK_NONE = (-1, "none", "none")
    
    A = (1, "a", "L-a")
    B = (0, "b", "R-b")
    
    def __new__(cls, value, common_name, specific_name):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.common_name = common_name
        obj.specific_name = specific_name
        return obj
    
    @classmethod
    def get(cls, key_code):
        """Находит клавишу по коду или возвращает VK_NONE."""
        try:
            return cls(key_code)
        except ValueError:
            return cls.VK_NONE
    
    @classmethod
    def get_by_common_name(cls, name):
        """Возвращает все варианты клавиш с общим именем (например 'ctrl')."""
        return [m for m in cls if m.common_name == name]
    
    @classmethod
    def get_by_specific_name(cls, name):
        """Находит точную клавишу по конкретному имени (например 'left-ctrl')."""
        for member in cls:
            if member.specific_name == name:
                return member
        return cls.VK_NONE
    
import string
for word in string.digits:
    print(f"""VK_{word.upper()} = (ord("{word.upper()}"), "{word}", "{word}")""")

# print(A(0, "a", "a"))