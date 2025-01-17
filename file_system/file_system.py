import struct
from components import Superblock, Inode, Bitmap, DataBlock
from typing import List


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
        self.inode_bitmap = None
        self.data_blocks_bitmap = None
        self.data_blocks: List(DataBlock) = []

    def create_new(self):
        with open(self.file_name, 'wb') as fs:
            fs.write(self.superblock.to_binary())
            for inode in self.inode_table:
                fs.write(inode.to_binary())
        self.superblock.info()

    def load_old(self):
        with open(self.file_name, 'rb') as f:
            self.superblock.from_binary(f.read(self.superblock.get_size()))
            for inode in self.inode_table:
                inode.from_binary(f.read(inode.get_size()))

        self.superblock.info()

#


if __name__ == "__main__":
    fs = FileSystem("/home/szczypawka/Nauka/Python/SOI/file_system/filesystem.bin")
    # fs.create_new()
    fs.load_old()
    # fs.superblock.increase_num_of_files()
    # fs.superblock.info()
    # fs.superblock.decrease_num_of_files()
    # fs.superblock.info()
