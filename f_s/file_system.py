from components import Superblock, Inode, Bitmap, DataBlock
import math
import copy


class FileSystem:
    FILE_SYSTEM_SIZE = 100 * 1024 * 1024  # 100 MB
    INODES_NUMBER = 512
    DATA_BLOCK_SIZE = 4 * 1024  # 4KB
    DATA_BLOCKS_NUMBER = FILE_SYSTEM_SIZE // DATA_BLOCK_SIZE  # 25 * 1024
    MAX_FILE_SIZE = 200 * 1024  # 200 KB
    MAX_BLOCKS = MAX_FILE_SIZE // DATA_BLOCK_SIZE  # 25 -
    # maksymalna ilość bloków które mogą być przypisane do jedngo i-node

    def __init__(self, file_name):
        self.file_name = file_name
        self.superblock = Superblock(FileSystem.FILE_SYSTEM_SIZE)
        self.inode_table = [
            Inode(FileSystem.MAX_BLOCKS)
            for _ in range(FileSystem.INODES_NUMBER)
            ]
        self.inode_bitmap = Bitmap(FileSystem.INODES_NUMBER)
        self.data_blocks_table = [
            DataBlock(FileSystem.DATA_BLOCK_SIZE)
            for _ in range(FileSystem.DATA_BLOCKS_NUMBER)
            ]
        self.data_blocks_bitmap = Bitmap(FileSystem.DATA_BLOCKS_NUMBER)

        self._current_directiory_name = "root"
        self._current_directiory_idx = 1
        self._root_dir_idx = 1

    def save(self):
        with open(self.file_name, 'wb') as fs:
            fs.write(self.superblock.to_binary())

            for inode in self.inode_table:
                fs.write(inode.to_binary())

            fs.write(self.inode_bitmap.to_binary())
            fs.write(self.data_blocks_bitmap.to_binary())

            for block in self.data_blocks_table:
                fs.write(block.to_binary())

    def create_new(self):
        self.create_root_dir()
        self.superblock.decrease_free_space(
            self._calculate_constant_allocated()
            )
        self.save()

    def load_old(self):
        with open(self.file_name, 'rb') as f:
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

    def create_root_dir(self):
        # inode 0 w bitmapach są permamentnie zablokowane, ponieważ wolną przestrzeń
        # dopełniam zerami, które potem są usuwane
        self.inode_bitmap.take_idx(0)
        self.data_blocks_bitmap.take_idx(0)
        self._create_directory("root")

    def _create_directory(self, dir_name):
        inode_idx = self.inode_bitmap.find_free_inode_idx()
        data_block_idx = self.data_blocks_bitmap.find_free_inode_idx()

        self.inode_bitmap.take_idx(inode_idx)
        self.data_blocks_bitmap.take_idx(data_block_idx)

        dir_inode = self.inode_table[inode_idx]
        dir_inode.create_directory()
        dir_inode.add_data_block_idx(data_block_idx)

        return inode_idx

    def create_directory(self, dir_name):
        inode_idx = self._create_directory(dir_name)
        self.add_to_directory(dir_name, inode_idx)
        self.save()

    def remove_file(self, file_name, parent_inode_idx=1):
        # parent_inode to informacja z jakiego dir usuwamy
        parent_inode = self.inode_table[parent_inode_idx]
        block_idx = parent_inode.data_blocks_idx[0] # dir ma jeden blok

        directory_data = self.data_blocks_table[block_idx].content

        new_data = ""
        deleted_inode_idx = 0
        for entry in directory_data.rstrip(b'\x00').split(b'\n'):
            entry = entry.strip()
            if entry:
                parts = entry.decode('utf-8').split(':')
                if parts[0] != file_name and len(parts) == 2:
                    new_data += f"{parts[0]}:{parts[1]}\n"
                if parts[0] == file_name:
                    deleted_inode_idx = int(parts[1])

        if deleted_inode_idx == 0:
            raise ValueError("Brak inode idx")

        # zmiana w datablock
        self.data_blocks_table[block_idx].new_content(new_data)
        inode_to_del = self.inode_table[deleted_inode_idx]

        if inode_to_del.hard_links_counter == 0:
            self.inode_bitmap.realease_idx(deleted_inode_idx)
            all_blocks_idx = inode_to_del.data_blocks_idx
            inode_to_del.data_blocks_idx = []
            for block_idx in all_blocks_idx:
                self.data_blocks_bitmap.realease_idx(block_idx)
            self.data_blocks_bitmap.realease_idx(deleted_inode_idx)
        else:
            inode_to_del.hard_links_counter -= 1

        self.superblock.decrease_num_of_files()
        self.superblock.decrease_free_space(inode_to_del.size)
        self.save()

    def add_file(self, file_name, file_data, dir_name=None):
        if dir_name is None:
            dir_name = self._current_directiory_name

        inode_idx = self.inode_bitmap.find_free_inode_idx()
        self.inode_bitmap.take_idx(inode_idx)
        file_inode = self.inode_table[inode_idx]
        allocated_blocks = self._alocate_data_blocks(file_data)

        file_inode.data_blocks_idx = allocated_blocks
        file_inode.size = len(file_data)
        self.superblock.decrease_free_space(file_inode.size)

        self.add_to_directory(file_name, inode_idx)
        self.save()


    def _alocate_data_blocks(self, file_data, blocks_indexes=None):
        blocks_needed = (len(file_data) + FileSystem.DATA_BLOCK_SIZE - 1) // FileSystem.DATA_BLOCK_SIZE  # Zaokrąglenie w górę

        if blocks_indexes is None:
            blocks_indexes = []
            for _ in range(blocks_needed):
                block_index = self.data_blocks_bitmap.find_free_inode_idx()

                if block_index == -1:
                    raise Exception("Brak dostępnych bloków danych")
                blocks_indexes.append(block_index)
                self.data_blocks_bitmap.take_idx(block_index)

        if len(blocks_indexes) < blocks_needed:
            blocks_indexes_copy = copy.deepcopy(blocks_indexes)
            for _ in range(blocks_needed - len(blocks_indexes)):
                block_index = self.data_blocks_bitmap.find_free_inode_idx()
                if block_index == -1:
                    raise Exception("Brak dostępnych bloków danych")
                self.data_blocks_bitmap.take_idx(block_index)
                blocks_indexes_copy.append(block_index)
            blocks_indexes = blocks_indexes_copy

        for i, block_index in enumerate(blocks_indexes):
            data_chunk = file_data[i * FileSystem.DATA_BLOCK_SIZE: (i + 1) * FileSystem.DATA_BLOCK_SIZE]
            self.data_blocks_table[block_index].new_content(data_chunk)

        return blocks_indexes

    def add_to_directory(self, filename, file_inode_idx=None):
        # dodaje do aktualnego katalogu

        if file_inode_idx is None:
            file_inode_idx = self.inode_bitmap.find_free_inode_idx()

        dir_inode_idx = self._current_directiory_idx
        all_block_idx = self.inode_table[dir_inode_idx].data_blocks_idx
        entry = f'{filename}:{file_inode_idx}\n'

        current_data = self._read_file_content(dir_inode_idx)
        new_data = current_data + entry

        # to jest katalog, a więc miał już wcześniej przypisany blok danych
        self._alocate_data_blocks(new_data, all_block_idx)

        self.superblock.increase_num_of_files()
        self.superblock.decrease_free_space(len(entry.encode('utf-8')))
        self.inode_table[dir_inode_idx].size += len(entry.encode('utf-8'))

    def _read_file_content(self, inode_idx) -> str:
        all_block_idx = self.inode_table[inode_idx].data_blocks_idx

        current_data = ''
        for block_idx in all_block_idx:
            block_data = self.data_blocks_table[block_idx].content
            current_data += block_data.rstrip(b'\x00').decode('utf-8')

        return current_data

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
        return entries

    def _find_file_idx_by_name(self, file_name, directory_idx=None):
        if directory_idx is None:
            directory_idx = self._current_directiory_idx

        entries = self.read_from_directory(directory_idx)
        for name, idx in entries:
            if name == file_name:
                return int(idx)

        raise ValueError("Nie ma takiego pliku w katologu")

    def pwd(self):
        print(f"Working directory: {self._current_directiory_name}")

    def cd(self, path):
        # aktualnie obsługuje tylko wchodzenie do następnych katalogów,
        # aby cofnąć się do root służy ~

        if path == "~":
            self._current_directiory_idx = self._root_dir_idx
            self._current_directiory_name = "root"
            return

        path_elements = path.split("/")
        dir_name = path_elements[0]

        dir_idx = self._find_file_idx_by_name(dir_name)
        if dir_idx:
            self._current_directiory_idx = dir_idx
            self._current_directiory_name = dir_name

        if len(path_elements) >= 2:
            path = "/".join(path_elements[1:])
            self.cd(path)

    def ls(self):
        entries = self.read_from_directory(self._current_directiory_idx)
        if entries:
            file_names = [x[0] for x in entries]
            print(file_names)
        else:
            raise ValueError("Nie ma takiego pliku w katalogu")

    def copy_file_to_otside_system(self, file_name):
        outside_path = f"./f_s/{file_name}"

        inode_idx = self._find_file_idx_by_name(file_name)
        inode = self.inode_table[inode_idx]
        data_blocks_idx = inode.data_blocks_idx
        with open(outside_path, 'wb') as f:
            for block_idx in data_blocks_idx:
                block = self.data_blocks_table[block_idx]
                f.write(block.content.rstrip(b'\x00'))

    def create_hardlink(self, base_file, copy_file):
        base_file_idx = self._find_file_idx_by_name(base_file)
        self.add_to_directory(copy_file, base_file_idx)

        base_inode = self.inode_table[self._current_directiory_idx]
        base_inode.hard_links_counter += 1

        self.save()

    def add_n_bytes_to_file(self, file_name, n):
        file_idx = self._find_file_idx_by_name(file_name)
        file_inode = self.inode_table[file_idx]
        all_block_idx = file_inode.data_blocks_idx

        current_data = self._read_file_content(file_idx)
        extended_data = current_data + 'm' * n

        extendend_file_blocks = self._alocate_data_blocks(extended_data, all_block_idx)

        new_data_blocks = [x for x in extendend_file_blocks if x not in all_block_idx]
        if new_data_blocks:
            for new_db in new_data_blocks:
                file_inode.data_blocks_idx.append(new_db)
        file_inode.size += n

        self.superblock.decrease_free_space(n)
        self.save()

    def remove_n_bytes_from_file(self, file_name, n):
        file_idx = self._find_file_idx_by_name(file_name)
        file_inode = self.inode_table[file_idx]
        all_block_idx = file_inode.data_blocks_idx

        current_data = self._read_file_content(file_idx)
        end = len(current_data) - n
        reduced_data = current_data[:end]

        reduced_file_blocks = self._alocate_data_blocks(reduced_data, all_block_idx)

        new_data_blocks = [x for x in reduced_file_blocks if x not in all_block_idx]
        if new_data_blocks:
            for new_db in new_data_blocks:
                file_inode.data_blocks_idx.append(new_db)

        file_inode.size -= n

        self.superblock.increase_free_space(n)
        self.save()

    def directory_info(self, dir_name=None):
        if dir_name is None:
            inode_idx = self._current_directiory_idx
        else:
            inode_idx = self._find_file_idx_by_name(dir_name)
        self._directory_info(inode_idx)

    def _calculate_constant_allocated(self):
        return (
            (self.superblock.get_size()) +
            FileSystem.INODES_NUMBER * self.inode_table[0].get_size() +
            (self.inode_bitmap.size // 8) +
            (self.data_blocks_bitmap.size // 8)
        )

    def _directory_info(self, directory_inode_index=0):
        directory_inode = self.inode_table[directory_inode_index]
        if not directory_inode.is_directory:
            raise Exception("Nieprawiłowy inode - nie ma takiego katalogu")

        total_size = 0
        total_size_with_subdirs = 0

        total_size_with_subdirs = self._calculate_directory_size(directory_inode_index)

        for entry in self.read_from_directory(directory_inode_index):
            name, inode_index = entry
            inode_index = int(inode_index)
            inode = self.inode_table[inode_index]
            if not inode.is_directory:
                total_size += inode.size

        free_space = self.superblock.free_space

        print(f"Folder size (without subfolders): {total_size / 1024:.2f} KB")
        print(f"Folder size (including subfolders): {total_size_with_subdirs / 1024:.2f} KB")
        print(f"Free space on the virtual disk: {free_space / 1024 ** 2:.2f} MB")

    def _calculate_directory_size(self, inode_index):
        total_size = 0

        inode = self.inode_table[inode_index]
        if inode.is_directory:
            for entry in self.read_from_directory(inode_index):
                name, entry_inode_index = entry
                entry_inode_index = int(entry_inode_index)
                total_size += self._calculate_directory_size(entry_inode_index)
        else:
            total_size += inode.size

        return total_size

