import os
import timeit
def main():
    fileList=["C17","C432","C499","C880","C1355","C1908","C2670","C3540","C5315","C6288","C7552"]

    for fileName in fileList: #skip first during generazion phase
        start_time = timeit.default_timer()
        os.system('python simulazione.py --input circuiti_ISCAS85/'+fileName+'.txt --output circuiti_ISCAS85/'+fileName+'_output.txt --test circuiti_ISCAS85/'+fileName+'_test.txt --error circuiti_ISCAS85/'+fileName+'_error.txt --error_rate 10 --generate > NUL')
        elapsed = timeit.default_timer() - start_time
        print(fileName, ":", elapsed)

    for fileName in fileList:
        start_time = timeit.default_timer()
        os.system('python simulazione_fast.py --input circuiti_ISCAS85/'+fileName+'.txt --output circuiti_ISCAS85/'+fileName+'_output.txt --test circuiti_ISCAS85/'+fileName+'_test.txt --error circuiti_ISCAS85/'+fileName+'_error.txt > NUL')
        elapsed = timeit.default_timer() - start_time
        print(fileName, ":", elapsed)

    for fileName in fileList:
        start_time = timeit.default_timer()
        os.system('python simulazione.py --input circuiti_ISCAS85/'+fileName+'.txt --output circuiti_ISCAS85/'+fileName+'_output.txt --test circuiti_ISCAS85/'+fileName+'_test.txt --error circuiti_ISCAS85/'+fileName+'_error.txt > NUL')
        elapsed = timeit.default_timer() - start_time
        print(fileName, ":", elapsed)

if __name__ == "__main__":
    main()