class __prev(object):

    _i = 3

    @property
    def i(self):
        return type(self)._i

    @i.setter
    def i(self,val):
        type(self)._i = val


def stdout_print(text: str):
    print(' '.join(['' for i in range(0, __prev().i)]), end='\r', flush=True)
    print('{0}'.format(text), end='\r', flush=True)
    __prev().i = len(text)