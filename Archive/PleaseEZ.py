import os
import csv
import sys

Jdir = 'CharaJ\\'
Jf = "C:\\Users/1234/Desktop/nameJ.txt"
OUTJ = open(Jf,'w',encoding='UTF-8-sig')
"""
Kdir = "C\Ezwork/CharaK/"
Kf = "C:\\Users/1234/Desktop/nameK.txt"
OUTK = open(Kf,'w')
filenK = os.listdir(Kdir)
"""
filenJ = os.listdir(Jdir)
#Jname만
"""
for filename in filenJ:
    if ".csv" not in filename:
        continue
    Jfile = open(Jdir + filename)
    for line in Jfile:
        OUTJ.write(line)
    OUTJ.write("\n\n")
    Jfile.close()
OUTJ.close()
"""
#filename = argv[2]
for filename in filenJ:
    if ".csv" not in filename:
        continue
    Jfile = Jdir + filename
    OJfile = open(Jfile)
    with open(Jfile, 'r',encoding='UTF-8-sig',newline='') as csv_in_file:
        for line in Jfile:
            csv_read = csv.reader(csv_in_file)
            for row_list in csv_read:
                try:
                    N = str(row_list[1]).strip()
                    A = str(row_list[0]).strip()
                except IndexError:
                    continue
                if A == "名前":
                    print(N)
                elif A == "番号":
                    print(N)
                else:
                    continue
