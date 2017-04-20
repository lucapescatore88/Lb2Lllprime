## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: handles values with errors

import math

class Value :

    def __init__(self,val = 0,err = 0,scale = 0,error=None):
        self.val = float(val)
        self.err = float(err)
        self.scale = scale

        if err != 0 or error is None : return 
        if not isinstance(error,tuple) : return
        if len(error) == 2 and error[0] == 'binomial' :
            self.err = math.sqrt((self.val*(1.-self.val)) / float(error[1]))


    def __add__(self,other) :
        val = self.val * 10**self.scale  + other.val * 10**other.scale
        err = self.err * 10**self.scale + other.err * 10**other.scale
        return Value(val,err)

    def __sub__(self,other) :
        val = self.val * 10**self.scale - other.val * 10**other.scale
        err = self.err * 10**self.scale + other.err * 10**other.scale
        return Value(val,err) 

    def __div__(self,other) :

        if other.val == 0: 
            print "ATENTION: Cannot divide by 0"
            return 
        
        if self.val == 0:
            return Value(0.,0.)

        val = self.val / other.val
        err = val * math.sqrt( (self.err / self.val)**2 + (other.err / other.val)**2 )
        scale = self.scale - other.scale
        return Value(val,err,scale)

    def __mul__(self,other) :
        
        if self.val == 0 or other.val == 0:
            return Value(0.,0.)
        
        val = self.val * other.val
        err = val * math.sqrt( (self.err / self.val)**2 + (other.err / other.val)**2 )
        scale = self.scale + other.scale
        return Value(val,err,scale)

    def __repr__(self) :
        
        return self.get_str()

    def get_str(self,scale=None, showscale=True,prec=None,otype='shell') :

        if scale is None :
            scale = self.scale
        val = self.get_val(scale)
        err = self.get_err(scale)
        
        if prec is None :
            prec = 1
            if abs(err) < 0.5 :
                prec = abs(self.detect_scale()+self.scale-scale)

        pm    = '+/-'
        times = 'x'
        wrap  = ''
        exp = "10^{0:}".format(scale)
        if 'latex' in otype :
            pm    = r'\pm'
            times = r'\times'
            if 'nowrap' not in otype : wrap  = '$'
            exp = "10^{{"+"{0:}".format(scale)+"}}"

        out = ""
        if err > 0 :
            if self.scale == 0 or not showscale :
                out = ("{0:."+str(prec)+"f} {pm} {1:."+str(prec)+"f}").format(val,err,pm=pm)
            else :
                out = ("({0:."+str(prec)+"f} {pm} {1:."+str(prec)+"f}) {times} "+exp).format(val,err,pm=pm,times=times)
        else :
            if self.scale == 0 or not showscale :
                out = ("{0:."+str(prec)+"f}").format(val)
            else :
                out = ("{0:."+str(prec)+"f} {times} "+exp).format(val,times=times)
        return wrap+out+wrap

    def set_scale(self,scale) :
        self.scale = scale

    def get_val(self, scale=0) :
        return self.val * 10**(self.scale-scale)

    def get_err(self,scale=0) :
        return self.err * 10**(self.scale-scale)

    def change_scale(self,scale=0) :
        self.val *= 10**(self.scale-scale)
        self.err *= 10**(self.scale-scale)
        self.scale = scale
        #return self#.owner.getTopParent()

    def detect_scale(self,setscale=False) :

        scale = 0
        err = self.err
        if abs(err) < 1.e-12 :
            return 0

        if self.err < 1 :
            while err < 1. :
                err *= 10
                scale -= 1
        else :
            while err > 1. :
                err *= 0.1
                scale += 1
        
        if setscale :
            self.change_scale(scale)
        
        return scale



