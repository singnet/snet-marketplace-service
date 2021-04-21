import shutil
import zipfile


def zip_file(source_path, destination_path):
    with zipfile.ZipFile(source_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path)


def unzip_file(destination, source):
    shutil.make_archive(destination, 'zip', source)
