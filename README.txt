# Ohjeet:

# Raakadatan konversio tsharkilla:
src/raakadata_konversio.sh /path/to/can_dump.pcapng /path/to/candump_parsed.tsv

# .tsv -muotoisen tiedon dekoodaus:
python3 src/main.py -i /path/to/candump_parsed.tsv -d ./data/toyota_rav4_hybrid_2017_pt_generated.dbc -q SPEED

Ohjelma tallentaa dekoodauksen tuloksen json-formaatissa, ja tulostaa tilastot näytölle.
