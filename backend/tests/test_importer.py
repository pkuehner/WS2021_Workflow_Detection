import unittest

from importer import import_file

class TestPatternUtil(unittest.TestCase):

    def test_import_csv(self):
        import_csv = import_file('../test-data/OR.csv')

    def test_import_xes(self):
        import_csv = import_file('../test-data/running-example.xes')

    def test_import_wrong_csv(self):
        try:
            import_file('../test-data/fail_wrong_format.csv')
            self.assertTrue(False)
        except:
            self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()
