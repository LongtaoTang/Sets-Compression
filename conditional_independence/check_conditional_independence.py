# we conduct the chi-square independence test on the dataset
import pickle
import numpy as np
from utility import line_to_set
from tqdm import tqdm
from Independence.chi_square import chi_sqare


if __name__ == '__main__':
    # pair_path = "Tmall_condition_pairs.pickle"
    # data_path = "../dataset/Tmall.txt"
    # contingency_path = "Tmall_contingency_table_dataset.pickle"
    # result_path = "Tmall_result_dataset.pickle"

    pair_path = "HKTVmall_condition_pairs.pickle"
    data_path = "../dataset/HKTVmall.txt"
    contingency_path = "HKTVmall_contingency_table_dataset.pickle"
    result_path = "HKTVmall_result_dataset.pickle"

    f = open(pair_path, 'rb')
    pair_list = pickle.load(f)
    contingency_table_list = []
    for i in range(len(pair_list)):
        contingency_table_list.append(np.array([[0, 0],
                                                [0, 0]]))
    with open(data_path, "r") as f:
        for line in tqdm(f.readlines()):
            set_list = line_to_set(line)
            for i in range(len(pair_list)):
                pair = pair_list[i]
                a = pair[0]
                b = pair[1]
                listA = pair[2]
                listB = pair[3]
                if len(list(set(set_list) & set(listA))) == 0:
                    continue
                if len(list(set(set_list) & set(listB))) == 0:
                    continue
                if a not in set_list:
                    if b not in set_list:
                        contingency_table_list[i][0][0] += 1
                    else:
                        contingency_table_list[i][0][1] += 1
                else:
                    if b not in set_list:
                        contingency_table_list[i][1][0] += 1
                    else:
                        contingency_table_list[i][1][1] += 1

    f = open(contingency_path, 'wb')
    pickle.dump(contingency_table_list, f)

    f = open(contingency_path, 'rb')
    contingency_table_list = pickle.load(f)
    print(contingency_table_list)

    result = []
    for i in range(len(contingency_table_list)):
        print(pair_list[i][0], pair_list[i][1])
        res = chi_sqare(contingency_table_list[i])
        result.append(res)
        # if res == False:
        #     print(contingency_table_list[i])
    print(result)
    f = open(result_path, 'wb')
    pickle.dump(result, f)
    print(sum(result))
