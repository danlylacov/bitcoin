from io import BytesIO
from helper import *
import json
import requests


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

    def fee(self, testnet=False): # расчёт платы за транзакцию
        input_sum, output_sum = 0, 0
        for tx_in in self.tx_ins:
            input_sum += tx_in.value(testnet=testnet)
        for tx_out in self.tx_outs:
            output_sum += tx_out.amount
        return input_sum - output_sum

    def sig_hash(self, input_index): # вычисление хеша подписи
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.tx_ins))
        for i, tx_in in enumerate(self.tx_ins):
            if i == input_index:
                s += TxIn(
                    prev_tx=tx_in.prev_tx,
                    prev_index=tx_in.prev_index,
                    script_sig=tx_in.script_pubkey(self.testnet),
                    sequence=tx_in.sequence,
                ).serialize()
            else:
                s += TxIn(
                    prev_tx=tx_in.prev_tx,
                    prev_index=tx_in.prev_index,
                    sequence=tx_in.sequence,
                ).serialize()
        s += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            s += tx_out.serialize()
        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)
        h256 = hash256(s)
        return int.from_bytes(h256, 'big')

    def verify_input(self, input_index): # проверка ввода транзакции на достоверность
        tx_in = self.tx_ins[input_index]
        script_pubkey = tx_in.script_pubkey(testnet=self.testnet)
        z = self.sig_hash(input_index)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)

    def verify(self): # верификация всей транзакции
        if self.fee() < 0: # проверка на отсутствие создания биткоинов в даннной транз.
            return False
        for i in range(len(self.tx_ins)):# проверка ScriptSig
            if not self.verify_input(i):
                return False
            return True





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

    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False): # -> сумма из вывода
        tx =self.fetch_tx(testnet=testnet)
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False):# сценарий ScriptPubKey -> объект типа Script
        tx = self.fetch_tx(testnet=testnet)
        return tx.tx_outs[self.prev_index].script_pubkey




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

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False): # извлечение класса транзакции
        if fresh or (tx_id not in cls.cache):
            url = '{}/tx/{}/hex'.format(cls.get_url(testnet), tx_id)
            response = requests.get(url)
            try:
                raw = bytes.fromhex(response.text.strip())
            except ValueError:
                raise ValueError('unexpected response: {}'.format(response.text))
            if raw[4] == 0:
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
            if tx.id() != tx_id:
                raise ValueError('not the same id: {} vs {}'.format(tx.id(),
                                                                    tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]


