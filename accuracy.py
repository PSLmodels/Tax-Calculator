import numpy as np

def check_accuracy(py_answer, gold_std):
    acc_dict = {}
    for key in py_answer:
        if key in gold_std:
            print 'Found {} in gold standard'.format(key)
            test_length = float(len(py_answer[key]))
            gold_array = np.array(gold_std[key])
            print 'Array length is equal? {}'.format(len(gold_array) == test_length)
            n_correct = sum(py_answer[key] == gold_array)
            # n_correct = sum(np.in1d(py_answer[key], gold_array))
            acc_dict[key] = n_correct / test_length
    return acc_dict
