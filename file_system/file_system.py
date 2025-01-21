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

        self._current_directiory_idx = 1  #root
        self._current_directiory_name = "root"
        # self._data_blocks_offset = self._datablocks_offset()

    def _data_block_offset(self, block_idx):
        superblock_size = self.superblock.get_size()
        inode_table_size = FileSystem.INODES_NUMBER * self.inode_table[0].get_size()
        inode_bitmap_size = math.ceil(self.inode_bitmap.size / 8)
        data_blocks_bitmap_size = math.ceil(self.data_blocks_bitmap.size / 8)

        # przechodzę przez kolejne bloki danych, aż będę przed odpowiednim
        blocks = block_idx * FileSystem.DATA_BLOCK_SIZE

        total_offset = (
            superblock_size +
            inode_table_size +
            inode_bitmap_size +
            data_blocks_bitmap_size +
            blocks
        )

        return total_offset

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
            # self.superblock.from_binary(f.read(self.superblock.get_size()))
            data = f.read(self.superblock.get_size())
            print(f'Wczytano {len(data)} bajtów dla superblock')
            self.superblock.from_binary(data)

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
        self.add_to_directory(parent_inode_idx, dir_name, inode_idx)

    def remove_directory(self, dir_name, parent_inode_idx=1):
        parent_inode = self.inode_table[parent_inode_idx]
        block_idx = parent_inode.data_blocks_idx[0]

        directory_data = self.data_blocks_table[block_idx].content

        new_data = ""
        deleted_idx = 0
        for entry in directory_data.rstrip(b'\x00').split(b'\n'):
            entry = entry.strip()
            if entry:
                parts = entry.decode('utf-8').split(':')
                if parts[0] != dir_name and len(parts) == 2:
                    new_data += f"{parts[0]}:{parts[1]}\n"
                if parts[0] == dir_name:
                    deleted_idx = int(parts[1])

        # zmiana w datablock
        self.data_blocks_table[block_idx].new_content(new_data)
        print(self.data_blocks_table[block_idx].content)


        # self.inode_table[] -> trzeba zwolnić
        self.inode_bitmap.realease_idx(deleted_idx)
        self.inode_table[deleted_idx].data_blocks_idx = []
        self.data_blocks_bitmap.realease_idx(deleted_idx)

        # zmniejszyć rozmiar directory (o zawartosć wpisu)
        self.superblock.decrease_num_of_files()

    def add_file(self, file_name, file_data, dir_name=None):
        if dir_name is None:
            dir_name = self._current_directiory_name

        # parent_inode_idx = self._find_file_idx_by_name(dir_name)
        parent_inode_idx = self._current_directiory_idx

        inode_idx = self.inode_bitmap.find_free_inode_idx()
        data_block_idx = self.data_blocks_bitmap.find_free_inode_idx()
        # zajęcie inode
        self.inode_bitmap.take_idx(inode_idx)

        # dane dla inoda:
        # dir_inode = self.inode_table[inode_idx]
        # dir_inode.create_directory()
        file_inode = self.inode_table[inode_idx]

        # zajęcie bloku danych
        self.data_blocks_bitmap.take_idx(data_block_idx)
        file_inode.data_blocks_idx.append(data_block_idx)

        # dodanie do bloku danych treści
        file_data_block = self.data_blocks_table[data_block_idx]
        file_data_block.new_content(file_data)

        # zwiększenie ilości plików w superbloku
        self.add_to_directory(parent_inode_idx, file_name, inode_idx)


    def add_to_directory(self, dir_inode_idx, filename, file_inode_idx=None):
        if file_inode_idx is None:
            file_inode_idx = self.inode_bitmap.find_free_inode_idx()
        # znależć lub stworzyć datablock przyisany do dir_inode
        entry = f"{filename}:{file_inode_idx}\n"
        # znaleźć wolne miejsce w data block i dopisać
        block_idx = self.inode_table[dir_inode_idx].data_blocks_idx[0]

        current_data = self.data_blocks_table[block_idx].content
        current_data = current_data.rstrip(b'\x00').decode('utf-8')
        new_data = current_data + entry

        self.data_blocks_table[block_idx].new_content(new_data)

        # zwiększyć rozmiar directory (o zawartosć wpisu)
        self.superblock.increase_num_of_files()

    def read_from_directory(self, directory_inode_idx):
        directory_inode = self.inode_table[directory_inode_idx]
        block_idx = directory_inode.data_blocks_idx[0]
        directory_data = self.data_blocks_table[block_idx].content

        entries = []
        for entry in directory_data.rstrip(b'\x00').split(b'\n'):
            entry = entry.strip()
            if entry:
                parts = entry.decode('utf-8').split(':')
                if len(parts) == 2:
                    entries.append(parts)
        # print(entries)
        return entries

    def _find_file_idx_by_name(self, file_name, directory_idx=None):
        if directory_idx is None:
            directory_idx = self._current_directiory_idx
        entries = self.read_from_directory(directory_idx)
        for name, idx in entries:
            if name == file_name:
                return int(idx)

        self.pwd()
        raise ValueError("Nie ma takiego pliku w katologu")

    def pwd(self):
        print(f"Working direcotry: {self._current_directiory_name}")

    def cd(self, dir_name):
        dir_idx = self._find_file_idx_by_name(dir_name)
        if dir_idx:
            self._current_directiory_idx = dir_idx
            self._current_directiory_name = dir_name
            self.pwd()

    def ls(self):
        entries = self.read_from_directory(self._current_directiory_idx)
        if entries:
            file_names = [x[0] for x in entries]
            print(file_names)
        else:
            print("empty")

    def alocate_data_blocks(self, file_data):
        pass

    def copy_file_to_otside_system(self, file_name):
        outside_path = f"/home/szczypawka/Nauka/Python/SOI/file_system/{file_name}"
        inode_idx = self._find_file_idx_by_name(file_name)
        inode = self.inode_table[inode_idx]
        data_blocks_idx = inode.data_blocks_idx
        with open(outside_path, 'wb') as f:
            # znależć file_idx
            # znaleźć data_block idx
            # znaleźć datablock z i wpisać tu
            for block_idx in data_blocks_idx:
                block = self.data_blocks_table[block_idx]

                f.write(block.content.rstrip(b'\x00'))


if __name__ == "__main__":
    fs = FileSystem("/home/szczypawka/Nauka/Python/SOI/file_system/filesystem.bin")
    # fs.create_new()

    fs.load_old()
    fs.pwd()
    fs.ls()
    # fs.add_file("heloł.txt", "Witam was wszystkich")
    # fs.create_directory("rootek5")
    # fs.create_directory("rootek2")
    # fs.remove_directory("rootek1")
    # fs.pwd()
    fs.ls()
    fs.copy_file_to_otside_system("heloł.txt")
    # fs.read_from_directory(1)
    # fs.superblock.info()
    # fs.create_directory("home2")
    # fs.read_from_directory(1)
    # fs.superblock.info()
    # fs.add_to_directory(2, "bejbe2")
    # fs.add_to_directory(1, "bejbee2")
    # fs.read_from_directory(1)
    # fs.read_from_directory(2)
    # fs.superblock.info()
    # fs.remove_directory("home2")
    # fs.read_from_directory(1)

    fs.save()

    pass

