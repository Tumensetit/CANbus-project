# Ohjeet:

Ohjelma tallentaa dekoodauksen tuloksen json-formaatissa, ja tulostaa tilastot näytölle.

Tarvittavien python kirjastojen asentaminen:
Navigoi CMD:ssä projektin kansioon, polun pitäisi näyttää kutakuinkin tältä: C:\CANbus\CANbus-project>
suorita seuraava komento:
pip install -r requirements.txt

Käyttöohje löytyy ohjelmasta:
% python3 src/main.py --help

Esimerkki:
python3 src/main.py -i <datatiedosto> -d data/toyota_rav4_hybrid_2017_pt_generated.dbc -Q BREAK --diffpriv

