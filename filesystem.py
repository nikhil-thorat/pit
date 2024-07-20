import os


class FileSystem:

    @staticmethod
    def create_directory(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    @staticmethod
    def write_file(file_path, content, mode="w", encoding="utf-8"):
        with open(file_path, mode, encoding=encoding) as f:
            return f.write(content)

    @staticmethod
    def read_file(file_path, mode="r", encoding="utf-8"):
        with open(file_path, mode, encoding=encoding) as f:
            return f.read()
