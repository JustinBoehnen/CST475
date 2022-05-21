# this program takes the output of gendata.py and converts it to meet the 
# requrments of lab7, this is done because the output of gendata.py is a more
# desirable collection of data for the purposes of training a slither.io bot

import csv

def convert(src_name, dest_name):
    src = open(src_name, "r")
    dest = open(dest_name, "w", newline="")

    reader = csv.reader(src, skipinitialspace=True, quoting=csv.QUOTE_NONNUMERIC)

    writer = csv.writer(dest)

    i = 0
    for row in reader:
        i += 1
        print(f"\rrow: {i}", end="")
        writer.writerow([i, row[-3]])
    src.close()
    dest.close()

convert(input("input: "), input("output: "))
