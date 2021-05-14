import threading

''' Simple threading obj that keeps a list of threads and executes them one by one '''
class threadQueue():

    def __init__(self):

        self.queue = []
        self.cont = True
        self.curr = None

        def run():

            if self.cont:
                if self.queue.__len__() != 0:
                    self.curr = self.queue.pop(0)
                    self.curr.start()
                    self.curr.join()
                    threading.Thread(target=run).start()
                else:
                    threading.Timer(1.0, run).start()

        threading.Thread(target=run).start()

    def addJob(self, thread):

        self.queue.append(thread)

        
    def destroy(self):

        self.cont = False

'''
testQ = threadQueue()

from time import sleep

def test(_time: int):
    for a in range(0, _time):
        sleep(1)
        print(a+1)

t1 = threading.Thread(target=test, args=[5])
t2 = threading.Thread(target=test, args=[6])
t3 = threading.Thread(target=test, args=[7])

testQ.addJob(t1)
testQ.addJob(t2)
testQ.addJob(t3)
'''