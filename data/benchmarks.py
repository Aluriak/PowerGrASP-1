
import csv
import os

FIELD_TEST_CASE = 'test case'
FIELD_METH      = 'method'
FIELD_TIME      = 'time'
ALL_FIELDS      = FIELD_TEST_CASE, FIELD_METH, FIELD_TIME

METHOD_BLOCK = 'block'
METHOD_RDCTN = 'post-reduction'
METHOD_CURRENT = METHOD_BLOCK
METHOD_OTHER   = METHOD_RDCTN if METHOD_CURRENT is METHOD_BLOCK else METHOD_BLOCK

def swith_method():
    global METHOD_CURRENT
    METHOD_CURRENT = METHOD_RDCTN if METHOD_CURRENT is METHOD_BLOCK else METHOD_BLOCK

def int_input(input_msg):
    data = None
    while data is None:
        try:
            data = int(input(input_msg))
        except ValueError:
            pass
    return data

ASP_DIR = 'tests'
CSV_FILE  = 'data/benchmarks.csv'



testcases = dict(enumerate(
    _ for _ in os.listdir(ASP_DIR) if _.endswith('.lp')
))
outputfile = open(CSV_FILE, 'w')
writer = csv.DictWriter(outputfile, fieldnames=ALL_FIELDS)
writer.writeheader()

terminated = False
while not terminated:
    print('\n'.join(str(n) + ':' + str(t) for n, t in testcases.items()))
    rawdata = {}

    try:
        rawdata[FIELD_TEST_CASE] = testcases[int_input('Which test case ?')]
        rawdata[FIELD_METH]      = METHOD_CURRENT
        rawdata[FIELD_TIME]      = str(round(int_input('time (secondes) : = '), 2))

        command = ' '
        while len(command) > 0:
            print('\n'.join(field.rjust(10) + ': ' + rawdata[field]
                            for field in ALL_FIELDS))
            command = input('enter for save & next, q for save & quit, s for change used method: ')
            if command == 'q':
                terminated = True
                command = ''
            elif command == 's':
                swith_method()
                rawdata[FIELD_METH] = METHOD_CURRENT

        assert(all(k in ALL_FIELDS for k in rawdata))
        writer.writerow(rawdata)


    except KeyError:
        print('Non valid id')


print('Data saved in ' + CSV_FILE)

outputfile.close()


