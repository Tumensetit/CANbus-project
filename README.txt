# Ohjeet:

Ohjelma tallentaa dekoodauksen tuloksen json-formaatissa, ja tulostaa tilastot näytölle.

Tarvittavien python kirjastojen asentaminen:
Navigoi CMD:ssä projektin kansioon, polun pitäisi näyttää kutakuinkin tältä: C:\CANbus\CANbus-project>
suorita seuraava komento:
% pip install -r requirements.txt
% pip install .

Käyttöohje löytyy ohjelmasta:
% canbusdecoder --help

Esimerkki (linux/mac):
## Muuta raakadata ohjelman ymmärtämään muotoon:
% ./src/raakadata_konversio.sh src/dump100000.pcapng <datatiedosto.tsv>
## Dekoodaa
% canbusdecoder -i <datatiedosto.tsv> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc -Q BREAK --diffpriv


## Automaattitestien ajo:

% pytest
