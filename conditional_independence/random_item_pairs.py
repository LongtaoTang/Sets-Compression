import random
import pickle

from generating_polynomial import BinaryGP

# NUM_ITEM = 1362
# file_path = "Tamll_condition_pairs.pickle"
# root_path = "../Tmall_root.pickle"

NUM_ITEM = 4627
file_path = "HKTVmall_condition_pairs.pickle"
root_path = "../HKTVmall_root.pickle"

random.seed(1234)
f = open(root_path, 'rb')
root = pickle.load(f)

num_pairs = 100
pair_list = []
for i in range(num_pairs):
    a = random.randint(0,NUM_ITEM-1)
    while True:
        b = random.randint(0,NUM_ITEM-1)
        if b != a:
            break
    condition_setA = []
    condition_setB = []
    # print(a)
    # print(b)
    node:BinaryGP = root
    while True:
        if a in node.var_A:
            if b in node.var_B:
                condition_setA = node.var_A
                condition_setB = node.var_B
                break
            else:
                node = node.childA
        else:
            if b in node.var_A:
                condition_setA = node.var_B
                condition_setB = node.var_A
                break
            else:
                node = node.childB

    pair_list.append([a, b, condition_setA, condition_setB])
# print(pair_list)

f = open(file_path, 'wb')
pickle.dump(pair_list, f)
