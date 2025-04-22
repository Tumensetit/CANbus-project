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

Tällä hetkellä stats.py ei toimi kunnolla jos unix_epoch ei muutu tarpeeksi datatiedoston sisällä.
Jos raakadata_konversio.sh ajon kanssa ongelmia > katso docs\tshark_konversio_ohje_windows.txt

## Automaattitestien ajo:

% pytest

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