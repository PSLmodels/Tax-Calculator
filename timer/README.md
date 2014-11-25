--------------
Timer Utils Example usage 
--------------

(with the taxcalc package from latest master):
========

*Each necessary new line of code includes comments above it*

A) To cumulatively time all of functions added together into  'main_timer' (lowest level)

    ## 'timed_calculate.py' defines 'main_timer' and strictly times each functions execution
    from timer.timed_calculate import *

    if __name__ == '__main__':
        run()
        ## after the functions have been called print the timer results
        print (main_timer)


B) To time the functions, along with the results being concatenated into a DataFrame into 'func_concat_timer',
   This times the code level higher than the above example

    from timer.timed_calculate import *
    ## declare timer
    no_csv_timer = cumulative_timer("No CSV Timer")

    def run(puf=True):
        tax_dta = pd.read_csv("puf2.csv")

        ## start timer
        with no_csv_timer.time():
            calc = Calculator(tax_dta)
            set_input_data(calc)
            update_globals_from_calculator(calc)
            update_calculator_from_module(calc, constants)
            *
            *  
            *
            calculated = concat([calculated, df_C1040], axis=1)
            calculated = concat([calculated, DEITC()], axis=1)
            calculated = concat([calculated, SOIT(_eitc)], axis=1)
        to_csv("results.csv", calculated)

    if __name__ == '__main__':
        run()

        ## printer the new timer
        print (no_csv_timer)

        print (main_timer)


C) To time the entire run() function at the highest level
   including the function calculations, concatenating into DataFrames, and the CSV input/output calls
   *Note this format can be used to specifically time any one function
   
    ## if timed_calculate has already been imported this import is not needed 
    from timer.timer_utils import cumulative_timer

    ## apply the @time_this decorator
    @time_this
    def run(puf=True):
        tax_dta = pd.read_csv("puf2.csv")
        *
        *
        *


(timing initial code before taxcalc refactoring):
========

git clone the repo to temporary local directory

    'git clone https://github.com/OpenSourcePolicyCenter/Tax-Calculator temp_dir_name'
    
checkout to repo to commit before refactoring ('PEP8 fixes' commit)

    'git checkout -b new_branch 4cdc5841fefc5d175c9e5e538c7fd9c670fe35d1'
    
copy timer from original master directory to the new cloned branch

    'cp ~/user/.../Tax-Calculator/timer/* ~/user/.../temp_dir_name/timer/'

decorate the Test() function with @time_this, same as step C) above
*note this includes CSV input/output, comment out #np.savetxt() calls to time explicit func calculation time