import numpy
import numpy as np
from utility import line_to_set
import matplotlib.pyplot as plt
from tqdm import tqdm
import pickle
from generating_polynomial import BinaryGP
import time


def polynomial_times(a, b):
    assert len(a) == len(b)
    c = numpy.zeros(len(a))
    for i in range(len(a)):
        for j in range(i+1):
            c[i] += a[j] * b[i-j]
    return c


def bgp_size_distribution(root:BinaryGP, num_item):
    F_A = np.zeros(num_item)
    if root.childA is None:
        F_A[1] = 1
    else:
        F_A = bgp_size_distribution(root.childA, num_item)
    F_B = np.zeros(num_item)
    if root.childB is None:
        F_B[1] = 1
    else:
        F_B = bgp_size_distribution(root.childB, num_item)

    F_C = root.Pa * F_A + root.Pb * F_B + root.Pab * polynomial_times(F_A, F_B)
    return F_C


if __name__ == '__main__':
    # NUM_ITEM = 100
    # NUM_ITEM = 1362
    NUM_ITEM = 4627
    file_path = "dataset/HKTVmall.txt"
    # file_path = "dataset/subsample_HKTVmall.txt"
    # file_path = "invertable_mapping_result/HKTVmall_subsample/im.txt"

    item_freq = np.zeros(NUM_ITEM)
    size_freq = np.zeros(NUM_ITEM)
    NUM_SET = 0
    with open(file_path, "r") as f:
        for line in tqdm(f.readlines()):
            NUM_SET += 1
            set_list = line_to_set(line)
            for item in set_list:
                item_freq[item] += 1
            size_freq[len(set_list)] += 1

    # Ground Truth
    size_p = size_freq / NUM_SET
    plt.figure()
    # plt.title("HKTVmall size distribution")
    plt.xlabel("Set Size")
    plt.ylabel("p")
    plt.ylim(0, 0.45)
    plt.bar(range(16), size_p[0:16])
    plt.show()

    # # IID
    # item_p = item_freq / NUM_SET
    # ideal_size_distribution = np.zeros(NUM_ITEM)
    # ideal_size_distribution[0] = 1
    # for i in tqdm(range(NUM_ITEM)):
    #     p = np.zeros(NUM_ITEM)
    #     p[0] = 1 - item_p[i]
    #     p[1] = item_p[i]
    #     ideal_size_distribution = polynomial_times(ideal_size_distribution, p)
    #
    # with open("HKTVmall_iid_size_distribution.pickle", 'wb') as f:
    #     pickle.dump(ideal_size_distribution, f)
    # plt.figure()
    # # plt.title("HKTVmall size distribution under iid")
    # plt.xlabel("Set Size")
    # plt.ylabel("p")
    # plt.ylim(0, 0.45)
    # plt.bar(range(16), ideal_size_distribution[0:16])
    # plt.show()

    # BGP
    st = time.time()
    # f = open("HKTVmall_root.pickle", "rb")
    # root = pickle.load(f)
    #
    # BGP_size = bgp_size_distribution(root, NUM_ITEM)
    # with open("HKTVmall_BGP_size_distribution.pickle", 'wb') as f:
    #     pickle.dump(BGP_size, f)

    f = open("HKTVmall_BGP_size_distribution.pickle", 'rb')
    BGP_size = pickle.load(f)
    print(BGP_size[0:21])
    plt.figure()
    # plt.title("HKTVmall size distribution under BGP")
    plt.xlabel("Set Size")
    plt.ylabel("p")
    plt.ylim(0, 0.45)
    plt.bar(range(16), BGP_size[0:16])
    plt.show()
    print(time.time() - st)
