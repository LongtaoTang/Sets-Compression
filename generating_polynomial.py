import pickle
import numpy as np
from utility import line_to_set
from tqdm import tqdm


class BinaryGP:
    def __init__(self):
        self.Pa = 0
        self.Pb = 0
        self.Pab = 0
        self.childA = None
        self.childB = None
        self.var_A = []
        self.var_B = []
        self.var_total = []

    # def total_var(self):
    #     var_list = []
    #     var_list.extend(self.var_A.copy())
    #     var_list.extend(self.var_B.copy())
    #     return var_list

    def access_probability(self, var_X:list):
        flagA = False
        flagB = False
        for var in var_X:
            if var in self.var_A:
                flagA = True
            if var in self.var_B:
                flagB = True
        if flagA and flagB:
            return self.Pab, flagA, flagB
        elif flagA and not flagB:
            return self.Pa, flagA, flagB
        elif flagB and not flagA:
            return self.Pb, flagA, flagB


def scan_file(file_name, var_group):
    group_size = len(var_group)
    single_freq = np.zeros(group_size)
    pair_freq = np.zeros(shape=(group_size, group_size))
    num_set = 0
    with open(file_name, "r") as f:
        for line in tqdm(f.readlines()):
            num_set += 1
            set_list = line_to_set(line)
            flag_array = np.zeros(group_size)
            for i in range(group_size):
                for var in var_group[i]:
                    if var in set_list:
                        flag_array[i] = 1
            single_freq += flag_array
            indexes = np.nonzero(flag_array)[0]

            for i in range(len(indexes) - 1):
                for j in range(i + 1, len(indexes)):
                    a = indexes[i]
                    b = indexes[j]
                    pair_freq[a, b] += 1
    pair_freq = pair_freq + pair_freq.transpose()
    return single_freq, pair_freq, num_set


def grouping(single_freq, pair_freq, num_set):
    group_size = len(single_freq)
    M = pair_freq.copy()
    # mask the diag
    for i in range(len(M)):
        M[i, i] = - 1e9
    group_list = []
    for i in range(group_size//2):
        max_index_1d = np.argmax(M)
        max_index_2d = np.unravel_index(max_index_1d, M.shape)
        group_list.append(max_index_2d)
        # mask
        for j in range(group_size):
            M[max_index_2d[0], :] += -1e9
            M[:, max_index_2d[0]] += -1e9
            M[max_index_2d[1], :] += -1e9
            M[:, max_index_2d[1]] += -1e9
    return group_list


def model_entropy(bgp: BinaryGP):
    entropy = - bgp.Pa * log_2(bgp.Pa) - bgp.Pb * log_2(bgp.Pb) - bgp.Pab * log_2(bgp.Pab)
    if bgp.childA is not None:
        entropy += (bgp.Pa + bgp.Pab) * model_entropy(bgp.childA)
    if bgp.childB is not None:
        entropy += (bgp.Pb + bgp.Pab) * model_entropy(bgp.childB)
    return entropy


def check_length(root, file_path):
    with open(file_path, 'r') as f:
        length = 0
        for line in tqdm(f.readlines()):
            set_list = line_to_set(line)
            length += check_single_length(root, set_list)
        return length


def check_single_length(bgp: BinaryGP, set_list):
    flagA = False
    flagB = False
    length = 0
    for item in set_list:
        if item in bgp.var_A:
            flagA = True
        if item in bgp.var_B:
            flagB = True
    if flagA and flagB:
        length += - log_2(bgp.Pab)
    elif flagA and not flagB:
        length += - log_2(bgp.Pa)
    elif flagB and not flagA:
        length += - log_2(bgp.Pb)
    else:
        print("Error")

    if flagA:
        if bgp.childA is not None:
            length += check_single_length(bgp.childA, set_list)
    if flagB:
        if bgp.childB is not None:
            length += check_single_length(bgp.childB, set_list)
    return length


def log_2(x):
    if x > 0:
        return np.log2(x)
    else:
        print("Warning: too small for log2(x): " + str(x))
        return np.log2(1e-9)


def build_root(NUM_ITEM, file_path):
    var_group = []
    var_polynomial = []
    for i in range(NUM_ITEM):
        var_group.append([i])
        var_polynomial.append(None)

    while len(var_group) > 1:
        print(len(var_group))
        # scan the file and decide the groups
        single_freq, pair_freq, num_set = scan_file(file_path, var_group)
        group_list = grouping(single_freq, pair_freq, num_set)
        # calculate new polynomial
        new_var_group = []
        new_var_polynomial = []
        group_index = list(range(len(var_group)))
        for group in group_list:
            a, b = group
            group_index.remove(a)
            group_index.remove(b)

            Na = single_freq[a] - pair_freq[a, b]
            Nb = single_freq[b] - pair_freq[a, b]
            Nab = pair_freq[a, b]
            new_gp = BinaryGP()
            if Na + Nb + Nab > 0:
                new_gp.Pa = Na / (Na + Nb + Nab)
                new_gp.Pb = Nb / (Na + Nb + Nab)
                new_gp.Pab = Nab / (Na + Nb + Nab)
            else:
                new_gp.Pa = 0
                new_gp.Pb = 0
                new_gp.Pab = 0
            new_gp.childA = var_polynomial[a]
            new_gp.childB = var_polynomial[b]
            new_gp.var_A = var_group[a]
            new_gp.var_B = var_group[b]

            temp = var_group[a].copy()
            temp.extend(var_group[b].copy())
            new_gp.var_total = temp
            new_var_group.append(temp)

            new_var_polynomial.append(new_gp)
        for i in group_index:
            new_var_group.append(var_group[i])
            new_var_polynomial.append(var_polynomial[i])
        var_group = new_var_group
        var_polynomial = new_var_polynomial

    return var_polynomial[0]


if __name__ == '__main__':
    # NUM_ITEM = 1362
    NUM_ITEM = 4627
    file_path = "dataset/HKTVmall.txt"
    root_path = "HKTVmall_root.pickle"

    # root = build_root(NUM_ITEM, file_path)
    # f = open(root_path, 'wb')
    # pickle.dump(root, f)

    f = open(root_path, "rb")
    root = pickle.load(f)

    # calculate by file
    # total_length = check_length(root, file_path)
    # print(total_length)

    #  calculate by model
    from AC_single_based_length import get_the_item_frequency_and_num_of_set_by_scan_the_file
    _, num_set = get_the_item_frequency_and_num_of_set_by_scan_the_file(file_path, NUM_ITEM)
    total_entropy = model_entropy(root)
    total_length = total_entropy * num_set
    print(total_length)
