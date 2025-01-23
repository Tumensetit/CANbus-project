#!/bin/bash

# Tämä pipeline yhdistää kaikki yksittäiset osat

#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Give the .pcapng raw data file as an argument"
    echo "Usage: $0 <file-name.pcapng>"
    exit 1
fi

RAAKADATA=$1
DBC=../data/toyota_rav4_hybrid_2017_pt_generated.dbc

RAAKADATA_KONVERSIO=tmp_raakadata_konversio.tsv
DEKOODATTU=tmp_dekoodattu.txt
KUVATIEDOSTO=output.png

echo "Starting pipeline"
./raakadata_konversio.sh $RAAKADATA $RAAKADATA_KONVERSIO
python3 ./decoder.py $RAAKADATA_KONVERSIO $DEKOODATTU
python3 visualizer.py $DEKOODATTU $KUVATIEDOSTO
echo "Pipeline done!"
