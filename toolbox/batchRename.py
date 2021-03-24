import os
import pathlib

FILES_DIR = pathlib.Path('C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-03-10 OCS/notch')


def constructName(index, oldName):
    return str(index)


if __name__ == '__main__':
    fileNames = os.listdir(str(FILES_DIR))
    for i, fileName in enumerate(fileNames):
        if not (fileName.endswith('.txt') or fileName.endswith('.xls')):
            continue
        pieces = fileName.split('.')
        extension = pieces[-1]
        old_name = ''.join(pieces[:-1])
        newName = f'{constructName(i, old_name)}.{extension}'
        os.rename(str(FILES_DIR / fileName), str(FILES_DIR / newName))
