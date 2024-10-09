# this file calculate the performance using first-order Markov model
import numpy as np
from utility import line_to_set, x_log2_x
from tqdm import tqdm
from random import shuffle


def markov_based_length(pair_freq):
    markov_length = 0
    for i in range(len(pair_freq)):
        total_count = sum(pair_freq[i, :])  # start at the current item
        markov_length += x_log2_x(total_count)
        for j in range(len(pair_freq[i])):
            # for next item
            markov_length = markov_length - x_log2_x(pair_freq[i, j])
    return markov_length


if __name__ == '__main__':
    # NUM_ITEM = 1362
    NUM_ITEM = 4627
    file_path = "dataset/HKTVmall.txt"
    # file_path = "dataset/subsample_Tmall.txt"

    pair_freq = np.zeros(shape=(NUM_ITEM, NUM_ITEM), dtype=np.int32)  # split flag is the item 0
    NUM_SET = 0
    with open(file_path, "r") as f:
        for line in tqdm(f.readlines()):
            NUM_SET += 1
            set_list = line_to_set(line)
            set_list.sort()
            shuffle(set_list)
            set_len = len(set_list)
            current_item = 0    # start at the split flag
            for i in range(set_len):
                next_item = set_list[i]
                pair_freq[current_item, next_item] += 1
                current_item = next_item
            next_item = 0   # we end with the split flag
            pair_freq[current_item, next_item] += 1

    # calculate
    length = markov_based_length(pair_freq)
    print(length)
