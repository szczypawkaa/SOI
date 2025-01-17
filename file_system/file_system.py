import struct
from components import Superblock, Inode, Bitmap, DataBlock
from typing import List


class FileSystem:
    FILE_SYSTEM_SIZE = 100 * 1024 * 1024  # 100 MB
    INODES_NUMBER = 1024
    DATA_BLOCK_SIZE = 2 * 1024  # 2KB
    DATA_BLOCKS_NUMBER = FILE_SYSTEM_SIZE // DATA_BLOCK_SIZE  # 50 * 1024

    def __init__(self, file_name):
        self.file_name = file_name
        self.superblock = Superblock(FileSystem.FILE_SYSTEM_SIZE)
        self.inode_table = None
        self.inode_bitmap = None
        self.data_blocks_bitmap = None
        self.data_blocks: List(DataBlock) = []

    def create_new(self):
        with open(self.file_name, 'wb') as fs:
            fs.write(self.superblock.to_binary())
        self.superblock.info()

    def load_old(self):
        with open(self.file_name, 'rb') as fs:
            self.superblock.from_binary(fs.read(self.superblock.size()))
        self.superblock.info()
        # self.num_of_files = num_of_files
        # self.last_modified = last_mod.decode('utf-8').strip('\x00')
        # self.free_space = free_space


#


if __name__ == "__main__":
    fs = FileSystem("/home/szczypawka/Nauka/Python/SOI/file_system/filesystem.bin")
    # fs.create_new()
    fs.load_old()
