import hashlib
import os
import zipfile

def get_sha1(file_path):
    buffer_size = 65536  # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def get_md5(file_path):
    buffer_size = 65536  # lets read stuff in 64kb chunks!
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def create_zip_file(source_dir, output_filename):
    # If current directory is needed in zip file
    # relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    relroot = os.path.abspath(source_dir)
    zipf = zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED, allowZip64=True)
    for root, dirs, files in os.walk(source_dir):
        # FIXME: removed this line, as not sure why it is necessary, and it was leaving weird directories with the name "." in the zip
        # add directory (needed for empty dirs)
        # zipf.write(root, os.path.relpath(root, relroot))
        for filename in files:
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath): # regular files only
                arcname = os.path.join(os.path.relpath(root, relroot), filename)
                zipf.write(filepath, arcname)
    zipf.close()