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

    def create_new(self):
        with open(self.file_name, 'wb') as fs:
            fs.write(self.superblock.to_binary())

            for inode in self.inode_table:
                fs.write(inode.to_binary())

            fs.write(self.inode_bitmap.to_binary())

            for block in self.data_blocks_table:
                fs.write(block.to_binary())

            fs.write(self.data_blocks_bitmap.to_binary())

        self.superblock.info()
        self.inode_bitmap.info()
        self.data_blocks_bitmap.info()

    def load_old(self):
        with open(self.file_name, 'rb') as f:
            self.superblock.from_binary(f.read(self.superblock.get_size()))

            for inode in self.inode_table:
                inode.from_binary(f.read(inode.get_size()))

            self.inode_bitmap.from_binary(f.read(math.ceil(self.inode_bitmap.size // 8) ))

            for block in self.data_blocks_table:
                block.from_binary(f.read(block.size))

            self.data_blocks_bitmap.from_binary(f.read(math.ceil(self.data_blocks_bitmap.size // 8)))

        self.superblock.info()
        self.inode_bitmap.info()
        self.data_blocks_bitmap.info()
        # print(self.data_blocks_table[3].content)

#


if __name__ == "__main__":
    fs = FileSystem("/home/szczypawka/Nauka/Python/SOI/file_system/filesystem.bin")
    # fs.create_new()
    fs.load_old()

