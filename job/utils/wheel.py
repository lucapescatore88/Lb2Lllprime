
class Wheel :
    wheel = ['-','\\','|','/']
    curwheel = 0

    def increment(self) :

        if self.curwheel == 3 :
            self.curwheel = 0
            return self.wheel[0]
        self.curwheel += 1
        return self.wheel[self.curwheel]

