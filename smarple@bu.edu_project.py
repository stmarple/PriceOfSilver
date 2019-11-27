# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 14:29:58 2019

@author: M322671
"""
# In[]
from Final_Project import Analysis, filepath

def main(): 
    try: 
        Analysis(filepath()).setup().run()
    except KeyError:
        print('Please check your inputs.  The file path entered does not contain the historical data.')
    except FileNotFoundError:
        print('That file path is invalid.  Please try again.')

if __name__=='__main__':
    main()
    