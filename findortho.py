#!/bin/env python3
import argparse
import subprocess
from pathlib import Path

def cli_parse():
    """Genome sequence CLI parsing."""
    parser = argparse.ArgumentParser(description='find reciprocal best hits')
    parser.add_argument('-i1',
                        required=True,
                        help='first input sequence file')
    parser.add_argument('-i2',
                        required=True,
                        help='second input sequence file')
    parser.add_argument('-o',
                        required=True,
                        help='output file')
    parser.add_argument('-t',
                        required=True,
                        choices=['n','p'],
                        help='p for protein, n for nucleotide')
    
    return parser.parse_args()

def cleanup():
    delete = {'.nhr','.nin','.nsq'}
    for p in Path.cwd().iterdir():
        if p.suffix in delete:
            p.unlink()

def make_db(in_file, sequence):
    v = subprocess.check_output(['makeblastdb',
                                 '-in',
                                 in_file,
                                 '-dbtype',
                                 sequence
                                 ])

def make_blast(param_one, param_two):
    return subprocess.check_output(['blastn',
                                    '-query',
                                    param_one,
                                    '-db',
                                    param_two,
                                    '-outfmt',
                                    '6 qseqid sseqid pident qcovs'
                                    ])

def best_hits(found_hits):
    pairs = {}
    for line in found_hits.split('\n'):
        i = line.split('\t')
        if i[0] not in pairs or (i[0] in pairs and pairs[i[0]][1] < i[2]):
            pairs[i[0]] = i[1], i[2]
    return pairs

def blast(parse_info):
    """Comment"""
    if parse_info.t == 'n':
        seq = 'nucl'
    else:
        seq = 'prot'

    make_db(parse_info.i1,seq)
    make_db(parse_info.i2,seq)
    save_one = make_blast(parse_info.i1, parse_info.i2)
    save_two = make_blast(parse_info.i2, parse_info.i1)

    str_one = save_one.decode('utf-8').strip()
    str_two = save_two.decode('utf-8').strip()

    input_one = best_hits(str_one)
    input_two = best_hits(str_two)
    
    with open(parse_info.o, 'w') as writer:
        for i, j in input_one.items():
            if j[0] in input_two and input_two[j[0]][0] == i:
                writer.write(i + '\t' + j[0] + '\n')

def main():
    parsed = cli_parse()
    blast(parsed)
    cleanup()

if __name__ == "__main__":
    main()
