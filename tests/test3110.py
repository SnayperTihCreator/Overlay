# Пример демонстрирующий, что super() не всегда вызывает непосредственного родителя
class A:
    def test(self):
        print("A")

class B(A):
    def test(self):
        print("B")
        super().test()

class C(A):
    def test(self):
        print("C")
        super().test()

class D(B, C):
    def test(self):
        print("D")
        super().test()

d = D()
d.test()
# Вывод: D B C A (а не D B A)