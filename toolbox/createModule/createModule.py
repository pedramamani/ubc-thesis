from pathlib import Path
import os
import re

DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = DIR / 'assets'

nameCamel = None
namePascal = None


def createModule(name, creationDir, createMain=False):
    global nameCamel, namePascal
    nameCamel = name
    namePascal = name[0].capitalize() + name[1:]
    moduleDir = Path(creationDir) / nameCamel

    assert re.match(r'^[a-z]+([A-Z][a-z]*)*$', name), f'Module name "{name}" does not follow camelCase'
    assert os.path.exists(creationDir), f'Creation directory "{creationDir}" does not exist'
    assert not os.path.exists(moduleDir), 'Module directory "{moduleDir}" already exists'

    os.mkdir(moduleDir)
    os.mkdir(moduleDir / 'assets')
    createModuleFile(moduleDir, '__init__.py')
    createModuleFile(moduleDir, '{}.py')
    if createMain:
        createModuleFile(moduleDir, '__main__.py')


def createModuleFile(moduleDir, fileNameFormat):
    moduleFilePath = str(moduleDir / fileNameFormat.format(nameCamel))
    templateFilePath = ASSETS_DIR / fileNameFormat.format('template')
    with open(moduleFilePath, 'w') as file:
        content = generateFromTemplate(templateFilePath)
        file.write(content)


def generateFromTemplate(filePath):
    content = filePath.read_text()
    content = content.replace('template', nameCamel)
    content = content.replace('Template', namePascal)
    return content
