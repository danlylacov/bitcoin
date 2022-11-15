import hashlib



BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'




# tag::source4[]
def hash160(s):
    '''sha256 followed by ripemd160'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()  # <1>
# end::source4[]


def hash256(s):
    '''two rounds of sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


# tag::source2[]
def encode_base58(s):
    count = 0
    for c in s:  # <1>
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:  # <2>
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result  # <3>


def encode_base58_checksum(b):
    return encode_base58(b + hash256(b)[:4])



def decode_base58(s):
    num = 0
    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)
    combined = num.to_bytes(25, byteorder='big')
    checksum = combined[-4:]
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError('bad address: {} {}'.format(checksum, hash256(combined[:-4])[:4]))
    return combined[1:-4]

def little_endian_to_int(b): # байты в исх порядке -> целое число
    return int.from_bytes(b, 'little')

def int_to_little_endian(n, length): # целое число -> байты в обратном порядке
    return n.to_bytes(length, 'big')

def read_varint(s): # вариант в закод. виде -> возвр int
    i = s.read(1)[0]
    if i == 0xfd:
        return little_endian_to_int(s.read(2))
    elif i == 0xfe:
        return little_endian_to_int(s.read(4))
    elif i == 0xff:
        return little_endian_to_int(s.read(8))
    else:
        return i

def encode_varint(i): # int -> вариант в байтовом представлении(для количества транзакций в классе Tx)
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return  b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError('integer too large: {}'.format(i))

def p2pkh_script(h160):# хеш-код -> сценарий ScriptPubKey
    return Script([0x76, 0xa9, h160, 0x88, 0xac])

