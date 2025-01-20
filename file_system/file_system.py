from components import Superblock, Inode, Bitmap, DataBlock
from typing import List
import math


class FileSystem:
    FILE_SYSTEM_SIZE = 100 * 1024 * 1024  # 100 MB
    INODES_NUMBER = 1024
    DATA_BLOCK_SIZE = 2 * 1024  # 2KB
    DATA_BLOCKS_NUMBER = FILE_SYSTEM_SIZE // DATA_BLOCK_SIZE  # 50 * 1024
    MAX_FILE_SIZE = 200 * 1024  # 200 KB
    MAX_BLOCKS = MAX_FILE_SIZE // DATA_BLOCK_SIZE  # 100 KB

    def __init__(self, file_name):
        self.file_name = file_name
        self.superblock = Superblock(FileSystem.FILE_SYSTEM_SIZE)
        self.inode_table = [Inode(FileSystem.MAX_BLOCKS) for _ in range(FileSystem.INODES_NUMBER)]
        self.inode_bitmap = Bitmap(FileSystem.INODES_NUMBER)
        self.data_blocks_table = [DataBlock(FileSystem.DATA_BLOCK_SIZE) for _ in range(FileSystem.DATA_BLOCKS_NUMBER)]
        self.data_blocks_bitmap = Bitmap(FileSystem.DATA_BLOCKS_NUMBER)
        self._data_blocks_offset = None

    def save(self):
        with open(self.file_name, 'wb') as fs:
            fs.write(self.superblock.to_binary())

            for inode in self.inode_table:
                fs.write(inode.to_binary())

            fs.write(self.inode_bitmap.to_binary())
            fs.write(self.data_blocks_bitmap.to_binary())

            for block in self.data_blocks_table:
                fs.write(block.to_binary())

        self.superblock.info()
        self.inode_bitmap.info()
        self.data_blocks_bitmap.info()

    def create_new(self):
        self.create_root_dir()
        self.save()

    def load_old(self):
        with open(self.file_name, 'rb') as f:
            self.superblock.from_binary(f.read(self.superblock.get_size()))

            for inode in self.inode_table:
                inode.from_binary(f.read(inode.get_size()))

            self.inode_bitmap.from_binary(f.read(math.ceil(self.inode_bitmap.size // 8) ))
            self.data_blocks_bitmap.from_binary(f.read(math.ceil(self.data_blocks_bitmap.size // 8)))

            for block in self.data_blocks_table:
                block.from_binary(f.read(block.size))

        self.superblock.info()
        self.inode_bitmap.info()
        self.data_blocks_bitmap.info()
        # print(self.data_blocks_table[3].content)

    # def save_file_system(self):
    def create_root_dir(self):
        self.inode_bitmap.take_idx(0)
        self.data_blocks_bitmap.take_idx(0)

        inode_idx = 1
        data_block_idx = 1
        # zajęcie inode
        self.inode_bitmap.take_idx(inode_idx)

        # dane dla inoda:
        dir_inode = self.inode_table[inode_idx]
        dir_inode.create_directory()

        # zajęcie bloku danych
        self.data_blocks_bitmap.take_idx(data_block_idx)
        dir_inode.data_blocks_idx.append(data_block_idx)

    def create_directory(self, dir_name, parent_inode_idx=1):
        inode_idx = self.inode_bitmap.find_free_inode_idx()
        data_block_idx = self.data_blocks_bitmap.find_free_inode_idx()
        # zajęcie inode
        self.inode_bitmap.take_idx(inode_idx)

        # dane dla inoda:
        dir_inode = self.inode_table[inode_idx]
        dir_inode.create_directory()

        # zajęcie bloku danych
        self.data_blocks_bitmap.take_idx(data_block_idx)
        dir_inode.data_blocks_idx.append(data_block_idx)

        # zwiększenie ilości plików w superbloku
        # self.superblock.increase_num_of_files()
        self.add_to_directory(parent_inode_idx, dir_name, inode_idx)

    def add_to_directory(self, dir_inode_idx, filename, file_inode_idx=None):
        if file_inode_idx is None:
            file_inode_idx = self.inode_bitmap.find_free_inode_idx()
        # znależć lub stworzyć datablock przyisany do dir_inode
        entry = f"{filename}:{file_inode_idx}\n".encode('utf-8')
        # znaleźć wolne miejsce w data block i dopisać
        block_idx = self.inode_table[dir_inode_idx].data_blocks_idx[0]

        with open(self.file_name, 'rb') as f:

            # offset
            f.read(self.superblock.get_size())
            f.read(FileSystem.INODES_NUMBER * self.inode_table[0].get_size())
            f.read(math.ceil(self.inode_bitmap.size // 8))
            f.read(math.ceil(self.data_blocks_bitmap.size // 8))
            f.read(block_idx * FileSystem.DATA_BLOCK_SIZE)

            current_data = f.read(FileSystem.DATA_BLOCK_SIZE).rstrip(b'\x00')

        new_data = current_data + entry
        with open(self.file_name, 'r+b') as f:

            # offset
            f.read(self.superblock.get_size())
            f.read(FileSystem.INODES_NUMBER * self.inode_table[0].get_size())
            f.read(math.ceil(self.inode_bitmap.size // 8))
            f.read(math.ceil(self.data_blocks_bitmap.size // 8))
            f.read(block_idx * FileSystem.DATA_BLOCK_SIZE)

            f.write(new_data)

        # zwiększyć rozmiar directory (o zawartosć wpisu)
        self.superblock.increase_num_of_files()



    def read_from_directory(self, directory_inode_idx):
        directory_inode = self.inode_table[directory_inode_idx]
        block_idx = directory_inode.data_blocks_idx[0]

        with open(self.file_name, 'rb') as f:

            # offset
            f.read(self.superblock.get_size())
            f.read(FileSystem.INODES_NUMBER * self.inode_table[0].get_size())
            f.read(math.ceil(self.inode_bitmap.size // 8))
            f.read(math.ceil(self.data_blocks_bitmap.size // 8))
            f.read(block_idx * FileSystem.DATA_BLOCK_SIZE)

            self.data_blocks_table[block_idx].from_binary(f.read(FileSystem.DATA_BLOCK_SIZE))
            directory_data = self.data_blocks_table[block_idx].content
        entries = []
        for entry in directory_data.rstrip(b'\x00').split(b'\n'):
            entry = entry.strip()
            if entry:
                parts = entry.decode('utf-8').split(':')
                if len(parts) == 2:
                    entries.append(parts)
        print(entries)
        return entries


    def alocate_data_blocks(self, file_data):
        pass


if __name__ == "__main__":
    fs = FileSystem("/home/szczypawka/Nauka/Python/SOI/file_system/filesystem.bin")
    # fs.create_new()

    fs.load_old()
    fs.read_from_directory(1)
    fs.create_directory("rootek2")
    fs.read_from_directory(1)
    fs.superblock.info()
    fs.create_directory("home2")
    fs.read_from_directory(1)
    fs.superblock.info()
    fs.add_to_directory(2, "bejbe2")
    fs.add_to_directory(1, "bejbee2")
    fs.read_from_directory(1)
    fs.read_from_directory(2)
    fs.superblock.info()
    fs.save()

    pass

