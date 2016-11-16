## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: handles values with errors

import math

class Value :

    def __init__(self,val,err = 0):
        self.val = float(val)
        self.err = float(err)

    def __add__(self,other) :
        val = self.val + other.val
        err = self.err + other.err
        return Value(val,err)

    def __sub__(self,other) :
        val = self.val - other.val
        err = self.err - other.err
        return Value(val,err) 

    def __div__(self,other) :

        if other.val == 0: 
            print "ATENTION: Cannot divide by 0"
            return 
        
        if self.val == 0:
            return Value(0.,0.)

        val = self.val / other.val
        err = val * math.sqrt( (self.err / self.val)**2 + (other.err / other.val)**2 )
        return Value(val,err)

    def __mul__(self,other) :
        
        if self.val == 0 or other.val == 0:
            return Value(0.,0.)
        
        val = self.val * other.val
        err = val * math.sqrt( (self.err / self.val)**2 + (other.err / other.val)**2 )
        return Value(val,err)

    def __repr__(self) :
        return "{0:.4} +/- {1:.4}".format(self.val,self.err)


