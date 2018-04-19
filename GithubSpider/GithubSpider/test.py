import re
class test():

    def testNorm(var):
        string = r'.*[^/]$';
        pattern = re.compile(string)
        match = re.search(pattern,var)
        print match.group(0)

    testNorm('sssss/aaaa?tab=following')