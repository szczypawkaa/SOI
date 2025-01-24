from file_system import FileSystem

if __name__ == "__main__":
    fs = FileSystem("./f_s/filesystem.bin")
    # fs.create_new()

    fs.load_old()
    fs.ls()
    fs.pwd()
    fs.directory_info()
    # fs.create_directory("first")
    fs.cd("first")
    fs.directory_info()
    # fs.add_file("inner_file.txt", "Witam z głębin")
    fs.cd("~")
    fs.directory_info()
    # fs.remove_n_bytes_from_file("inner_file.txt", 100)
    # fs.copy_file_to_otside_system("inner_file.txt")
