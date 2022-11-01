from helper import hash256, hash160

def op_dup(stack): # функция дублирования элемента на вершине стека
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True

def op_hash(stack): # эллемент из вершины стека -> хеширование -> возврат в стек
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hash256(element))
    return True

def op_hash160(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    h160 = hash160(element)
    stack.append(h160)
    return True

OP_CODE_FUNCTIONS = { # коды функций
    118: op_dup,
    170: op_hash,
    169: op_hash160,
}
