from firehelper import CommandRegistry
import azkm

version = {
    'version': lambda : print(azkm.__VERSION__)
}

CommandRegistry.register(version)