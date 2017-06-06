# The recid (key) for each record is not unique after CPS match
# because 1) original PUF records were split in some cases
# 2) non-filers were added

# This script fixes the recid issue by
# 1) adding a digit at the end of recid for all original PUF records
#      - if no duplicates, add zero
#      - otherwise, differentiate duplicates by numbering them with increment integers starting from zero
# 2) setting recid for all non-filers (4000000 - 4005693)



import pandas

# import the old CPS matched PUF
data = pandas.read_csv("cps-puf.csv")

# sort all the records based on old recid
sorted_dta = data.sort(columns='recid')

# count how many duplicates each old recid has
# and save the dup count for each record
seq = sorted_dta.index
length = len(sorted_dta['recid'])
count = [0 for x in range(length)]
for index in range(1, length):
    num = seq[index]
    previous = seq[index-1]
    if sorted_dta['recid'][num] == sorted_dta['recid'][previous]:
        count[num] = count[previous]+1


# adding the ending digit for filers and non-filers
# with the dup count
new_recid = [0 for x in range(length)]
for index in range(0, length):
    if data['recid'][index] == 0:
        new_recid[index] = 4000000 + count[index]
    else:
        new_recid[index] = data['recid'][index] * 10 + count[index]

# replace the old recid with the new one
data['recid'] = new_recid
data.to_csv('puf.csv', index=False)



