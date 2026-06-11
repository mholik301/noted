import importlib
import inspect
import os
import importlib.util
import sys
from enum import Enum






def ModuleFactory(moduleName):

    #ref: https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

    rootFullPath = os.path.dirname(os.path.realpath(__file__)) + "\\"
    pluginFullPath = rootFullPath + 'plugins'

    for mymodule in os.listdir(pluginFullPath):
        if os.path.splitext(mymodule)[0] == moduleName:

            modulePath = pluginFullPath+"\\"+moduleName+".py"
            spec = importlib.util.spec_from_file_location(moduleName, modulePath)
            my_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(my_module)
            #instance = my_module.parrot("test")
            #instance.menu()

            for name, obj in inspect.getmembers(my_module):         # iterate through members
                #if isinstance(obj, type):                           # check if members is a class
                #    return obj
                if name == moduleName:
                    return obj