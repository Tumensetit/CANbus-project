# Ohjeet:

# Raakadatan konversio tsharkilla:
src/raakadata_konversio.sh /path/to/can_dump.pcapng /path/to/candump_parsed.tsv

# .tsv -muotoisen tiedon dekoodaus:
python3 src/decoder.py /path/to/candump_parsed.tsv ./data/toyota_rav4_hybrid_2017_pt_generated.dbc

.. Toistaiseksi tulostaa näytölle. TODO: tulostus tiedostoon, filtteröinti.

# Visualisoi:
python3 src/visualizer.py input_from_decoder output.png

