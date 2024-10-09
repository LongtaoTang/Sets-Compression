import os
import pickle
import time

from tqdm import tqdm
import numpy as np
from scl.compressors.arithmetic_coding import ArithmeticEncoder, ArithmeticDecoder, AECParams
# from scl.compressors.rANS import rANSEncoder, rANSDecoder, rANSParams
from scl.core.data_block import DataBlock
from scl.core.prob_dist import Frequencies
from bitarray import bitarray
from scl.compressors.probability_models import FixedFreqModel
from utility import line_to_set


def get_the_item_frequency_and_num_of_set_by_scan_the_file(file_path, num_item):
    item_freq = np.zeros(num_item, dtype=np.int32)
    num_set = 0
    with open(file_path, "r") as f:
        for line in tqdm(f.readlines()):
            num_set += 1
            set_list = line_to_set(line)
            for item in set_list:
                item_freq[item] += 1
    return item_freq, num_set


def compress_a_set_txt_file_by_single_based_by_arithmetic_coding(txt_file_path:str, num_item:int, item_frequency, num_set, total_num_set):
    # modified the item_frequency, so that no zero in the item_frequency
    for i in range(num_item):
        if item_frequency[i] == 0:
            item_frequency[i] = 1

    encode_time = 0
    decode_time = 0
    # coding
    start_time = time.time()
    total_bit_len = 0
    # get 0-1 item_indicator array
    item_indicator = np.zeros(shape=(num_item, num_set), dtype=np.int8)
    decode_item_indicator = np.zeros(shape=(num_item, num_set), dtype=np.int8)
    count_set = 0
    with open(txt_file_path, "r") as f:
        set_index = 0
        for line in f.readlines():
            count_set += 1
            if count_set > num_set:
                break
            set_list = line_to_set(line)
            for item in set_list:
                item_indicator[item, set_index] = 1
            set_index += 1
    end_time = time.time()
    encode_time += end_time - start_time

    for item in range(num_item):
        # encoding
        start_time = time.time()
        code_freq_dict = {}
        code_freq_dict[1] = int(item_frequency[item])
        code_freq_dict[0] = int(total_num_set - item_frequency[item])
        freq = Frequencies(code_freq_dict)
        params = AECParams()
        # create encoder decoder
        freq_model_enc = FixedFreqModel(freqs_initial=freq, max_allowed_total_freq=params.MAX_ALLOWED_TOTAL_FREQ)

        # create encoder
        encoder = ArithmeticEncoder(params, freq_model_enc)
        data_block = DataBlock(list(item_indicator[item]))
        encoded_bitarray = encoder.encode_block(data_block)

        end_time = time.time()
        encode_time += end_time - start_time
        total_bit_len += len(encoded_bitarray)

        # decoding
        start_time = time.time()
        code_freq_dict = {}
        code_freq_dict[1] = int(item_frequency[item])
        code_freq_dict[0] = int(total_num_set - item_frequency[item])
        freq = Frequencies(code_freq_dict)
        params = AECParams()
        freq_model_enc = FixedFreqModel(freqs_initial=freq, max_allowed_total_freq=params.MAX_ALLOWED_TOTAL_FREQ)

        # create decoder
        decoder = ArithmeticDecoder(params, freq_model_enc)
        decoded_data_list, num_bits_consumed = decoder.decode_block(encoded_bitarray)
        for i in range(num_set):
            decode_item_indicator[item, i] = decoded_data_list.data_list[i]
        end_time = time.time()
        decode_time += end_time - start_time

    start_time = time.time()
    f = open("decoder.txt", 'w')
    # one-hot to set
    for set_index in range(num_set):
        for item in range(num_item):
            if decode_item_indicator[item, set_index] == 1:
                f.write(str(item))
                f.write(' ')
        f.write('\n')
    f.close()
    end_time = time.time()
    decode_time += end_time - start_time

    print("encode_time", encode_time)
    print("decode_time", decode_time)
    return total_bit_len


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

    f = open("HKTVmall_item_freq", "rb")
    item_freq = pickle.load(f)

    for num_set in [2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 18000, 20000]:
        print(num_set)
        real_bit_len = compress_a_set_txt_file_by_single_based_by_arithmetic_coding(dir_path, num_item, item_freq,
                                                                                    num_set=num_set,
                                                                                    total_num_set=total_num_set)
        print(real_bit_len)
