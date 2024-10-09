import pickle
import numpy as np
import random
from random import sample
from utility import line_to_set, x_log2_x
from tqdm import tqdm


def bits_to_int(bits:list):
    if sum(bits)==0:
        return 0
    sum_res = 0
    for i in range(len(bits)):
        sum_res += bits[i] * 2**i
    return int(sum_res)


def group_based_length(source_file_path, permutation, group_size, num_item):
    num_group = num_item // group_size
    freq = np.zeros(shape=(num_group, 2**group_size))
    num_set = 0
    with open(source_file_path, 'r') as f:
        for line in tqdm(f.readlines()):
            num_set += 1
            set_list = line_to_set(line)
            x = np.zeros(num_item)
            for item in set_list:
                item = permutation[item]
                x[item] += 1
            for i in range(num_group):
                number = bits_to_int(list(x[group_size*i:group_size*(i+1)]))
                freq[i, number] += 1
    # check the length
    length = 0
    for i in range(num_group):
        length += x_log2_x(num_set)
        for number in range(2**group_size):
            length += - x_log2_x(freq[i, number])
    return length


if __name__ == '__main__':
    source_file_path = 'dataset/Tmall.txt'
    # source_file_path = 'dataset/subsample_HKTVmall.txt'
    num_item = 1368   # Tmall, 8 * 171
    # num_item = 4632  # HKTVmall, 8 * 579

    # seed = 42
    # print(seed)
    # random.seed(seed)
    # np.random.seed(seed)
    # permutation = random.sample(range(num_item), k=num_item)

    permutation = list(range(num_item))

    length = group_based_length(source_file_path, permutation, group_size=8, num_item=num_item)
    print(length)

    # # length = group_based_length(source_file_path, permutation, group_size=8, num_item=num_item)
    # # print(length)
    # for i in range(10):
    #     source_file_path = 'dataset/HKTVmall/HKTVmall' + str(i) + '.txt'
    #     length = group_based_length(source_file_path, permutation, group_size=8, num_item=num_item)
    #     print(length)
