from os import getenv as env, path
from typing import Tuple, Optional

from . import security, spaces


def create_encrypted_file(filename: str, content: str, folder: str = "code") -> Tuple[str, bool]:
    """
    Creates a file in the filesystem if in dev, or in a digitalocean block volume if in prod

    :param filename: Name of the file (no extension needed)
    :param content: Content to put in the file (is encrypted)
    :param folder: Folder to put in in
    :return: Returns a tuple with the first element being the path and the second tells if the file was created locally
    or not
    """
    filename = filename + ".encrypted"
    if env("FLASK_ENV", "") == "development":
        pathname = path.join(path.abspath(path.dirname(__file__)), "..", "static", folder, filename)
        with open(pathname, "wb") as f:
            f.write(security.enc(content).encode())
        return pathname, True
    else:
        pathname = path.join(folder, filename)
        spaces.upload_file_from_string(security.enc(content), pathname)
        return pathname, False


def get_encrypted_file_contents(filename: str, folder: str = "code", local: bool = True) -> Optional[str]:
    if filename.split(".")[-1] != "encrypted":
        filename += ".encrypted"
    if local:
        pathname = path.join(path.abspath(path.dirname(__file__)), "..", "static", folder, filename)
        try:
            with open(pathname, "rb") as f:
                return security.dec(f.read().decode())
        except FileNotFoundError:
            return None
    else:
        pathname = path.join(folder, filename)
        try:
            return security.dec(spaces.get_file_contents(pathname).decode())
        except Exception as e:
            print(e)
            return None
