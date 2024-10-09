import pickle
import time

import numpy as np
from utility import line_to_set
from tqdm import tqdm
from scl.compressors.arithmetic_coding import ArithmeticEncoder, ArithmeticDecoder, AECParams
from scl.compressors.probability_models import FixedFreqModel
from scl.core.data_block import DataBlock
from scl.core.prob_dist import Frequencies

from queue import Queue


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


class NamedBinaryGP:
    def __init__(self):
        self.Pa = 0
        self.Pb = 0
        self.Pab = 0
        self.childA = None
        self.childB = None
        self.var_A = []
        self.var_B = []
        self.var_total = []
        self.name = 0



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


def get_trinary_array(root, file_path, num_set):
    code_dict = dict()
    stack = list()
    stack.append(root)
    while len(stack) > 0:
        node = stack.pop()
        code_dict[id(node)] = list()
        if node.childB is not None:
            stack.append(node.childB)
        if node.childA is not None:
            stack.append(node.childA)

    with open(file_path, 'r') as f:
        count = 0
        for line in f.readlines():
            count += 1
            if count > num_set:
                break
            set_list = line_to_set(line)
            stack = list()
            stack.append(root)
            while len(stack) > 0:
                bgp = stack.pop()
                flagA = False
                flagB = False
                for item in set_list:
                    if item in bgp.var_A:
                        flagA = True
                    if item in bgp.var_B:
                        flagB = True
                if flagA and flagB:
                    code_dict[id(bgp)].append(2)
                elif flagA and not flagB:
                    code_dict[id(bgp)].append(0)
                elif flagB and not flagA:
                    code_dict[id(bgp)].append(1)
                else:
                    print("Error")
                if flagB:
                    if bgp.childB is not None:
                        stack.append(bgp.childB)
                if flagA:
                    if bgp.childA is not None:
                        stack.append(bgp.childA)
    return code_dict


def time_cost(root, code_dict, total_num_set):
    encode_time = 0
    decode_time = 0
    length = 0
    stack = list()
    stack.append(root)
    decoder_dict = dict()
    while len(stack) > 0:
        node = stack.pop()
        if node.childB is not None:
            stack.append(node.childB)
        if node.childA is not None:
            stack.append(node.childA)

        if len(list(code_dict[id(node)])) == 0:
            decoder_dict[id(node)] = []
            continue

        # encode
        # print("encode start")
        start_time = time.time()
        code_freq_dict = {}
        code_freq_dict[0] = int(node.Pa * total_num_set) + 1
        code_freq_dict[1] = int(node.Pb * total_num_set) + 1
        code_freq_dict[2] = int(node.Pab * total_num_set) + 1
        freq = Frequencies(code_freq_dict)
        params = AECParams()
        # create encoder decoder
        freq_model_enc = FixedFreqModel(freqs_initial=freq, max_allowed_total_freq=params.MAX_ALLOWED_TOTAL_FREQ)

        # create encoder
        encoder = ArithmeticEncoder(params, freq_model_enc)
        data_block = DataBlock(code_dict[id(node)])
        encoded_bitarray = encoder.encode_block(data_block)
        end_time = time.time()

        encode_time += end_time - start_time
        length += len(encoded_bitarray)

        # decode
        start_time = time.time()
        code_freq_dict = {}
        code_freq_dict[0] = int(node.Pa * total_num_set) + 1
        code_freq_dict[1] = int(node.Pb * total_num_set) + 1
        code_freq_dict[2] = int(node.Pab * total_num_set) + 1
        freq = Frequencies(code_freq_dict)
        params = AECParams()
        # create encoder decoder
        freq_model_enc = FixedFreqModel(freqs_initial=freq, max_allowed_total_freq=params.MAX_ALLOWED_TOTAL_FREQ)
        # create encoder
        decoder = ArithmeticDecoder(params, freq_model_enc)
        decoded_data_list, num_bits_consumed = decoder.decode_block(encoded_bitarray)
        decoder_dict[id(node)] = decoded_data_list.data_list
        end_time = time.time()
        decode_time += end_time - start_time
    return encode_time, decode_time, length, decoder_dict


def decode_DFS(root, code_dict, num_set):
    pointer_dict = {}
    for key in code_dict:
        pointer_dict[key] = 0
    f = open("decoded.txt", "w")
    for _ in range(num_set):
        set_list = []
        stack = []
        stack.append(root)
        while len(stack) > 0:
            node = stack.pop()
            index = pointer_dict[id(node)]
            x = code_dict[id(node)][index]
            pointer_dict[id(node)] += 1
            if x == 0:
                if node.childA is not None:
                    stack.append(node.childA)
                else:
                    set_list.append(node.var_A[0])
            elif x == 1:
                if node.childB is not None:
                    stack.append(node.childB)
                else:
                    set_list.append(node.var_B[0])
            else:
                if node.childB is not None:
                    stack.append(node.childB)
                else:
                    set_list.append(node.var_B[0])
                if node.childA is not None:
                    stack.append(node.childA)
                else:
                    set_list.append(node.var_A[0])
        for item in set_list:
            f.write(str(item))
            f.write(' ')
        f.write('\n')


def copy_tree(root: BinaryGP):
    stack = list()
    stack_copy = list()
    stack.append(root)


if __name__ == '__main__':
    # NUM_ITEM = 1362
    NUM_ITEM = 4627
    # file_path = "../dataset/Tmall_shuffle.txt"
    file_path = "../dataset/HKTVmall_shuffle.txt"
    # root_path = "../Tmall_root.pickle"
    root_path = "../HKTVmall_root.pickle"
    # total_num_set = 5446607
    total_num_set = 52046411

    # root = build_root(NUM_ITEM, file_path)
    # f = open(root_path, 'wb')
    # pickle.dump(root, f)

    f = open(root_path, "rb")
    root = pickle.load(f)

    for num_set in [total_num_set]:
        print(num_set)
        # DFS
        start_time = time.time()
        code_dict = get_trinary_array(root, file_path, num_set)
        end_time = time.time()
        DFS_time = end_time - start_time
        print(DFS_time)
        encode_time, decode_time, length, decoder_dict = time_cost(root, code_dict, total_num_set)
        print(encode_time)
        print(decode_time)

        start_time = time.time()
        decode_DFS(root, decoder_dict, num_set)
        # decode_DFS(root, code_dict, num_set)
        end_time = time.time()
        DFS_time = end_time - start_time
        print(DFS_time)
        print(length)
