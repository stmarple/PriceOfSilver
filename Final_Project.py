# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 16:25:07 2019

@author: STMar
"""
# In[]
import pandas as pd, os, matplotlib.pyplot as plt, warnings, sys


#from IPython import get_ipython
#get_ipython().run_line_magic('matplotlib', 'inline')

pd.set_option('display.expand_frame_repr',False)
pd.options.display.max_rows = 48

warnings.filterwarnings('ignore')
    
class Setup_Data:
    
    ''' This script can be used in conjuntion with stock analysis in conjunction with statistical modeling, clustering, and/or machine learning
        with little effort in modification.  I should be able to add modules the the core of this one.  Some of the questions that may be asked are:
            is there a negative correlation between stocks and silver (precious metals)?  Does silver go up/down/stay the same during hard times?
            Do silver prices go up during/around certain holidays?  I would guess that they would around christmas, but then again, silver seems to 
            go on sale around then.  Do sales affect the spot prices?
    '''
               
    def __init__(self, inputs, hist_tabname='Silver_1968_to_2015', current_tabname='Silver_2016_to_Present'):
        
        self.__reference = {'silver_1968' : {'sheetname': hist_tabname   },
                          'silver_2016' : {'sheetname': current_tabname} }   
        self.inputs = inputs
        self.out_path()
        self.display()
        self.file_sheets()
        self.display()
        
    def setup(self):
        self.__historical = self.__file_dataframes('silver_1968')
        self.__current = self.__file_dataframes('silver_2016')
        self.combined = self.combine_data_sets()
        self.transposed = self.transpose_df()
        self.add_cols = self.add_columns()
        self.dataset = self.filter_data()
        return self
        

    def filepath(self):
        count = 3  # end user gets 3 tries before program closes
        while True:
            inputs = input('Enter the folder path to the foler where all of your data files are stored: ')  
        
            if os.path.isdir(inputs) == False:
                count -= 1
                print('The path you entered was invalid. Please try again.')
                
                if count == 0:  # exit program after 3 bad entries
                    sys.exit('You have entered too many bad entries.  Program will now be shut down...')
            else:
                break
        return inputs
    
    def out_path(self):
        self.folder = os.path.abspath(os.path.join(os.path.dirname(self.inputs),'.', 'Outputs'))
   
    def __repr__(self,var):
        return repr(self.var)
     
    def file_sheets(self):  # sheetname verification
        input_list = [item for item in self.__reference]
        
        for infile in input_list:
            old = input("Is sheet name for {} still '{}'? (Y/N, or hit enter to skip): ".format(infile.upper(),self.__reference[infile]['sheetname'])).upper()
            if old in ['NO','N']:
                self.__reference[infile]['sheetname'] = input('Enter sheet name for {}: '.format(infile))
                
        # add filepaths
        for infile in os.listdir(self.inputs):
            for key in self.__reference:
                if key in infile.lower():
                    print('{}/{}'.format(self.inputs,infile))
                    self.__reference[key].update({'filename':'{}/{}'.format(self.inputs,infile)})
           
        # check if output folder exists at destination.  If not, create one
        if os.path.isdir(self.folder) == False:
            os.mkdir(self.folder)           
        return self.__reference
            
    def display(self):
        print('Loading data...please wait...')        
    
    def __file_dataframes(self,keyword):
        ref = self.__reference
        cols = (['Dates',
                'USD-Bid-High','USD-Ask-High', 'AUD-Bid-High','AUD-Ask-High','JPY-Bid-High','JPY-Ask-High',
                'USD-Bid-Low','USD-Ask-Low', 'AUD-Bid-Low','AUD-Ask-Low','JPY-Bid-Low','JPY-Ask-Low',
                'USD-Bid-Average','USD-Ask-Average', 'AUD-Bid-Average','AUD-Ask-Average','JPY-Bid-Average','JPY-Ask-Average'])
        
        # read in file
        tbl = pd.read_excel(ref[keyword]['filename'],sheet_name=ref[keyword]['sheetname'],skip_blanks=True)
        
        # filter out multi-indexes
        tbl = tbl.iloc[4:, :len(cols)]  # filter out last column

        # rename columns
        col = 0
        for column in cols:
            tbl =tbl.rename(columns={ tbl.columns[col] : column })
            col += 1
        
        # set dates to US time
        tbl['Dates'] = tbl['Dates'].apply(lambda x: pd.to_datetime(x).strftime('%m/%d/%Y'))
        tbl['Dates'] = pd.to_datetime(tbl['Dates'], errors='coerce') # ensure these are dates
        
        return tbl
    
    def combine_data_sets(self):
        combine = pd.concat([self.__historical,self.__current],ignore_index=True)
        combined = combine[combine['USD-Bid-Average'].notnull() ]
        combined.dropna(subset=['USD-Bid-Average'],inplace=True)
        return combined
          
    def transpose_df(self):
        self.combined
        values = list(self.combined.columns)
        values.remove('Dates')
        return pd.melt(self.combined, id_vars=['Dates'], value_vars=values)
    
    def add_columns(self):
        data = self.transposed.copy()
        
        data['Year'] = data['Dates'].dt.year
        data['Month'] = data['Dates'].dt.month
        
        data['Currency'] = data['variable'].map(lambda x: x.split('-')[0])
        data['Bid_Ask'] = data['variable'].map(lambda x: x.split('-')[1])
        data['Price_Type'] = data['variable'].map(lambda x: x.split('-')[2])
        
        del data['variable']
        return data      
    
    def filter_data(self):
        " Due to having limited data between 1968 and 1991, likely due to lack of internet worldwide, I'll be filtering these out"
        " Due to holidays, weekends,...etc, no prices are come out for some days.  I'll be filtering those out as well"
        
        df = pd.DataFrame(self.add_cols.copy(),columns=[
                'Dates','Currency','Bid_Ask','Price_Type','Year','Month','value']).rename(columns={'value':'Price'})
    
        df['Year'] = df['Year'].astype(int)
        df['Month'] = df['Month'].astype(int)
        return df
        
class Analysis(Setup_Data):
    
    def run(self):
        
        self.reduced_dataset = self.set_options()
        self.year_lst = self.choose_years()
        self.subset = self.group_data()
        self.graph_data = self.graph()
        
    # choose currency, bid/ask, high/low/average
    # set currency to USD, ask, average
    def set_options(self):
        return self.dataset.query("(Currency=='USD') and (Bid_Ask=='Ask') and (Price_Type=='Average')")
        
    def choose_years(self): 
        while True:
            try:
                years = input('Enter up to 4 years between 1991 and 2019 (seperated by commas, in format (yyyy)): ').split(',')
                year_list = [int(x) for x in years ]  # make sure input years are between 1991 and this year 1991 is when we started getting more complete data
                year_list = [x for x in years if 1991 <= int(x) <= pd.datetime.now().year]      
                
                if 0 < len(year_list) < 5:
                    break  
                else:
                    print('You entered too many inputs.  Please try again.')             
            except ValueError:
                print('Make sure your inputs are integers that are in the format yyyy')        
        return year_list

    def group_data(self):
        dataset = self.reduced_dataset
        years = self.year_lst
        
        # filter isolate_data based on years chosen by user
        my_data = pd.DataFrame(dataset[dataset['Year'].isin(years)],columns=['Dates','Year','Month','Price'])
        my_data['Price'] = my_data['Price'].astype(float)   # ensure all prices are float
        grouped = my_data.groupby(['Year','Month'])['Price'].mean().reset_index()
        print(repr(grouped))
        return grouped
    
    def graph(self):
        graph = self.subset.copy()
        graph.set_index('Month').groupby(['Year'])['Price'].plot(legend = True)      
        plt.title('Monthly Silver Spot Pricing Over Time')
        plt.ylabel('Average Prices')    
        plt.savefig('{}/{}.pdf'.format(self.folder,'_'.join(str(element) for element in self.year_lst))) 
    
def filepath():
    count = 3  # end user gets 3 tries before program closes
    while True:
        inputs = input('Enter the folder path to the foler where all of your data files are stored: ')  
    
        if os.path.isdir(inputs) == False:
            count -= 1
            print('The path you entered was invalid. Please try again.')
            
            if count == 0:  # exit program after 3 bad entries
                sys.exit('You have entered too many bad entries.  Program will now be shut down...')
        else:
            break
    return inputs




    
    
    
    
    
    
    
    
    
    
    
    
    
    