import struct


class FileSystem:
    def __init__(self, file_name):
        self.file_name = file_name
        self.num = 1
        self.date = 'today'
        self.author = 'Olusiaaaa'

    # def create(self):
    #     with open(self.file_name, 'wb') as fs:

    def to_binary(self):
        date_bytes = self.date.ljust(20, '\x00').encode('utf-8')  # Dopełniamy do 20 znaków
        author_bytes = self.author.ljust(20, '\x00').encode('utf-8')  # Dopełniamy do 20 znaków

        return struct.pack(
            'I20s20s',
            self.num,
            date_bytes,
            author_bytes
        )

    # @staticmethod
    def from_binary(self, data):
        num, date, author = struct.unpack('I20s20s', data)
        date = date.decode('utf-8').strip('\x00')
        author = author.decode('utf-8').strip('\x00')
        return num, date, author

    def create(self):
        with open('file_name', 'wb') as fs:
            bin_data = self.to_binary()
            fs.write(bin_data)

    def read(self, file_name):
        with open(file_name, 'rb') as fs:
            data = fs.read()

        return self.from_binary(data)


if __name__ == "__main__":
    fs = FileSystem("file_system")
    # bin_data = fs.to_binary()
    # print(bin_data)
    # read_data = fs.from_binary(bin_data)
    # print(read_data)

    fs.create()
    print(fs.read("file_name"))