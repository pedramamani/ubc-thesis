import os
import pathlib
import re

INFO_FILE_NAME = 'info.txt'
NOTES_FILE_NAME = 'notes.txt'


class Dataset:
    def __init__(self, folderPath: str):
        folderPath = str(folderPath)
        if not all([os.path.exists(folderPath), os.path.isdir(folderPath)]):
            raise Exception(f'Provided path "{folderPath}" does not exist or is not a folder.')

        infoFilePath = str(pathlib.Path(folderPath) / INFO_FILE_NAME)
        if not all([os.path.exists(infoFilePath), os.path.isfile(infoFilePath)]):
            raise Exception(f'Dataset folder must contain an "{INFO_FILE_NAME}" file.')
        self.fileNames = self._findFileNames(folderPath)
        self.info = self._parseInfoFile(infoFilePath)
        if len(self.fileNames) != len(self.info):
            raise Exception(f'Number of data files {len(self.fileNames)} does not match provided number {len(self.info)} in "{INFO_FILE_NAME}".')
        self._index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self._index += 1
        if self._index >= len(self.fileNames):
            self._index = -1
            raise StopIteration
        else:
            return self.fileNames[self._index], self.info[self._index]

    @staticmethod
    def _findFileNames(folderPath: str):
        fileNames = os.listdir(folderPath)
        fileNames.remove(INFO_FILE_NAME)
        if NOTES_FILE_NAME in fileNames:
            fileNames.remove(NOTES_FILE_NAME)

        match = re.match(r'([0-9]+)\.([a-z]+)$', fileNames[0])
        if (match is None) or (int(match.groups()[0]) != 0):
            raise Exception(f'File names must have "<number>.<extension>" format. Got unexpected "{fileNames[0]}".')
        extension = match.groups()[1]

        fileNumbers = []
        for index, fileName in enumerate(fileNames):
            match = re.match(rf'([0-9]+)\.{extension}$', fileName)
            if match is None:
                raise Exception(f'File names must have "<number>.<extension>" format. Got unexpected "{fileName}".')
            fileNumbers.append(int(match.groups()[0]))

        fileNumbers.sort()
        if fileNumbers != list(range(len(fileNumbers))):
            raise Exception(f'Files must be numbered in order of capture, starting at 0.')
        fileNames = [f'{n}.{extension}' for n in fileNumbers]
        return fileNames

    @staticmethod
    def _parseInfoFile(infoFilePath: str):
        with open(infoFilePath, 'r') as file:
            content = file.read()

        lines = content.splitlines()
        validLines = []
        for line in lines:
            if not (line.startswith('#') or line.strip() == ''):
                validLines.append(line)

        header = validLines.pop(0)
        names, types = [], []
        for heading in header.split():
            match = re.match(r'([a-zA-Z]+)(?:|\(([a-z]+)\))$', heading)
            if match is None:
                raise Exception(f'Heading "{heading}" in "{INFO_FILE_NAME}" has incorrect format.')
            name, type_ = match.groups()
            names.append(name)
            types.append(str if type_ is None else eval(type_))

        info = []
        for line in validLines:
            lineInfo = {}
            for column, value in enumerate(line.split()):
                name = names[column]
                if value == '.' and len(info) != 0:
                    lineInfo[name] = info[-1][name]
                elif value == '.':
                    raise Exception(f'First "{name}" is undefined.')
                elif value == '-':
                    lineInfo[name] = None
                else:
                    lineInfo[name] = types[column](value)
            info.append(lineInfo)
        return info
