# In[]
import unittest

from Final_Project import Analysis, filepath

class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.inputs = filepath()
        self.analysis = Analysis(self.inputs).setup()
        
    def test_group_data(self):
        analysis = self.analysis
        analysis.reduced_dataset = analysis.set_options()
        
        analysis.year_lst = [2001]
        
        grouped  = analysis.group_data()
        self.minimum = 4.24
        self.maximum = 4.70
        
        print('\nThe expected range of average monthly values for 2001 is between {} and {}'.format(self.minimum, self.maximum))
        
        self.assertGreater(grouped['Price'].min(), self.minimum)
        self.assertLess(grouped['Price'].max(), self.maximum)

if __name__ == '__main__':
    unittest.main()
