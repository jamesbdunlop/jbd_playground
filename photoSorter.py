import os, shutil, filecmp, time, logging, EXIF, sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
logger = logging.getLogger(__name__)
IGNORES = ['Thumbs.db', '.DS_Store', '.IFO', '.VOB', '.VCD', '.BUP', '.rar', '.idx']

def isRootFolderThere(rootFolder):
    """
    Method used to check if root folder is valid or not
    """
    if not os.path.isdir(rootFolder):
        print('No such root folder found.')
        return False
    else:
        return True

def fetchFiles(pathToRootFolder = ''):
    files = []
    if isRootFolderThere(rootFolder = pathToRootFolder):
        for dirname, dirnames, filenames in os.walk(pathToRootFolder):
            filenames = [file for file in os.scandir(dirname) if file.is_file() and file.name not in IGNORES and os.path.splitext(file.name)[1] not in IGNORES]
            files.extend(filenames)
    return files

def copyToTypeFolders(destination = "", paths = [], copy = True):
    ## Build base directories based off fileTypes
    for eachPath in paths:
        files = fetchFiles(eachPath)
        for eachFile in files:
            ## Build a path based on ext types for transferring into
            ext =  os.path.splitext(eachFile.name)[1].replace(".", "")

            extDirPath = "{0}\\{1}".format(destination, ext)
            if not os.path.isdir(extDirPath):
                os.mkdir(extDirPath)

            destPath = '{0}\\{1}'.format(extDirPath, eachFile.name)
            if os.path.isfile(destPath):
                extDirPath = "{0}\\{1}\\nameclash01".format(destination, ext)
                destPath = '{0}\\{1}'.format(extDirPath, eachFile.name)
                if not os.path.isdir(extDirPath):
                    os.mkdir(extDirPath)

                if os.path.isfile(destPath):
                    extDirPath = "{0}\\{1}\\nameclash02".format(destination, ext)
                    destPath = '{0}\\{1}'.format(extDirPath, eachFile.name)
                    if not os.path.isdir(extDirPath):
                        os.mkdir(extDirPath)
                    if not os.path.isfile(destPath):
                        if copy:
                            print("Copying {0} to {1}" .format(eachFile.path, destPath))
                            shutil.copy(eachFile.path, destPath)
                        else:
                            print("Moving {0} to {1}" .format(eachFile.path, destPath))
                            shutil.move(eachFile.path, destPath)
                    else:
                        print('CANT MOVE %s' % eachFile.path)
                else:
                    if copy:
                        print("Copying {0} to {1}" .format(eachFile.path, destPath))
                        shutil.copy(eachFile.path, destPath)
                    else:
                        print("Moving {0} to {1}" .format(eachFile.path, destPath))
                        shutil.move(eachFile.path, destPath)
            else:
                if copy:
                    print("Copying {0} to {1}" .format(eachFile.path, destPath))
                    shutil.copy(eachFile.path, destPath)
                else:
                    print("Moving {0} to {1}" .format(eachFile.path, destPath))
                    shutil.move(eachFile.path, destPath)
        print("FINISHED FILE TRANSFERS")

def getDateTaken(filePath):
    try:
        with open(filePath, 'rb') as fh:
            tags = EXIF.process_file(fh, stop_tag="EXIF DateTimeOriginal")
            try:
                dateTaken = tags["EXIF DateTimeOriginal"].values
            except:
                dateTaken = None
    except:
        print("WARNING cannot process %s" % filePath)
        dateTaken = None
    return dateTaken

def searchForMatchingFiles(rootFolder = "", checkname = True, checksize = True, imagesOnly = False):
    allFiles        = fetchFiles(rootFolder)
    searchResults   = {} ## Will populate with filenames as we go through the files
    for dirname, dirs, files in os.walk(rootFolder):
        searchResults[dirname] = {}
        files = [file for file in os.scandir(dirname) if file.is_file() and file.name not in IGNORES and os.path.splitext(file.name)[1] not in IGNORES]
        for eachFile in files:
            if eachFile.name not in searchResults[dirname].keys():
                searchResults[dirname][eachFile.name] = {
                                                         'nameMatches': [],
                                                         'sizeMatches': []
                                                         }
                for eachItr in allFiles:
                    if checkname:
                        if dirname not in eachItr.path and eachFile.name == eachItr.name:
                            if eachItr.path not in searchResults[dirname][eachFile.name]['nameMatches']:
                                searchResults[dirname][eachFile.name]['nameMatches'] = [eachItr.path]
                            else:
                                searchResults[dirname][eachFile.name]['nameMatches'].extend([eachItr.path])

                    if checksize:
                        if eachFile.path != eachItr.path:
                            if eachFile.stat().st_size == eachItr.stat().st_size:
                                if imagesOnly:
                                    origDate = getDateTaken(eachFile.path)
                                    itrDate = getDateTaken(eachItr.path)
                                else:
                                    origDate = eachFile.stat().st_mtime
                                    itrDate = eachItr.stat().st_mtime

                                if origDate and itrDate:
                                    if origDate == itrDate:
                                        if eachItr.path not in searchResults[dirname][eachFile.name]['sizeMatches'] and eachItr.path not in searchResults[dirname][eachFile.name]['nameMatches']:
                                            searchResults[dirname][eachFile.name]['sizeMatches'] = [eachItr.path]
                                        elif eachItr.path not in searchResults[dirname][eachFile.name]['nameMatches']:
                                            searchResults[dirname][eachFile.name]['sizeMatches'].extend([eachItr.path])
                                        else:
                                            pass
    return searchResults

def doDupCheck(paths = [], imagesOnly = False, move = False, checkname = True, checksize = True):
    for eachFilePath in paths:
        print("################# SCANNING FOR DUPLICATES IN %s" % eachFilePath)
        startTime = time.time()
        results = searchForMatchingFiles(rootFolder = eachFilePath, checkname = checkname, checksize = checksize, imagesOnly = imagesOnly)

        exportToyaml(results)

        for eachDir, dirData in results.items():
            baseFilesNames = []
            print("#####################################################################################################\n{0}".format(eachDir))
            for eachFileName, fileData in dirData.items():
                baseFilesNames.extend([eachFileName])

                if fileData['nameMatches'] or fileData['sizeMatches']:
                    if move:
                        if not os.path.isdir("{0}\\duplicates".format(eachDir)):
                            os.mkdir("{0}\\duplicates".format(eachDir))

                    if fileData['nameMatches']:
                        for eachFile in fileData['nameMatches']:
                            print("### DUP NAMES FOUND for %s:" % eachFileName)
                            print("\t{}".format(eachFile))
                            if move:
                                try:
                                    shutil.move(eachFile, "{0}\\duplicates".format(eachDir))
                                    print('Moved {0} to {1}'.format(eachFile, "%s\\duplicates" % eachDir))
                                except:
                                    pass

                    if fileData['sizeMatches']:
                        for eachFile in fileData['sizeMatches']:
                            if eachFile.split(os.sep)[-1] not in baseFilesNames:
                                print("### DUP SIZES FOUND for %s:" % eachFileName)
                                print("\t{}".format(eachFile))
                                if move:
                                    try:
                                        shutil.move(eachFile, "{0}\\duplicates".format(eachDir))
                                        print('Moved {0} to {1}'.format(eachFile, "%s\\duplicates" % eachDir))
                                    except:
                                        pass
            print("#####################################################################################################")
        print('Search Finished... time taken: %02d seconds' % (time.time() - startTime))

def buildDateFolders(path = "", destination='', copy = True):
    files = fetchFiles(path)
    print("Processing files into dated folders for {0}".format(path))
    for eachFile in files:
        with open(eachFile.path, 'rb') as fh:
            tags = EXIF.process_file(fh, stop_tag="EXIF DateTimeOriginal")
            try:
                dateTaken = tags["EXIF DateTimeOriginal"].values
            except:
                dateTaken = None
        if dateTaken:
            try:
                destYearDir = "{0}\\{1}".format(destination, dateTaken.split(":")[0])
                destMonthDir = '{0}\\{1}'.format(destYearDir, dateTaken.split(":")[1])
                destMonthDay = '{0}\\{1}'.format(destMonthDir, dateTaken.split(":")[2].split(" ")[0])
                if not os.path.isdir(destYearDir):
                    os.mkdir(destYearDir)
                if not os.path.isdir(destMonthDir):
                    os.mkdir(destMonthDir)
                if not os.path.isdir(destMonthDay):
                    os.mkdir(destMonthDay)

                if copy:
                    if not os.path.isfile(os.path.join(eachFile.name, destMonthDay)):
                        print("Copying %s" % eachFile.name)
                        shutil.copy(eachFile.path, destMonthDay)
                else:
                    if not os.path.isfile(os.path.join(eachFile.name, destMonthDay)):
                        print("Moving %s from %s to %s" % (eachFile.name, eachFile.path, destMonthDay))
                        shutil.move(eachFile.path, destMonthDay)
            except:
                pass
    print('FINISHED MOVING FILES TO DATE FOLDERS')

############################################ FUNC CALLS
## Step one is to process the files from a HD into a fresh set of type folders. These folders are jpg png etc etc
# copyToTypeFolders(destination = "A:\Temp", paths = ["G:\\!A77_Photography_Masters"], copy = True)
## Step two(or three) is to sort these folders into a dated subfolder setup for cleaner sorting. This currently only sorts by year / month folders
# buildDateFolders(path = "A:\\Temp\\JPG", destination = "A:\date", copy = False)
## Step three(or two) is to look for duplicates though this should be taken care of in the copy
#paths = ["A:\\!PhotosMaster_000\Phone_Photos_master001\\JPG"]
#doDupCheck(paths = paths, imagesOnly = False, move = False, checkname = True, checksize = True)

class DupCheckUI(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.mainLayout = QVBoxLayout(self)

def main():

    app = QApplication(sys.argv)

    w = DupCheckUI()
    w.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()