class FieldElement:

    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} not in field range 0 to {}'.format(num, prime - 1)
            raise ValueError(error)
        self.num = num  # 'эллемент поля
        self.prime = prime  # размерность поля

    def __repr__(self):  # вывод элемента класса
        return 'FieldElement_{}({})'.format(self.prime, self.num)

    def __eq__(self, other):  # проверка равенства двух объектов класса
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):  # проверка неравенства
        if other is None:
            return False
        return self.num != other.num or self.prime != other.prime

    def __add__(self, other):  # +
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in diffrent Fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)

    def __sub__(self, other):  # -
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in diffrent Fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)

    def __mul__(self, other):  # *
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in diffrent Fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):  # возведение в степень (**)
        num = (self.num ** exponent) % self.prime
        return self.__class__(num, self.prime)

    def __truediv__(self, other):  # деление (/)
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in diffrent Fields')
        num = self.num * pow(other.num, self.prime - 2, self.prime) % self.prime
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):  # переопределение операции возведения в степень, для возведения в отриц. степень
        n = exponent
        while n < 0:
            n += self.prime - 1
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)



class Point:
    # y**2 = x**2 + ax + b
    def __init__(self, x, y, a, b): # инициализация
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        if self.x is None and  self.y is None:
            return
        if self.y**2 != self.x**3 + a*x + b: # проверка на нахождение точки на заданной прямой
            raise ValueError('({}, {}) is not on curve'.format(x,y))

    def __repr__(self): # вывод экземпляра класса
        return 'Point({},{},{},{})'.format(self.x,self.y, self.a, self.b)

    def __eq__(self, other): # проверка равенства объектов класса
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b

    def __ne__(self, other):# проверка неравенства обьекта класса
        return self.x != other.x and self.y != other.y \
            and self.a != other.a and self.b != other.b

    def __add__(self, other): # перегрузка оператора сложения
        if self.a != other.a or self.b != other.b: # проверка, что складываемые точки на одной прямой
            raise TypeError('Points {},{} are not on the same curve'
                            .format(self, other))
        if self.x is None: # Если одна из точек None, то она бесконечно удаленная
            return other
        if other.x is None:
            return self

        if self.x == other.x and self.y!= self.y: # вертикальная линия -> точка бесконечно удалённая
            return self.__class__(None, None, self.a, self,b)

        if self.x != other.x: # сложение
            s = (other.y - self.y)/(other.x-self.x)
            x_3 = s**2 - self.x - other.x
            y_3 = s*(self.x - x_3) - self.y
            return self.__class__(x_3, y_3, self.a, self.b)

        if self == other: # cложение, если одна точка напротив другой
            s = (3 * self.x**2 + self.a) / (2 * self.y)
            x = s**2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

        if self == other and self.y == 0 * self.x: #  когда касательная проведена по вертикали
            return self.__class__(None, None, self.a, self.b)

print(Point(2, 5,5,7)+(Point(-1,-1, 5, 7)))









