from threading import Thread

''' Simple Thread obj, only difference is that you can extract the output of the threaded function '''
class retThread(Thread):

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.output = None # Variable to return

    def run(self):

        if self._target is not None:
            self.output = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):

        super().join(*args, **kwargs)
        return self.output
