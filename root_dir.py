import os.path


def root_dir():
    """корневой путь программы"""
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    return ROOT_DIR
