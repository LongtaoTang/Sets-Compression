# this file calculate the bits-back performance
import numpy as np
from utility import line_to_set, log_factorial, x_log2_x
from tqdm import tqdm


def bits_back_performance(file_path, num_item):
    item_freq = np.zeros(num_item)
    bit_back_gain = 0
    NUM_SET = 0
    with open(file_path, "r") as f:
        for line in tqdm(f.readlines()):
            NUM_SET += 1
            set_list = line_to_set(line)
            for item in set_list:
                item_freq[item] += 1
            bit_back_gain += log_factorial(len(set_list))

    # calculate
    Total_symbol = np.sum(item_freq) + NUM_SET  # NUM_SET is the number of split symbol
    length = x_log2_x(Total_symbol) - x_log2_x(NUM_SET)
    for i in range(num_item):
        length += -x_log2_x(item_freq[i])
    length = length - bit_back_gain
    return length, bit_back_gain


if __name__ == '__main__':
    # NUM_ITEM = 1362
    NUM_ITEM = 4627
    # file_path = "dataset/subsample_Tmall.txt"
    file_path = "dataset/HKTVmall.txt"
    length, bit_back_gain = bits_back_performance(file_path, NUM_ITEM)
    print(length)
    print(bit_back_gain)
    print(length/(length+bit_back_gain))