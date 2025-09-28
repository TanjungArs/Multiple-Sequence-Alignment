# Nama file: msa_nuc.py
from pipeline_click import pipeline
import sys
import os
import random
import string
import json
from ete3 import Tree

flag = sys.argv[1]
path = sys.argv[2]
min_seq_length = int(sys.argv[3])
max_seq_length = int(sys.argv[4])
min_brach_length = float(sys.argv[5])
max_brach_length = float(sys.argv[6])
num_of_samples = int(sys.argv[7])
input_minIR = float(sys.argv[8])
input_maxIR = float(sys.argv[9])
input_minAVal = float(sys.argv[10])
input_maxAVal = float(sys.argv[11])
num_of_sequences = int(sys.argv[12])

pipeline_path = f"/app/"
res_path = f"{path}res_{flag}"
data_set_path = f"{path}data_set_{flag}"

if not os.path.isdir(res_path):
    os.mkdir(res_path)
if not os.path.isdir(data_set_path):
    os.mkdir(data_set_path)

msa_filename = "temp_msa.fasta"
tree_filename = "temp_tree.tree"
msa_path = os.path.join(res_path, msa_filename)
tree_path = os.path.join(res_path, tree_filename)

file_output_path = os.path.join(data_set_path, f'all_data_{num_of_samples}.json')
all_data = []
succes_id = []
fail_id = []

for sample in range(num_of_samples):
    seq_length = random.randint(min_seq_length, max_seq_length)
    calculated_minRL = seq_length * 0.8
    calculated_maxRL = seq_length * 1.1
    t = Tree()
    seq_names = list(string.ascii_uppercase[:num_of_sequences])
    t.populate(num_of_sequences, seq_names)
    for node in t.traverse():
        if not node.is_root():
            node.dist = random.uniform(min_brach_length, max_brach_length)
    tree = t.write(format=1)
    
    with open(tree_path,'w') as f:
        f.write(tree)
    with open(msa_path,'w') as f:
        for name in seq_names:
            f.write(f">{name}\n")
            f.write("T"*seq_length + "\n")

    skip_config = { "sparta": True, "mafft": True, "inference": True , "correct_bias": True }
    submodel_params_ = {
        "mode": "nuc", "submodel": "GTR",
        "freq": (0.369764, 0.165546, 0.306709, 0.157981),
        "rates": (0.443757853, 0.084329474, 0.115502265, 0.107429571, 0.000270340),
        "inv_prop": 0.0, "gamma_shape": 99.852225, "gamma_cats": 4
    }
    res_dir = res_path
    clean_run = False
    op_sys= 'linux'
    minIR=input_minIR
    maxIR=input_maxIR
    minAVal=input_minAVal
    maxAVal=input_maxAVal
    verbose = 0
    b_num_top=1
    num_alignments = 1
    filter_p = (0.9,15)
    num_simulations = 1
    num_burnin = 1
    
    try :
        unaligned_msa, aligned_msa, structure_msa = pipeline(
            skip_config=skip_config, pipeline_path=pipeline_path, res_dir=res_dir, 
            clean_run=False, msa_filename=msa_filename, tree_filename=tree_filename,
            minIR=input_minIR, maxIR=input_maxIR, 
            minAVal=input_minAVal, maxAVal=input_maxAVal,
            minRL=calculated_minRL, maxRL=calculated_maxRL, 
            op_sys='linux', verbose=0, b_num_top=1,
            num_alignments=1, filter_p=(0.9,15), 
            submodel_params=submodel_params_, num_simulations=1,
            num_burnin=1)
    except Exception as e : 
        print(f"PERINGATAN : Gagal menjalankan pipeline {e}")
        fail_id.append(sample+1)
        continue

    # Membaca statistik seperti biasa
    params_file = os.path.join(res_path, 'SpartaABC_data_name_iddif.posterior_params')
    try:
        with open(params_file, 'r') as f_params:
            summary_stat = f_params.readlines()[4][:-1].split("\t")[1:]
    except (FileNotFoundError, IndexError) as e:
        print(f"  -> PERINGATAN: Gagal membaca file parameter: {e}")
        fail_id.append(sample+1)
        continue


    param_values = ", ".join(summary_stat)
    tree_str = tree

    # Membersihkan header dari setiap MSA
    structure_content = [line.strip() for line in structure_msa.split('\n') if not line.startswith('>') and line.strip()]
    aligned_content = [line.strip() for line in aligned_msa.split('\n') if not line.startswith('>') and line.strip()]
    unaligned_content = [line.strip() for line in unaligned_msa.split('\n') if not line.startswith('>') and line.strip()]

    # Buat JSON
    data_json = {
    "sample_msa_id": sample + 1,
    "parameter": [param_values, tree],
    "unalign": unaligned_content,
    "aligned": aligned_content,
    "structure": structure_content 
    }

    all_data.append(data_json)
    succes_id.append(sample + 1)
    print(f"Sample {sample+1}/{num_of_samples} selesai.")

    save_interval = 100
    if (sample + 1) % save_interval == 0 or (sample + 1) == num_of_samples:
        with open(file_output_path, 'w') as f:
            json.dump(all_data, f, indent=2)
        print(f"\nProgress {sample+1}: Output ditulis ke {file_output_path} \n")

print(f"Total Berhasil : {len(succes_id)} sample ")
print(f"Total Gagal : {len(fail_id)} sample ")
if fail_id:
    print(f"ID Gagal : {fail_id}")
