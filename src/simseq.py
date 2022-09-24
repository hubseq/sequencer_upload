#
# simseq
#
# Simulate raw file output coming off the sequencer.
#
import os, sys, random, string, gzip, subprocess
from scipy.stats import skewnorm

# CREATE_DIR_FREQ = 0.1  # frequency of putting a newly created file into a new directory
BINARY_FILE_FREQ = 0.2 # frequency of creating a binary file (as opposed to a text file)
RANDOM_CHARS = string.ascii_letters + string.digits
SMALL_FILE_BURST_SIZE = 200
FINAL_FILE = 'RTAComplete.txt'

def makeNewFile( file_size_chars, bin_freq, output_dir, f_num, fast=True, f_name = 'default'):
    """
    if bin_freq < BINARY_FILE_FREQ:
        with gzip.open("{}/f{}.gz".format(output_dir, str(f_num+1)), 'wt') as fout:
            fout.write(''.join(random.choices(RANDOM_CHARS, k = file_size_chars)))
    else:
        with open("{}/f{}.txt".format(output_dir, str(f_num+1)), 'w') as fout:
            fout.write(''.join(random.choices(RANDOM_CHARS, k = file_size_chars)))
    """
    if f_name == 'default' and fast == True:
        filename = 'f{}.bin'.format(str(f_num))
        subprocess.call("dd if=/dev/urandom of={}/{} bs=10k count={}".format(output_dir, filename, str(int(file_size_chars/10))), shell=True)        
    elif f_name == 'default' and fast != True:        
        filename = 'f{}.gz'.format(str(f_num))
        with gzip.open("{}/{}".format(output_dir, filename), 'wt') as fout:
            for r in range(0,int(file_size_chars/10)):
                fout.write(''.join(random.choices(RANDOM_CHARS, k = 10000)))        
    else:
        filename = f_name
        subprocess.call('touch {}/{}'.format(output_dir, filename), shell=True)
    return f_num + 1


def simseq( num_files, max_chars, output_dir = '.', speed = 'fast' ):
    # d_num = 1
    num_files = int(num_files)
    max_chars = int(max_chars)
    numValues = 1000
    file_size_fractions_list = [[], []]
    
    # skewed towards larger file sizes
    maxValue = 100
    skewness = 5     # skewed towards smaller files
    file_size_fractions = skewnorm.rvs(a = skewness,loc=maxValue, size=numValues)
    file_size_fractions = file_size_fractions - min(file_size_fractions)
    file_size_fractions_list[0] = list( file_size_fractions / max(file_size_fractions))
        
    skewness = -5    # slightly skewed towards larger numbers greater than 0.5*max_chars
    file_size_fractions = skewnorm.rvs(a = skewness,loc=maxValue, size=numValues)
    file_size_fractions = file_size_fractions - min(file_size_fractions)
    file_size_fractions_list[1] = list( file_size_fractions / max(file_size_fractions))

    # create dir if does not exist
    if output_dir != '.' and output_dir not in os.listdir():
        os.mkdir(output_dir)

    f_num = 0
    while f_num < num_files:
        print('FNUM: {}'.format(str(f_num)))
        bin_freq = random.uniform(0,1)
        # dir_freq = random.uniform(0,1)
        small_or_large = random.randint(0,1)  # 0 is small files, 1 is large files
        if small_or_large == 0:
            # for small files, let's "burst" the output of small files and test how sync handles this
            burst_size = int(random.uniform(0,1)*min(SMALL_FILE_BURST_SIZE, num_files - f_num - 1))
            print('BURSTING! {} small files'.format(burst_size))
            for i in range(0,int(burst_size)):
                file_size_chars = int(file_size_fractions_list[0][random.randint(0,numValues)]*max_chars)  # number of chars in this file
                f_num = makeNewFile( file_size_chars, bin_freq, output_dir, f_num, True if speed.lower() == 'fast' else False )
        else:
            # for large files, just output that file
            file_size_chars = int(file_size_fractions_list[1][random.randint(0,numValues)]*max_chars)  # number of chars in this file
            f_num = makeNewFile( file_size_chars, bin_freq, output_dir, f_num, True if speed.lower() == 'fast' else False )
    # final output file
    makeNewFile( 0, bin_freq, output_dir, f_num, True, FINAL_FILE )
    return


if __name__ == '__main__':
    print('$ python simseq.py <NUM_FILES> <MAX_FILE_SIZE_IN_KB> <OUTPUT_DIR> <fast/slow>')
    if len(sys.argv) == 5:
        simseq( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
    elif len(sys.argv) == 4:
        simseq( sys.argv[1], sys.argv[2], sys.argv[3] )
    elif len(sys.argv) == 3:
        simseq( sys.argv[1], sys.argv[2] )        


