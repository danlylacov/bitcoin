
class FieldElement:

    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} not in field range 0 to {}'.format(
                num, prime - 1)
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self):
        return 'FieldElement_{}({})'.format(self.prime, self.num)

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):
        # this should be the inverse of the == operator
        return not (self == other)

    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num + other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot subtract two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num - other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num * other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        # use fermat's little theorem:
        # self.num**(p-1) % p == 1
        # this means:
        # 1/n == pow(n, p-2, p)
        num = (self.num * pow(other.num, self.prime - 2, self.prime)) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime
        return self.__class__(num=num, prime=self.prime)



class Point: # x, y - координаты точки, а, б - задаём график
    # y**2 = x**2 + ax + b
    def __init__(self, x, y, a, b): # инициализация
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        if self.x is None and  self.y is None:
            return
        if self.y ** 2 != self.x ** 3 + a * x + b:
            raise ValueError('({}, {}) is not on the curve'.format(x, y))
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

        if self == other:
            s = (3 * self.x**2 + self.a) / (2 * self.y)
            x = s ** 2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

        if self == other and self.y == 0 * self.x: #  когда касательная проведена по вертикали
            return self.__class__(None, None, self.a, self.b)

    def __rmul__(self, coefficient): # умножение на коэффициент
        coef = coefficient
        current = self  # <1>
        result = self.__class__(None, None, self.a, self.b)  # <2>
        while coef:
            if coef & 1:  # <3>
                result += current
            current += current  # <4>
            coef >>= 1  # <5>
        return result

A = 0
B = 7
P = 2**256 - 2**32 - 977 # размерность поля
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141



class S256Field(FieldElement):

    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

 # для уравнения кривой




class S256Point(Point):
    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)

    def __repr__(self):
        if self.x is None:
            return 'S256Point(infinity)'
        else:
            return 'S256Point({}, {})'.format(self.x, self.y)

    def __rmul__(self, coefficient):
        coef = coefficient % N  # <1>
        return super().__rmul__(coef)

    def verify(self, z, sig):
        s_inv = pow(sig.s, N-2, N)
        u = z * s_inv % N
        v = sig.r * s_inv % N
        total = u * G + v * self
        return total.x.num == sig.r




# класс верификации подписи
class Signature:
    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return 'Signature ({:x}, {:x})'.format(self.r, self.s)


    











