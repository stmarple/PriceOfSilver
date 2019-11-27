# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 11:55:20 2019

@author: STMar
"""

# In[]
import pandas as pd
from Final_Project import Analysis, filepath


def main():
    Analysis(filepath()).setup().run()
    df = Analysis().subset
    writer = pd.ExcelWriter('Monthly_Averages',engine='xlsxwriter')
    df.to_excel(writer, sheet_name='AVGs')     
    writer.save()
main()