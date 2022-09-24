#
# Creates a simulated FASTQ for testing.
#
# Takes a setup config YAML or JSON as input.
# Requires package pyyaml.
#
import sys, os, json, yaml, random, gzip
import seq_constants as sc

def create_fastq_yaml( fastq_out, setup_yaml ):
    """ Takes YAML as input. Converts YAML input into a dictionary. Specifications are in create_fastq().
    """
    # parse YAML into a dictionary
    with open(setup_yaml,'r') as f:
        create_fastq( fastq_out, yaml.safe_load(f) )

    return

def create_fastq_json( fastq_out, setup_json ):
    """ Takes JSON as input. Converts JSON input into a dictionary. Specifications are in create_fastq().
    """
    # parse JSON into a dictionary

    return

def create_fastq( fastq_out, setup_dict ):
    """ Creates a simulated FASTQ file. Input is a Python dictionary. Also generates a log file of settings.
    Options are:
    sequencer: Illumina, PacBio, ONP
    paired-end: true or false
    num-reads: INT
    read-length: INT
    stdev-read-length: INT (0 = constant read length)
    min-quality-score: INT (min quality score)
    max-quality-score: INT (max quality score. If min=max, then quality score is constant.)
    compress: output a compressed FASTQ file, true or false
    instrument-id: STR
    run-id: INT or STR
    flowcell-id: STR
    flowcell-lane: INT
    tile-number: INT
    clusterx: INT
    clustery: INT
    barcode-i5: STR
    barcode-i7: STR
    allow-N: allow N in sequence, true or false
    filtered: are reads pre-filtered, true or false (almost always false)
    """
    def getFileName( fin ):
        """ Strips any FASTQ file extension
        """
        if fin.endswith('.fastq'):
            return fin[0:-6]
        elif fin.endswith('.fq'):
            return fin[0:-3]
        elif fin.endswith('.fastq.gz'):
            return fin[0:-9]
        elif fin.endswith('.fq.gz'):
            return fin[0:-6]
        else:
            return fin

    # defaults
    sequencer = 'Illumina'
    fastq_out_filename = getFileName(fastq_out)

    if str(setup_dict.get('sequencer', sequencer)).lower() == 'illumina':
        settings = create_fastq_illumina( fastq_out_filename, setup_dict )

    # write log of settings
    with open(fastq_out_filename+'.create_fastq.log','w') as fout:
        json.dump(settings, fout)
    
    return


def create_fastq_illumina( fastq_out, setup_dict ):
    """ Creates an Illumina-specific FASTQ file. Input is a Python dictionary of settings.
    """
    def isPairedEnd( paired_end ):
        if str(paired_end).lower() in ['true', 't', 'y', 'yes']:
            return True
        else:
            return False
    
    # defaults
    defaults = {'compress': 'true' if 'compress' not in setup_dict else setup_dict['compress'],
                'paired_end': 'false' if 'paired-end' not in setup_dict else setup_dict['paired-end'],
                'instrument_id': 'HWI-ST08' if 'instrument-id' not in setup_dict else setup_dict['instrument-id'],
                'run_id': 1 if 'run-id' not in setup_dict else setup_dict['run-id'],
                'flowcell_id': 'C0N4WACXN' if 'flowcell-id' not in setup_dict else setup_dict['flowcell-id'],
                'flowcell_lane': 1 if 'flowcell-lane' not in setup_dict else setup_dict['flowcell-lane'],
                'tile_number': 1101 if 'tile-number' not in setup_dict else setup_dict['tile-number'],
                'cluster_x': 2819 if 'clusterx' not in setup_dict else setup_dict['clusterx'],
                'cluster_y': 6798 if 'clustery' not in setup_dict else setup_dict['clustery'],
                'filtered': 'N' if 'filtered' not in setup_dict else setup_dict['filtered'],
                'barcode_i5': 'AGTCTAGA' if 'barcode-i5' not in setup_dict else setup_dict['barcode-i5'],
                'barcode_i7': 'CGTAGTAC' if 'barcode-i7' not in setup_dict else setup_dict['barcode-i7'],
                'read_length': 150 if 'read-length' not in setup_dict else setup_dict['read-length'],
                'num_reads': 100 if 'num-reads' not in setup_dict else setup_dict['num-reads'],
                'stdev_read_length': 0 if 'stdev-read-length' not in setup_dict else setup_dict['stdev-read-length'],
                'min_qscore': 32 if 'min-quality-score' not in setup_dict else setup_dict['min-quality-score'],
                'max_qscore': 32 if 'max-quality-score' not in setup_dict else setup_dict['max-quality-score'],
                'allow_N': 'false' if 'allow-N' not in setup_dict else setup_dict['allow-N']}

    # output stream
    if isPairedEnd(defaults['paired_end']):
        fout = gzip.open(fastq_out+'-R1.fastq.gz', 'wt') if defaults['compress'] in ['true', 't', 'y', 'yes'] else open(fastq_out+'-R1.fastq','w')
        fout2 = gzip.open(fastq_out+'-R2.fastq.gz', 'wt') if defaults['compress'] in ['true', 't', 'y', 'yes'] else open(fastq_out+'-R2.fastq','w')
    else:
        fout = gzip.open(fastq_out+'.fastq.gz', 'wt') if defaults['compress'] in ['true', 't', 'y', 'yes'] else open(fastq_out+'.fastq','w')
        fout2 = None

    for n in range(int(defaults['num_reads'])):
        # create header
        header = '@'
        header_3p = ''

        header += defaults['instrument_id']+':'
        header += str(defaults['run_id'])+':'
        header += str(defaults['flowcell_id'])+':'
        header += str(defaults['flowcell_lane'])+':'
        header += str(defaults['tile_number'])+':'
        header += str(defaults['cluster_x'])+':'
        header += str(defaults['cluster_y'])

        if isPairedEnd(defaults['paired_end']):
            header_3p = header
            header += ' 1:'+str(defaults['filtered'])+':0:'
            header_3p += ' 2:'+str(defaults['filtered'])+':0:'
        else:
            header += ' 1:'+str(defaults['filtered'])+':0:'

        if isPairedEnd(defaults['paired_end']):
            header += str(defaults['barcode_i5'])+'+'
            header += str(defaults['barcode_i7'])
            header_3p += str(defaults['barcode_i5'])+'+'
            header_3p += str(defaults['barcode_i7'])
        else:
            header += str(defaults['barcode_i5'])

        # create sequence
        seq, seq_3p = '', ''
        for i in range(int(defaults['read_length'])):
            if defaults['allow_N'] in ['true', 't', 'y', 'yes']:
                seq += sc.NT_N[random.randint(0,4)]
                if isPairedEnd(defaults['paired_end']):
                    seq_3p += sc.NT_N[random.randint(0,4)]
            else:
                seq += sc.NT[random.randint(0,3)]
                if isPairedEnd(defaults['paired_end']):
                    seq_3p += sc.NT[random.randint(0,3)]

        # plus line
        plus_line = '+'

        # quality score
        qscore, qscore_3p = '', ''
        if defaults['min_qscore'] == defaults['max_qscore']:
            for i in range(int(defaults['read_length'])):
                qscore += sc.QSCORE_INT_TO_ASCII.get(int(defaults['min_qscore']), 'A')
                if isPairedEnd(defaults['paired_end']):
                    qscore_3p += sc.QSCORE_INT_TO_ASCII.get(int(defaults['min_qscore']), 'A')

        # write out read to file
        fout.write(header+'\n'+seq+'\n'+plus_line+'\n'+qscore+'\n')
        if isPairedEnd(defaults['paired_end']):
            fout2.write(header_3p+'\n'+seq_3p+'\n'+plus_line+'\n'+qscore_3p+'\n')
    
    # close file streams and return
    fout.close()
    if fout2 != None:
        fout2.close()
    return defaults

if __name__ == '__main__':
    print('$ create_fastq.py [NAME_OF_FASTQ_PREFIX] [CONFIG_YAML_OR_JSON]')
    print('$ create_fastq.py chipseq_heart myconfig.yaml => outputs chipseq_heart_R1.fastq and chipseq_heart_R2.fastq')
    if len(sys.argv) >= 3:
        if str(sys.argv[2]).endswith('.yaml') or str(sys.argv[2]).endswith('.yml'):
            create_fastq_yaml( sys.argv[1], sys.argv[2] )
        elif str(sys.argv[2]).endswith('.json'):
            create_fastq_json( sys.argv[1], sys.argv[2] )

