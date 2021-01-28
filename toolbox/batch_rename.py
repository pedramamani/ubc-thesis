import os
import pathlib

FILES_DIR = pathlib.Path('C:/Users/amani/PycharmProjects/courses/thesis/xfrog/xfrog_assets/run_2/4')


def construct_name(index, old_name):
    position = 175 + 0.2 * index
    new_name = f'{position:.2f}'.replace('.', '-')
    return new_name


if __name__ == '__main__':
    file_names = os.listdir(str(FILES_DIR))
    for i, file_name in enumerate(file_names):
        pieces = file_name.split('.')
        extension = pieces[-1]
        old_name = ''.join(pieces[:-1])
        new_name = f'{construct_name(i, old_name)}.{extension}'
        os.rename(str(FILES_DIR / file_name), str(FILES_DIR / new_name))
