import os
import logging
logger = logging.getLogger(__name__)
IGNORES = ['Thumbs.db', '.DS_Store', '.IFO', '.VOB', '.VCD', '.BUP', '.rar', '.idx']

def exportToyaml(data, filePath):
    import yaml

    if os.path.isfile(filePath):
        os.remove(filePath)

    with open(filePath, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

    print('Dump complete to {}'.format(filePath))

def isRootFolderThere(rootFolder):
    """
    Method used to check if root folder is valid or not
    """
    if not os.path.isdir(rootFolder):
        print('No such root folder found.')
        return False
    else:
        return True

def fetchAllFiles(pathToRootFolder=''):
    files = []
    if isRootFolderThere(rootFolder=pathToRootFolder):
        for dirname, dirnames, filenames in os.walk(pathToRootFolder):
            filenames = [file for file in os.scandir(dirname) if file.is_file() and file.name not in IGNORES and os.path.splitext(file.name)[1] not in IGNORES]
            files.extend(filenames)
    return files

def searchForMatchingFileNames(rootFolder=""):
    print("Searching for matching fileNames in {}....".format(rootFolder))
    matching = {}

    allFiles = fetchAllFiles(rootFolder)
    allfilenames = [str(f.name) for f in allFiles]

    for fileName in allFiles:
        count = allfilenames.count(fileName.name)
        if count > 1:
            matching[fileName.path] = fileName.name
    print(matching)
    return matching

def searchForMatchingFileSizes(rootFolder=""):
    print("Searching for matching fileNames in {}....".format(rootFolder))
    matching = {}
    allFiles = fetchAllFiles(rootFolder)
    allfilenames = [(str(f.name), f.stat().st_size, f.path) for f in allFiles]

    for fileName, fileSize, filePath in allfilenames:
        for fileEntry in allFiles:
            if fileEntry.stat().st_size == fileSize and fileEntry.name != fileName:
                matching[filePath] = (fileSize, fileEntry.path, fileEntry.stat().st_size)
    return matching

############################################ FUNC CALLS
#exportToyaml(searchForMatchingFileNames(rootFolder="M:\\!MOVIES"), filePath="C:\\temp\\matchingFileName.yaml")
#exportToyaml(searchForMatchingFileSizes(rootFolder="M:\\!MOVIES"), filePath="C:\\temp\\matchingFileSize.yaml")
