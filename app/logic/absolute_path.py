import os
import sys
from pathlib import Path

'''Creates the AbsolutePath based off of the relative path.
Also creates the directories in path if they are not found.
@param {string} relativePath - a string of directories found in config.yaml
@param {string} filename - the name of the file that should be in that directory
@return {string} filepath - returns the absolute path of the directory'''
'''TODO: ADD @PARAm for make dirs'''
def getAbsolutePath(relativePath, filename=None, makeDirs=False):
    filepath = os.path.join(Path(__file__).parent.parent.parent,relativePath)
    if makeDirs == True:
        try:
            os.makedirs(filepath)
        except:
            pass
    if filename != None:
        filepath = os.path.join(filepath,filename)
    return filepath
