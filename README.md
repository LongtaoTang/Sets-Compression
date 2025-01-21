# Sets-Compression
The required package: tqdm, numpy, matplotlib, pickle.

We used python 3.9, but the other version is fine.

## dictionary

### Documents
This dictionary contains the proof of NP-hardness on the improved coding method and more documents.

### stanford_compression_library
The entropy coding interface is from the stanford_compression_library. <https://github.com/kedartatwawadi/stanford_compression_library>

This dictionary is a cloned version of stanford_compression_library.

### dataset
it contains the information of datasets.

### time_cost
it contains the experiments about encoding and decoding times.

### Independence
we conduct the chi-square independence test on the dataset without conditions.

### conditional_independence
we conduct the chi-square independence test on the dataset with conditions.

## codes
### utility.py
some commonly used functions

### generating_polynomial.py
- def build_root(NUM_ITEM, file_path): it build the binary trees, which will output Tmall_root.pickle or HKTVmall_root.pickle.

- if __name__ == '__main__': it calculates the file size by binary tree model. (Ours)

### bits-back performance.py
calculate the performance of the bits-back method

### single_based_length.py
calculate the performance of the single-item-based method

### Makov.py
calculate the performance of the Makov-based method

### group_baseline.py
calculate the performance of the group-based method

### size_distribution.py
it checks the size distribution

## other files

Tmall_root.pickle and HKTVmall_root.pickle are binary trees. 

Tmall1.png, Tmall2.png, Tmall3.png, HKTVmall1.png, HKTVmall2.png, and HKTVmall3.png are figures of size distribution.
