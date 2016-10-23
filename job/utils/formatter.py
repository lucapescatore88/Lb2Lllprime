## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: extends the standards string.format() to handle cases where the key is not present.

import string
from ROOT import *

class PartialFormatter(string.Formatter):
    def __init__(self, missing='--', bad_fmt='!!'):
        self.missing, self.bad_fmt=missing, bad_fmt

    def get_field(self, field_name, args, kwargs):
        
        try:
            val=super(PartialFormatter, self).get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            val=None,field_name 
        return val 

    def format_field(self, value, spec):
                # handle an invalid format
        if value==None: return self.missing
        try:
            return super(PartialFormatter, self).format_field(value, spec)
        except ValueError:
            if self.bad_fmt is not None: return self.bad_fmt   
            else: raise




def divide(num, numE, den, denE) :
    ratio  = 0
    ratioE = 0
    
    if (den != 0.) :
        ratio  = num / den
        ratioE = ratio * TMath.Sqrt(TMath.Power(numE / num, 2) + TMath.Power(denE / den, 2))
  
    return ratio, ratioE

def multiply(num, numE, den, denE) :
    prod  = 0
    prodE = 0
    
    if (den != 0.) : 
        prod  = num * den
        prodE = prod * TMath.Sqrt(TMath.Power(numE / num, 2) + TMath.Power(denE / den, 2))
  
    return prod, prodE


