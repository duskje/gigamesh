from mido import Message, open_output, open_input, get_input_names
from enum import IntEnum
from dataclasses import dataclass
from itertools import islice


def batched(iterable, n):
    it = iter(iterable)

    while batch := tuple(islice(it, n)):
        yield batch


def midi_data_to_internal_data(raw_data: tuple[int]) -> tuple[int]:
    internal_data: list[int] = []

    for batch in batched(raw_data, n=8):
        leading_bits = 0

        for i, byte in enumerate(batch):
            if byte == 0b11110111:
                break

            if i == 0:
                leading_bits = byte
            else:
                leading_bit = leading_bits & (0b1 << i - 1)
                internal_data.append(byte | (leading_bit << (7 - (i - 1))))

    return tuple(internal_data)


class KorgMode(IntEnum):
    COMBI = 0
    PROG = 2
    SEQ = 4


class KorgResultReport(IntEnum):
    OK = 0
    DATA_LENGTH_IS_WRONG = 1
    DEST_MEMORY_IS_PROTECTED = 2
    DEST_DOES_NOT_EXIST = 3
    WRONG_MODE = 4
    MEMORY_OVERFLOW = 5
    OTHER_ERROR = 40


@dataclass
class KorgCombiParameters:
    raw_data: tuple[int]
    internal_data: tuple[int] | None = None

    def __post_init__(self):
        self.internal_data = midi_data_to_internal_data(self.raw_data)

    @property
    def title(self):
        return ''.join([chr(byte) for byte in self.raw_data[0:23]])
    
    @property
    def control_assign(self):
        return self.internal_data[632]

    def get_volume(self, channel_no: int):
        return self.internal_data[836 + (112 * channel_no) + 5]
    

class KorgKrome:
    SYSEX_HEADER = 'f0 42 30 00 01 15'
    SYSEX_TAIL = ' f7'

    def __init__(self, port_name: str):
        self.out = open_output(port_name)
        self.input = open_input(port_name)

    def change_to_combi_mode(self):
        self.out.send(Message.from_hex('f0 42 30 00 01 15 4e 00 f7'))

    def set_combi(self, category_id: str, combi_id: int):
        if category_id == 'A':
            value = 0
        elif category_id == 'B':
            value = 1
        elif category_id == 'C':
            value = 2
        elif category_id == 'D':
            value = 3
        else:
            raise ValueError

        self.out.send(Message('control_change', channel=0, control=0, value=0))
        self.out.send(Message('control_change', channel=0, control=32, value=value))
        self.out.send(Message('program_change', program=combi_id))

    def mute_prog_by_id(self, prog_id: int):
        self.out.send(Message.from_hex(f'f0 42 30 00 01 15 41 00 00 {prog_id:02x} 00 28 00 00 00 00 01 f7'))

    def mute_prog(self, channel_no: int):
        self.mute_prog_by_id(0xb + channel_no)

    def mode_request(self) -> KorgMode:
        self.out.send(Message.from_hex(f'f0 42 30 00 01 15 12 f7'))
        msg = self.input.receive()

        return msg.data[6]

    def current_object_parameter_request(self):
        message = self.SYSEX_HEADER
        message += ' 74 '
        message += ' 01 '
        message += self.SYSEX_TAIL

        self.out.send(Message.from_hex(message))
        return self.input.receive()

    def combination_bank_parameter_dump_request(self):
        message = self.SYSEX_HEADER
        message += ' 72 '
        message += ' 01 '
        message += ' 03 '
        message += ' 00 '
        message += ' 01 '
        message += self.SYSEX_TAIL

        self.out.send(Message.from_hex(message))
        return self.input.receive()


@dataclass
class KorgPatch:
    patch_name: str
    patch_id: str


def main():
    korg_input = None

    for input_name in get_input_names():
        if input_name.split(':')[0] == 'KROME':
            korg_input = input_name

    if korg_input is None:
        raise ValueError('Korg not found.')

    korg = KorgKrome(korg_input)

    print(korg.mode_request() == KorgMode.COMBI)

    # korg.change_to_combi_mode()

    # song_list = {
    #         'profugos': 0,
    #         'danza_rota': 1,
    #         'nada_personal': 2,
    #         'el_rito': 3,
    #         'septimo_dia': 4,
    #         'sobredosis_de_tv': 5,
    #         'ciudad_de_la_furia': 15,
    # }

    # korg.set_combi('D', song_list['ciudad_de_la_furia'])
    # korg.mute_prog(6)
    dump = korg.combination_bank_parameter_dump_request()
    print(''.join([chr(byte) for byte in dump.data[10:34]]))

    dump = korg.current_object_parameter_request()
    print(''.join([chr(byte) for byte in dump.data[9:34]]))
    combi_parameters = KorgCombiParameters(dump.data[8:])
    print(combi_parameters.control_assign)
    print(combi_parameters.get_volume(4))


if __name__ == '__main__':
    main()
