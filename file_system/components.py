import struct
from datetime import datetime
import math

NUM_OF_INODES = 1024
BYTES = 8


class Superblock:
    def __init__(self, fs_size):
        # nie pobiera żadnych danych wejściowych bo jest tworzony
        # przy inicjalizacji file_systemu
        # jeśli file_system jest pobierany to dane są przypisywene
        # z pliku binarneg

        self.num_of_files = 0
        self.last_modified = datetime.now()
        self.free_space = fs_size  #w bajtach

    def to_binary(self):
        return struct.pack(
            'I20sI',
            self.num_of_files,
            self.last_modified.strftime('%Y-%m-%d %H:%M:%S').ljust(20, '\x00').encode('utf-8'),
            self.free_space
        )

    def from_binary(self, data):
        num_of_files, last_mod, free_space = struct.unpack('I20sI', data)
        self.num_of_files = num_of_files
        # self.created = datetime.strptime(created.decode('utf-8').strip('\x00'), "%Y-%m-%d %H:%M:%S")
        self.last_modified = datetime.strptime(last_mod.decode('utf-8').strip('\x00'), "%Y-%m-%d %H:%M:%S")
        # self.last_modified = datatime.last_mod.decode('utf-8').strip('\x00')
        self.free_space = free_space

    def info(self):
        print(f"Number of files: {self.num_of_files}")
        print(f"Last modified: {self.last_modified}")
        print(f"Free space: {self.free_space}")

    def get_size(self):
        """Oblicz rozmiar superbloku w bajtach."""
        # Format struktury: 'I20sI' (jak w metodzie to_bytes/from_bytes)
        return struct.calcsize('I20sI')

    def update_last_modified(self):
        self.last_modified = datetime.now()

    def increase_num_of_files(self):
        self.num_of_files += 1
        self.update_last_modified()

    def decrease_num_of_files(self):
        self.num_of_files -= 1
        self.update_last_modified()

    def release_memory_after_file(self, size):
        self.free_space += size
        self.update_last_modified()

    def take_memory_for_file(self, size):
        self.free_space -= size
        self.update_last_modified()


class Inode:
    def __init__(self, max_blocks):
        # info o poszcególnym pliku/katalogu
        # max blocks = max_file size // block size = 100
        self.created = datetime.now()
        self.last_modified = datetime.now()
        self.is_directory = False
        self.size = 0
        self.hard_links_counter = 0
        self.data_blocks_idx = []  #muszą być zapisane w odpowiedniej kolejności
        self._max_num_of_blocks = max_blocks


    def to_binary(self):
        max = self._max_num_of_blocks
        all_data_blocks = self.data_blocks_idx + [0] * (max - len(self.data_blocks_idx))
        return struct.pack(
            f'20s20s?II{max}I',
            self.created.strftime('%Y-%m-%d %H:%M:%S').ljust(20, '\x00').encode('utf-8'),
            self.last_modified.strftime('%Y-%m-%d %H:%M:%S').ljust(20, '\x00').encode('utf-8'),
            self.is_directory,
            self.size,
            self.hard_links_counter,
            *all_data_blocks
        )

    def from_binary(self, data):
        max = self._max_num_of_blocks
        created, last_mod, is_dir, size, hard_links, *full_data_blocks = struct.unpack(f'20s20s?II{max}I', data)

        self.created = datetime.strptime(created.decode('utf-8').strip('\x00'), "%Y-%m-%d %H:%M:%S")
        self.last_modified = datetime.strptime(last_mod.decode('utf-8').strip('\x00'), "%Y-%m-%d %H:%M:%S")
        self.is_directory = is_dir
        self.size = size
        self.hard_links_counter = hard_links
        self.data_blocks_idx = [x for x in full_data_blocks if x != 0]

    def get_size(self):
        """Oblicz rozmiar jednego i-node'a w bajtach."""
        # Format struktury: '20s20sI10I?' (jak w metodzie to_bytes/from_bytes)
        max = self._max_num_of_blocks
        return struct.calcsize(f'20s20s?II{max}I')

    def create_directory(self):
        # zmiana: last_modified, size, data_blocks_idx, is_dir
        self.created = datetime.now()
        self.last_modified = datetime.now()
        self.is_directory = True

    def add_data_block_idx(self, idx):
        self.data_blocks_idx.append(idx)

class Bitmap:
    def __init__(self, size):
        self.size = size  # w bitach, a nie bajtach
        self.map = [0] * math.ceil(size / 8)  # Bitmapa zajętości (w bajtach)

    def find_free_inode_idx(self):
        for idx, val in enumerate(self.map):
            if val == 0:
                return idx

    def take_idx(self, idx_number):
        self.map[idx_number] = 1

    def realease_idx(self, idx_number):
        self.map[idx_number] = 0

    def to_binary(self):
        # Konwersja bitarray do postaci bajtów
        return struct.pack(f'{len(self.map)}B', *self.map)

    def from_binary(self, data):
        # Odczyt bitów z danych (w postaci bajtów)
        # self.size = len(data) * 8 nie muszę zmieniać
        #       bo moja bitmapa ma stalą wartość
        self.map = list(struct.unpack(f'{len(data)}B', data))

    def info(self):
        print(f"Bitmap len : {len(self.map)}")
        # print(f"Bitmap: {self.map}")


class DataBlock:
    def __init__(self, data_block_size):
        self.size = data_block_size
        self.content = b'\x00' * self.size  #bajty

    def to_binary(self):
        return self.content

    def from_binary(self, data):
        self.content = data

    def new_content(self, n_content):
        if isinstance(n_content, str):
            # Jeśli dane są w formacie str, zakoduj je na bytes i dopełnij zerami.
            encoded_content = n_content.encode('utf-8')
            self.content = encoded_content + b'\x00' * (self.size - len(encoded_content))
        elif isinstance(n_content, bytes):
            # Jeśli dane są już w formacie bytes, dopełnij je zerami.
            self.content = n_content + b'\x00' * (self.size - len(n_content))
        else:
            raise ValueError("n_content must be of type str or bytes")
