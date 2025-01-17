import struct
from datetime import datetime

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
            self.last_modified.strftime('%Y-%m-%d %H:%M:%S').ljust(20, '\x00').encode('utf-8'),  #trzeba sformatować
            self.free_space
        )

    def from_binary(self, data):
        num_of_files, last_mod, free_space = struct.unpack('I20sI', data)
        self.num_of_files = num_of_files
        self.last_modified = last_mod.decode('utf-8').strip('\x00')
        self.free_space = free_space

    def info(self):
        print(f"Number of files: {self.num_of_files}")
        print(f"Last modified: {self.last_modified}")
        print(f"Free space: {self.free_space}")

    def size(self):
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
    def __init__(self):
        # info o poszcególnym pliku/katalogu
        self.created = None
        self.last_modified = None
        # self.permissions = None
        self.size = 0
        self.is_directory = False
        self.data_blocks_idx = []  #muszą być zapisane w odpowiedniej kolejności

    def to_binary(self):
        # data_blocks_idx
         # Zapisanie długości listy, a potem danych
        # length = len(self.data_blocks_idx)
        # Zapisujemy długość listy, a potem każdy element listy jako liczba całkowita
        # return struct.pack('I', length) + b''.join([struct.pack('I', item) for item in self.data_blocks_idx])

        # return struct.pack(
        #     '20s20s12sI'
        # )

        pass

    def from_binary(self):
        pass

    def add_file(self):
        # zmiana: last_modified, size, data_blocks_idx, is_dir
        pass

    # def chmod(self):
    #     pass


class Bitmap:
    def __init__(self, size):
        self.size = size
        self.map = [0] * size

    def find_free_inode_idx(self):
        for idx, val in enumerate(self.map):
            if val == 0:
                return idx


class DataBlock:
    def __init__(self):
        self.size = 0
        self.content

