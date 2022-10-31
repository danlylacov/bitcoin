

class Tx:  # класс транкзакции
    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        self.version = version  # версия
        self.tx_ins = tx_ins  # ввод
        self.tx_outs = tx_outs  # вывод
        self.locktime = locktime  # время блокировки
        self.testnet = testnet  # сеть тестнет или реальная

    def __repr__(self):  # вывод класса
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins = tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\n' \
               'version: {}\n' \
               'tx_ins:\n{}\n' \
               'tx_outs:\n{}\n' \
               'locktime: {}' \
            .format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime
        )

    def id(self):
        return self.hash().hex()

    def hash(self):
        return hash256(self.serialize()[::-1])

    @classmethod
    def parse(cls, s, testnet=False):
        version = little_endian_to_int(s.read(4))
        num_inputs = read_varint(s)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        num_outputs = read_varint(s)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        locktime = little_endian_to_int(s.read(4))
        return cls(version, inputs, outputs, locktime, testnet=testnet)

    def serialize(self):  # транзакция -> последовательность байтов
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_variant(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.locktime, 4)
        return result


class TxIn:  # ввод транзакции
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        self.prev_tx = prev_tx  # индефикатор предыдущей транзакции
        self.prev_index = prev_index  # индекс предыдущей транзакции
        if script_sig is None:  # стандартно поле сценария пустое
            self.script_sig = Script()
        else:
            self.script_sig = script_sig  # Сценарий ScriptSig
            self.sequence = sequence  # последовательность

    def __repr__(self):
        return '{} : {}'.format(
            self.prev_tx.hex(),
            self.prev_index
        )

    @classmethod
    def parse(cls, s):  # строка ввода -> объект TxIn
        prev_tx = s.read(32)[::-1]
        prev_index = little_endian_to_int(s.read(4))
        script_sig = Script.parse(s)
        sequence = little_endian_to_int(s.read(4))
        return cls(prev_tx, prev_index, script_sig, sequence)

    def serialize(self):  # ввод транзакции -> последовательность байтов
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result


class TxOut:
    def __init__(self, amount, script_pubkey):
        self.amount = amount  # сумма
        self.script_pubkey = script_pubkey  # сценарий

    def __repr__(self):
        return '{} : {}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        amount = little_endian_to_int(s.read(8))
        script_pubkey = Script.parse(s)
        return cls(amount, script_pubkey)

    def serialize(self):  # вывод транзакции -> последовательность байтов
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result


class TxFetcher:  # класс извлечения информации о транзакциях
    cache = {}

    @classmethod
    def get_url(cls, testnet=False):
        if testnet:
            return 'http://testnet.programmingbitcoin.com'
        else:
            return 'http://main.programmingbitcoin.com'

    
