import shutil
import zipfile


def unzip_file(source_path, destination_path):
    with zipfile.ZipFile(source_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path)


def zip_file(destination, source):
    shutil.make_archive(destination, 'zip', source)
