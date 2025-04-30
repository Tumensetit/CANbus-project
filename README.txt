Instructions:

This application saves the results of decoding process in json format, and prints the statistics.

To install python package:
Navigate to the project folder in command prompt, and the path should be something like: "C:\CANbus\CANbus-project>"
Run these commands:
% pip install -r requirements.txt
% pip install .

User guide can also be found in the application:
% canbusdecoder --help

Arguments: (print from help command):
  -h, --help                  >  show this help message and exit

Required arguments:
  -i, --inputfile INPUTFILE   >  Name of the file that contains the data in the specified .tsv format
  -d, --dbcfile DBCFILE       >  Name of the file that is used to decode the inputfile(ends in .dbc)

Optional arguments:
  --list-message-names        >  List all available message names in a dbc file (requires dbcfile file)
  -q, --query QUERY           >  Filter result by ECU (message name). See --list-message-names.
  --diffpriv                  >  Print experimental diffpriv mean
  --vss                       >  Experimental: map DBC signals to VSS paths
  -o, --outputfile OUTPUTFILE >  Output file for saving decoded data (default: decoder_output.json)

Example (Linux/mac):
## To change raw data to understandable format:
% ./src/raakadata_konversio.sh src/dump100000.pcapng <data_file.tsv>
## Decode:
% canbusdecoder -i <data_file.tsv> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc -Q BREAK --diffpriv

If problems while running raakadata_konversio.sh > see docs\tshark_conversion_windows.txt

Running automatic tests:

% pytest
OR:
% python tests/unit_test.py

This runs a handful of tests, that for now tests the correctness of CanID and VSS, and the correctness of prints of the stats-module, thus testing some of the application features on visual level.
After running the tests, application prints results of the tests to terminal, which includes amount of successful tests and why test failed if they failed.

## Applied demo
1. Downloading of raw data file
2. Downloading of GIT-repository
3. In CMD root folder pip install -r requirements.txt and pip install .
4. Decompressing the data file to a data folder
5. Tshark conversion in windows instructions
6. In CMD root folder: canbusdecoder -i <data_file.tsv> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc
7. Faced problems, which were fixed, after which git-repository was updated and reinstalled using: "pip uninstall canbusdecoder" and "pip install ."
8. Afterwards canbusdecoder command again: canbusdecoder -i <data_file.tsv> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc

--------------------

IN FINNISH BELOW

--------------------

# Ohjeet:

Ohjelma tallentaa dekoodauksen tuloksen json-formaatissa, ja tulostaa tilastot näytölle.

Tarvittavien python kirjastojen asentaminen:
Navigoi CMD:ssä projektin kansioon, polun pitäisi näyttää kutakuinkin tältä: C:\CANbus\CANbus-project>
Python paketin asentamiseksi suorita seuraavat komentot:
% pip install -r requirements.txt
% pip install .

Käyttöohje löytyy ohjelmasta:
% canbusdecoder --help

Argumenttien selitykset (help-komennon tuloste):
  -h, --help                  >  show this help message and exit

Required arguments:
  -i, --inputfile INPUTFILE   >  Name of the file that contains the data in the specified .tsv format
  -d, --dbcfile DBCFILE       >  Name of the file that is used to decode the inputfile(ends in .dbc)

Optional arguments:
  --list-message-names        >  List all available message names in a dbc file (requires dbcfile file)
  -q, --query QUERY           >  Filter result by ECU (message name). See --list-message-names.
  --diffpriv                  >  Print experimental diffpriv mean
  --vss                       >  Experimental: map DBC signals to VSS paths
  -o, --outputfile OUTPUTFILE >  Output file for saving decoded data (default: decoder_output.json)

Esimerkki (linux/mac):
## Muuta raakadata ohjelman ymmärtämään muotoon:
% ./src/raakadata_konversio.sh src/dump100000.pcapng <datatiedosto.tsv>
## Dekoodaa
% canbusdecoder -i <datatiedosto.tsv> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc -Q BREAK --diffpriv

Jos raakadata_konversio.sh ajon kanssa ongelmia > katso docs\tshark_conversion_windows.txt

Automaattitestien ajo:

% pytest
tai:
% python tests/unit_test.py

Ajaa muutaman valmiin testin, jotka testaavat CanID:n oikeellisuutta sekä vss ja stats moduulien tulostuksien oikeellisuutta, ja täten samalla niiden toimivuutta näkyvällä tasolla.
Testien ajon jälkeen tulostaa terminaaliin läpäistyjen testien määrän suhteessa kaikkien testien määrään, ja tulostaa virheet läpäisemättömien testien epäonnistumisien kohdalla.

## Suoritettu demo
1. Raakadata tiedoston lataus
2. Gitrepon lataus
3. CMD:ssä root kansiossa pip install -r requirements.txt ja pip install .
4. Raakadatan purku data kansioon
5. Tshark konversio windows ohjeilla
6. CMD:ssä root kansiossa canbusdecoder -i <datatiedosto.tsv> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc
7. Törmäsimme ongelmiin, jotka korjasimme, jonka jälkeen päivitettiin gitrepo ja asennettiin 
   uudelleen käyttäen pip uninstall canbusdecoder ja pip install .
8. Sitten canbusdecoder komento uudelleen: canbusdecoder -i <datatiedosto.tsv> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc
