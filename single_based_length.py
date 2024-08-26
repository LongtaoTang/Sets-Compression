# this file calculate the performance when coding one-hot with each item's frequency
import numpy as np
from utility import line_to_set, length_single
from tqdm import tqdm


def single_based_length(item_freq, NUM_SET):
    length = 0
    for i in range(len(item_freq)):
        length += length_single(freq=item_freq[i], N=NUM_SET)
    return length


if __name__ == '__main__':
    NUM_ITEM = 1362
    # NUM_ITEM = 4627
    # file_path = "dataset/HKTVmall.txt"
    file_path = "dataset/subsample_Tmall.txt"

    item_freq = np.zeros(NUM_ITEM)
    NUM_SET = 0
    with open(file_path, "r") as f:
        for line in tqdm(f.readlines()):
            NUM_SET += 1
            set_list = line_to_set(line)
            for item in set_list:
                item_freq[item] += 1

    # calculate
    length = single_based_length(item_freq, NUM_SET)
    print(length)
