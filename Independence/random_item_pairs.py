import random
import pickle

# NUM_ITEM = 1362
# file_path = "Tmall_pairs.pickle"

NUM_ITEM = 4627
file_path = "HKTVmall_pairs.pickle"

random.seed(1234)
num_pairs = 100
pair_list = []
for i in range(num_pairs):
    a = random.randint(0,NUM_ITEM-1)
    while True:
        b = random.randint(0,NUM_ITEM-1)
        if b != a:
            break
    pair_list.append([a, b])
print(pair_list)

f = open(file_path, 'wb')
pickle.dump(pair_list, f)
