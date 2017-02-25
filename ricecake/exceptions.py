# List of Exception classes for ricecake

class InvalidConfigFile(Exception):
    """ InvalidConfigFile: raised when config ini file contains too few or too many entries """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
		
class InvalidRootFolder(Exception):
    """ InvalidRootFolder: raised when multiple channel folders exist within a dir """
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)