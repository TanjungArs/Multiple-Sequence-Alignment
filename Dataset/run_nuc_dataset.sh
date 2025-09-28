#!/bin/bash

#=======================================================
# SKRIP EKSEKUSI FINAL - OTOMASI DENGAN LOGIKA DINAMIS
#=======================================================

echo "🚀 Memulai Produksi Dataset Lengkap..."

# --- Konfigurasi ---
images="sparta_edit" 
Output="dataset"
mkdir -p "$Output"
NUM_SAMPLE=1000 

# --- Definisi Skenario dari Tabel ---
# Format: "NAMA; min_seq_len; max_seq_len; min_br; max_br; min_ir; max_ir; min_a; max_a; num_seq"
declare -a SCENARIOS=(
    "ND1;50;60;0.03;0.1;0.0;0.05;1.01;2.0;2"
    "ND2;100;300;0.03;0.3;0.0;0.05;1.01;2.0;2"
    "ND3;200;300;0.3;0.6;0.04;0.05;1.01;2.0;2"
    "ND4;50;60;0.1;0.3;0.04;0.05;1.01;2.0;3"
    "ND5;50;80;0.15;0.15;0.5;0.5;1.0;1.01;3"
    "ND6;50;80;0.15;0.15;0.5;0.5;1.01;1.01;3"
    "ND7;50;80;0.15;0.15;0.5;0.5;1.5;1.5;3"
    "ND8;50;80;0.05;0.1;0.0;0.05;1.01;2.0;4"
    "ND9;50;80;0.05;0.1;0.03;0.05;1.01;2.0;4"
    "ND10;50;80;0.07;0.1;0.0;0.05;1.01;2.0;5"
    "ND11;50;80;0.08;0.09;0.03;0.05;1.01;2.0;5"
    "ND12;50;80;0.09;0.09;0.04;0.04;1.3;1.3;5"
    "ND13;50;80;0.05;0.1;0.02;0.03;1.0;1.1;4"
    "ND14;50;80;0.9;0.9;0.01;0.02;1.35;1.45;5"
    "ND15;50;80;0.07;0.1;0.0;0.05;1.01;2.0;7"
    "ND16;70;100;0.07;0.1;0.0;0.05;1.01;2.0;7"
)

for scenario in "${SCENARIOS[@]}"; do
    IFS=';' read -r NAMA MIN_SL MAX_SL MIN_BR MAX_BR MIN_IR MAX_IR MIN_A MAX_A NUM_SEQ <<< "$scenario"
    
    OUTPUT_SKENARIO="${Output}/${NAMA}"
    mkdir -p "$OUTPUT_SKENARIO"

    echo ""
    echo "--- Menjalankan Skenario: $NAMA ---"
    
    docker run --rm \
        -v "$(pwd)/${OUTPUT_SKENARIO}":/input \
        -v "$(pwd)":/app \
        --entrypoint python3 \
        "$images" \
        /app/msa_nuc.py \
        "$NAMA" \
        /input/ \
        "$MIN_SL" "$MAX_SL" \
        "$MIN_BR" "$MAX_BR" \
        "$NUM_SAMPLE" \
        "$MIN_IR" "$MAX_IR" \
        "$MIN_A" "$MAX_A" \
        "$NUM_SEQ"
done

echo ""
echo "✅ Semua skenario ND telah selesai dijalankan."