# this file calculate the bits-back performance
import numpy as np
from utility import line_to_set, log_factorial, x_log2_x
from tqdm import tqdm
import pickle
import random
import time
from scl.compressors.arithmetic_coding import ArithmeticEncoder, ArithmeticDecoder, AECParams
from scl.core.data_block import DataBlock
from scl.core.prob_dist import Frequencies
from scl.compressors.probability_models import FixedFreqModel


def time_cost(file_path, item_freq, num_set):
    bit_back_gain = 0
    data_list = []
    length = 0
    count = 0
    encode_time = 0
    decode_time = 0
    start_time = time.time()
    with open(file_path, "r") as f:
        for line in f.readlines():
            count += 1
            if count > num_set:
                break
            set_list = line_to_set(line)
            set_list.sort()
            bit_back_gain += log_factorial(len(set_list))
            while len(set_list) > 0:
                x = random.choice(set_list)
                data_list.append(x)
                set_list.remove(x)
            data_list.append(0)
    end_time = time.time()
    encode_time += end_time - start_time
    # encoding
    start_time = time.time()
    code_freq_dict = {}
    for i in range(len(item_freq)):
        code_freq_dict[i] = int(item_freq[i])
    freq = Frequencies(code_freq_dict)
    params = AECParams()
    # create encoder decoder
    freq_model_enc = FixedFreqModel(freqs_initial=freq, max_allowed_total_freq=params.MAX_ALLOWED_TOTAL_FREQ)

    # create encoder
    encoder = ArithmeticEncoder(params, freq_model_enc)
    data_block = DataBlock(list(data_list))
    encoded_bitarray = encoder.encode_block(data_block)

    end_time = time.time()
    encode_time += end_time - start_time
    length = len(encoded_bitarray)

    # decoding
    start_time = time.time()
    code_freq_dict = {}
    for i in range(len(item_freq)):
        code_freq_dict[i] = int(item_freq[i])
    freq = Frequencies(code_freq_dict)
    params = AECParams()
    freq_model_enc = FixedFreqModel(freqs_initial=freq, max_allowed_total_freq=params.MAX_ALLOWED_TOTAL_FREQ)

    # create decoder
    decoder = ArithmeticDecoder(params, freq_model_enc)
    decoded_data_list, num_bits_consumed = decoder.decode_block(encoded_bitarray)
    end_time = time.time()
    decode_time += end_time - start_time

    start_time = time.time()
    f = open("decode.txt", 'w')
    symbol_list = decoded_data_list.data_list
    for symbol in symbol_list:
        if int(symbol) != 0:
            f.write(str(symbol))
            f.write(' ')
        else:
            f.write('\n')
    f.close()
    end_time = time.time()
    decode_time += end_time - start_time
    print(encode_time)
    print(decode_time)
    return length, bit_back_gain


if __name__ == '__main__':
    # dir_path = "../dataset/Tmall_shuffle.txt"
    dir_path = "../dataset/HKTVmall_shuffle.txt"
    # num_item = 1361+1
    # total_num_set = 5446607

    num_item = 4627
    total_num_set = 52046411

    # item_freq, num_set = get_the_item_frequency_and_num_of_set_by_scan_the_file(dir_path, num_item)
    # with open("Tmall_item_freq", "wb") as f:
    #     pickle.dump(item_freq, f)

    # f = open("Tmall_item_freq", "rb")
    f = open("HKTVmall_item_freq", "rb")
    item_freq = pickle.load(f)
    item_freq[0] = total_num_set
    # print(item_freq)

    for num_set in [total_num_set]:
        print(num_set)
        length, bit_back_gain = time_cost(dir_path, item_freq, num_set)
        print(length-bit_back_gain)
