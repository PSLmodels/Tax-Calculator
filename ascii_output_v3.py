"""
Turns csv output of tax calculator to ascii output with uniform columns
and transposes data so columns are rows, rows are columns

"""

#records the data of one csv row to be later written into a uniform column
#also returns number of rows in result file
def rec_col(data, col_size, temp):
    nrows = 0
    while (data != []):
        col_elem = data.pop()
        #cuts a data string from the end if length is larger than col_size
        if (len(col_elem) > col_size):
            cut = col_size - len(col_elem)
            col_elem = col_elem[:cut]
        else:
        #adds spaces to fill out data string if length is smaller than col_size
            col_elem = col_elem.ljust(col_size)
        temp.write(col_elem)
        nrows += 1
    return nrows

def ascii_output():
    csv_results = "results_puf.csv" #input csv file
    ascii_results = "results_ascii.txt"
    
    #list of integers corresponding to the number(s) of the row(s) in the
    #csv file, only rows in list will be recorded in final output
    #if left as [], results in entire file being converted to ascii
    #must put in order from smallest to largest
    recid_list = [1,2,3]
    #recid_list = [33180, 64023, 68020, 74700, 84723, 98001, 107039, 107298, 108820]

    #Number of characters in each column
    col_size = 15

    #counters for number of rows and columns in eventual ascii output
    col_num = 0
    row_num = 0

    f1 = open(csv_results, 'r')
    temp = open("temp_res.txt", 'r+')
    f2 = open(ascii_results, 'w')

    #initiate first column with headers
    line = f1.readline()
    sline = line.rstrip()
    column_data = sline.split(",")
    column_data.reverse()
    row_num = rec_col(column_data, col_size, temp)
    col_num += 1

    #Makes temporary ascii file with uniform blocks of data
    if (recid_list == []):
        #record all the rows
        while line != '':
            line = f1.readline()
            sline = line.rstrip()
            column_data = sline.split(",")
            column_data.reverse()
            row_num = rec_col(column_data, col_size, temp)
            col_num += 1
            line = f1.readline()
    else:
        #record only rows in recid_list
        i = 0
        recid = 2
        while (i < len(recid_list)):
            #skips unnecessary lines
            while (recid < recid_list[i]):
                f1.readline()
                recid += 1
            line = f1.readline()
            sline = line.rstrip()
            column_data = sline.split(",")
            column_data.reverse()
            row_num = rec_col(column_data, col_size, temp)
            recid += 1
            i += 1
            col_num += 1

    #transposes the results so different recids are in different columns
    i = 0
    while (i < row_num):
        j = 0
        row = ''
        temp.seek(15*i, 0)
        while (j < col_num):        
            row = row + temp.read(15)
            j += 1
            temp.seek((col_size*(row_num-1)), 1)
        f2.write(row + '\n')
        i += 1

    temp.close()
    f1.close()
    f2.close()

ascii_output()