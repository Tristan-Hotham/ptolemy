"""Hand decisions, kept apart from the code so they can be checked: German exonyms used by the catalogue's editors,
my own coordinates for coastal features and well-known places (HAND), and matches rejected after inspection (REJECT)."""

# German names in Modern_location and the forms a gazetteer uses
EXONYM = {
    "Florenz": ["Firenze", "Florence"], "Wien": ["Vienna"], "Belgrad": ["Beograd", "Belgrade"], "Theben": ["Luxor", "Thebes"],
    "Karthago": ["Carthage"], "Nizza": ["Nice"], "Neapel": ["Napoli", "Naples"], "Mailand": ["Milano", "Milan"], "Köln": ["Cologne", "Koln"],
    "Lissabon": ["Lisbon", "Lisboa"], "Venedig": ["Venezia", "Venice"], "Rom": ["Roma", "Rome"], "Genf": ["Geneva", "Geneve"],
    "Athen": ["Athens", "Athina"], "Damaskus": ["Damascus", "Dimashq"], "Tanger": ["Tangier", "Tanger"], "Saragossa": ["Zaragoza"],
    "Mekka": ["Mecca", "Makkah"], "Kairo": ["Cairo"], "Bagdad": ["Baghdad"], "Ninive": ["Nineveh"], "Belgrad ": ["Belgrade"],
    "Konstantinopel": ["Istanbul"], "Byzanz": ["Istanbul"], "Isfahan": ["Esfahan", "Isfahan"], "Kandahar": ["Qandahar", "Kandahar"],
    "Balch": ["Balkh"], "Samarkand": ["Samarqand"], "Chodschent": ["Khujand"], "Kirman": ["Kerman"], "Hormus": ["Hormuz", "Minab"],
    "Schabwa": ["Shabwa"], "Zafar": ["Dhofar", "Zafar"], "Buscher": ["Bushehr"], "Naksch-e Rustem": ["Naqsh-e Rustam"],
    "Taschkurgan": ["Tashkurgan"], "Sevastopol": ["Sevastopol"], "Feodosija": ["Feodosiya"], "Evpatorija": ["Yevpatoriya"],
    "Kertsch": ["Kerch"], "Regensburg": ["Regensburg"], "Speyer": ["Speyer"], "Leiden": ["Leiden"], "Karlsburg": ["Alba Iulia"],
    "Lüttich": ["Liege"], "Aachen": ["Aachen"], "Trier": ["Trier"], "Mainz": ["Mainz"], "Strassburg": ["Strasbourg"],
    "Basel": ["Basel"], "Bregenz": ["Bregenz"], "Kempten": ["Kempten"], "Augsburg": ["Augsburg"], "Salzburg": ["Salzburg"],
    "Laibach": ["Ljubljana"], "Pettau": ["Ptuj"], "Cilli": ["Celje"], "Agram": ["Zagreb"], "Essegg": ["Osijek"], "Mitrovica": ["Sremska Mitrovica"],
    "Ofen": ["Budapest"], "Altofen": ["Budapest"], "Szöny": ["Komarom"], "Sofia": ["Sofia"], "Philippopel": ["Plovdiv"], "Adrianopel": ["Edirne"],
    "Saloniki": ["Thessaloniki"], "Durazzo": ["Durres"], "Valona": ["Vlore"], "Jerusalem": ["Jerusalem"], "Akko": ["Akko", "Acre"],
    "Antiochia": ["Antakya"], "Aleppo": ["Halab", "Aleppo"], "Hama": ["Hamah"], "Homs": ["Hims"], "Gaza": ["Gaza"], "Azza": ["Gaza"],
    "Bharuch": ["Broach", "Bharuch"], "Ujjain": ["Ujjain"], "Patna": ["Patna"], "Mathura": ["Mathura"], "Madurai": ["Madurai"],
    "Xi'an": ["Xian", "Xi'an"], "Dunhuang": ["Dunhuang"], "Kabul": ["Kabul"], "Herat": ["Herat"], "Merv": ["Mary"],
    "Erbil": ["Arbil", "Erbil"], "Basra": ["Basra"], "Hit": ["Hit"], "Aden": ["Aden"], "Marib": ["Marib"], "Muscat": ["Muscat"],
    "Assuan": ["Aswan"], "Alexandria": ["Alexandria", "Al Iskandariyah"], "Kadiköy": ["Kadikoy"], "Izmit": ["Izmit", "Kocaeli"],
    "Paphos": ["Paphos", "Pafos"], "Episkopi": ["Episkopi"], "Larnaka": ["Larnaca"], "Famagusta": ["Famagusta"],
    "Kéllibia": ["Kelibia"], "Djidjelli": ["Jijel"], "Philippeville": ["Skikda"], "Bône": ["Annaba"], "Tripolis": ["Tripoli"],
}

# My own coordinates (lat, lon, confidence, what the point is) for catalogue entries the gazetteers cannot place: coastal
# landmarks (capes, river mouths, estuaries, heads of gulfs) and a few well-known places outside the gazetteers. Each
# follows the editors' identification in Modern_location. 'high': a named landmark whose position is not in doubt
# (a headland, the mouth of a large river, a city); 'medium': a smaller feature or a broad estuary. Positions are to
# about 0.05 degrees (5 km), far finer than the errors measured here.
HAND_TABLE = r"""
# key (chapter|editors' identification, or a full catalogue id) | lat | lon | confidence
2.02|Fair Head|55.22|-6.15|high
2.02|Carnsore Point|52.17|-6.36|high
2.02|Shannon-Mündung|52.58|-9.67|medium
2.02|Lee-Mündung|51.80|-8.28|medium
2.02|Barrow-Mündung|52.20|-6.95|medium
2.02|Boyne-Mündung|53.72|-6.24|high
2.02|Belfast Lough|54.68|-5.75|medium
2.02|Dublin|53.35|-6.26|medium
2.02|Man|54.23|-4.53|medium
2.02|Anglesey|53.28|-4.35|medium
2.03|Loch Ryan|54.97|-5.05|medium
2.03|Irvine Bay|55.60|-4.70|medium
2.03|Firth of Clyde|55.94|-4.60|medium
2.03|Loch Fyne|55.95|-5.35|medium
2.03|Mull of Kintyre|55.31|-5.80|high
2.03|Naver-Mündung|58.53|-4.23|high
2.03|Dunnet Head|58.67|-3.38|high
2.03.02.06|54.80|-4.07|medium
2.03.05.12|57.14|-2.07|high
2.03|Nith-Mündung|54.98|-3.58|high
2.03|Solway Firth|54.90|-3.40|medium
2.03|Morecambe Bay|54.10|-2.95|medium
2.03|Ribble|53.73|-2.95|medium
2.03|Mersey|53.44|-3.02|high
2.03|Braich-y-Pwll|52.79|-4.75|high
2.03|Ystwyth-Mündung|52.40|-4.09|high
2.03|St. David's Head|51.90|-5.31|high
2.03|Tywi-Mündung|51.75|-4.38|high
2.03|Taff-Mündung|51.46|-3.17|high
2.03|Severn|51.55|-2.75|medium
2.03|Bridgewater Bay|51.25|-3.10|medium
2.03|Hartland Point|51.02|-4.53|high
2.03|Land's End|50.07|-5.72|high
2.03|Lizard Point|49.96|-5.21|high
2.03|Tamar-Mündung|50.36|-4.18|high
2.03|Exe-Mündung|50.61|-3.42|high
2.03|Spithead|50.75|-1.10|medium
2.03|Arun|50.80|-0.54|high
2.03|Newhaven|50.78|0.06|high
2.03|South Foreland|51.14|1.37|high
2.03|Duncansby Head|58.64|-3.02|high
2.03|Noss Head|58.48|-3.05|high
2.03|Tarbat Ness|57.87|-3.77|high
2.03|Spey Bay|57.67|-3.08|high
2.03|Deveron-Mündung|57.67|-2.52|high
2.03|Kinnairds Head|57.70|-2.00|high
2.03|Firth of Tay|56.45|-2.85|medium
2.03|Firth of Forth|56.05|-3.10|medium
2.03|Aln-Mündung|55.39|-1.60|high
2.03|Wear-Mündung|54.92|-1.36|high
2.03|Tees Bay|54.63|-1.15|medium
2.03|Bridlington Bay|54.08|-0.18|medium
2.03|Spurn Head|53.58|0.11|high
2.03|Humber|53.65|-0.25|medium
2.03|The Wash|52.90|0.30|medium
2.03|Yare-Mündung|52.57|1.74|high
2.03|Themse-Ästuar|51.50|0.80|medium
2.03|Chester|53.19|-2.89|high
2.03|Orkney-Inseln|59.00|-3.00|medium
2.04|Cabo de Gata|36.72|-2.19|high
2.04|Guadiana-Mündung|37.17|-7.40|high
2.04|Huelva|37.25|-6.95|high
2.04|Guadalquivir-Mündung|36.79|-6.37|high
2.04|Rio del Valle-Mündung|36.09|-5.77|medium
2.04|Guadiaro-Mündung|36.28|-5.27|high
2.04|Guadalhorce-Mündung|36.67|-4.45|high
2.04|Golfo de Almería|36.83|-2.47|medium
2.04|bei Puerto de Santa Maria|36.60|-6.23|medium
2.05|Cabo de San Vicente|37.02|-8.99|high
2.05|Cabo Espichel|38.42|-9.22|high
2.05|Duoro-Mündung|41.14|-8.67|high
2.05|Sado-Mündung|38.48|-8.90|high
2.05|Tejo-Mündung|38.68|-9.25|high
2.05|Mondego-Mündung|40.15|-8.86|high
2.05|Vouga-Mündung|40.64|-8.74|medium
2.05|Cabo de Roca|38.78|-9.50|high
2.05|Cáceres|39.47|-6.37|high
2.06|bei Póvoa de Varzim|41.38|-8.77|medium
2.06|Cabo Touriñán|43.05|-9.30|high
2.06|Cabo Ortegal|43.77|-7.87|high
2.06|Cabo Higuer|43.39|-1.79|high
2.06|Cabo de Palos|37.63|-0.69|high
2.06|Cabo de la Nao|38.73|0.23|high
2.06|Cap Begur|41.95|3.23|high
2.06|Cap Béar|42.51|3.14|high
2.06|Ave-Mündung|41.34|-8.75|high
2.06|Neiva-Mündung|41.61|-8.81|medium
2.06|Limia-Mündung|41.69|-8.85|high
2.06|Miño-Mündung|41.87|-8.87|high
2.06|Ulla-Mündung|42.63|-8.78|medium
2.06|Tambre-Mündung|42.80|-8.97|medium
2.06|Eo-Mündung|43.55|-7.03|high
2.06|Navia-Mündung|43.55|-6.73|high
2.06|Nalón-Mündung|43.56|-6.08|high
2.06|Nervión-Mündung|43.33|-3.02|high
2.06|Deva-Mündung|43.30|-2.35|medium
2.06|Segura-Mündung|38.11|-0.64|high
2.06|Xúquer-Mündung|39.15|-0.24|high
2.06|Palantia-Mündung|39.66|-0.21|medium
2.06|Turia-Mündung|39.45|-0.32|high
2.06|Ebro-Mündung|40.72|0.87|high
2.06|Llobregat-Mündung|41.30|2.13|high
2.06|Fluvià-Mündung|42.14|3.12|high
2.06|León|42.60|-5.57|high
2.07|Cabo Higuer|43.39|-1.79|high
2.07|Cap Ferret|44.64|-1.25|high
2.07|Adour-Mündung|43.53|-1.52|high
2.07|Leyre-Mündung|44.66|-1.03|medium
2.07|Garonne-Mündung|45.58|-1.05|high
2.07|Charente-Mündung|45.96|-1.08|high
2.07|Loire-Mündung|47.28|-2.17|high
2.08|Loire-Mündung|47.28|-2.17|high
2.08|Vilaine-Mündung|47.50|-2.47|high
2.08|Orne-Mündung|49.29|-0.24|high
2.08|Seine-Mündung|49.45|0.15|high
2.08|Lisieux|49.15|0.23|high
2.08|Jublains|48.25|-0.50|high
2.08|Evreux|49.02|1.15|high
2.09|Seine-Mündung|49.45|0.15|high
2.09|Maas-Mündung|51.95|4.05|medium
2.09.04.03|51.90|4.05|medium
2.09.04.04|52.21|4.40|medium
2.09.04.05|53.30|5.07|medium
2.11.01.04|53.30|5.07|medium
2.10|bei La Ciotat|43.17|5.60|medium
2.10|Var-Mündung|43.66|7.19|high
2.10|Tech-Mündung|42.61|3.05|high
2.10|Têt-Mündung|42.72|3.04|high
2.10|Aude-Mündung|43.21|3.24|high
2.10|Orb-Mündung|43.25|3.30|high
2.10|Hérault-Mündung|43.28|3.44|high
2.10|Petit-Rhône|43.45|4.43|high
2.10|Grand-Rhône|43.33|4.84|high
2.10|Argens-Mündung|43.41|6.75|high
2.10|Cap Béar|42.51|3.14|high
2.11|Ems-Mündung|53.35|7.05|medium
2.11|Weser-Mündung|53.55|8.55|high
2.11|Elbe-Mündung|53.88|8.75|high
2.11|Weichsel-Mündung|54.36|18.95|high
2.16|Krka-Mündung|43.72|15.88|high
2.16|Neretva-Mündung|43.02|17.45|high
2.16|Drin-Mündung|41.77|19.59|medium
2.16|Golf von Kotor|42.43|18.70|medium
3.01|Var-Mündung|43.66|7.19|high
3.01|Punta di Talamone|42.55|11.13|high
3.01|Capo Circeo|41.22|13.05|high
3.01|Capo Vaticano|38.62|15.83|high
3.01|Rocca di Scilla|38.25|15.71|high
3.01|Capo dell'Armi|37.95|15.68|high
3.01|Capo Bruzzano|38.03|16.15|high
3.01|Capo Colonna|39.03|17.20|high
3.01|Capo S. Maria di Leuca|39.79|18.36|high
3.01|Entella-Mündung|44.31|9.34|high
3.01|Magra-Mündung|44.05|9.99|high
3.01|Arno-Mündung|43.68|10.28|high
3.01|Osa-Mündung|42.50|11.21|medium
3.01|Tiber-Mündung|41.74|12.23|high
3.01|Garigliano-Mündung|41.22|13.76|high
3.01|Sarno-Mündung|40.72|14.47|high
3.01|Sele-Mündung|40.48|14.94|high
3.01|Lao-Mündung|39.79|15.79|high
3.01|Ofanto-Mündung|41.36|16.20|high
3.01|Biferno-Mündung|41.99|15.02|high
3.01|Sangro-Mündung|42.24|14.54|high
3.01|Pescara-Mündung|42.47|14.23|high
3.01|Tronto-Mündung|42.89|13.92|high
3.01|Esino-Mündung|43.65|13.36|high
3.01|Rubicone-Mündung|44.17|12.44|medium
3.01|Po-Mündung|44.95|12.53|medium
3.01|Tagliamento-Mündung|45.64|13.10|high
3.01|Rizana-Mündung|45.55|13.77|medium
3.01|Golfo di S. Eufemia|38.85|16.20|medium
3.01|Golfo di Squillace|38.80|16.55|medium
3.01|Tarent|40.47|17.24|high
3.01|Isole di Tremiti|42.12|15.50|high
3.02|Capo a u Cavallo|42.53|8.68|medium
3.02|Pointe de Cargèse|42.13|8.58|medium
3.02|Aliso-Mündung|42.68|9.30|medium
3.02|Porto-Mündung|42.27|8.69|medium
3.02|Prunelli-Mündung|41.90|8.80|medium
3.02|Taravo-Mündung|41.70|8.81|medium
3.02|Fium'Orbo|41.98|9.45|medium
3.02|Tavignano-Mündung|42.10|9.55|medium
3.02|Golo-Mündung|42.52|9.53|medium
3.02|Golfe de Galéria|42.42|8.63|medium
3.03|Capo del Falcone|40.97|8.20|high
3.03|Capo Marargiu|40.33|8.38|medium
3.03|Capo Altano|39.25|8.38|medium
3.03|Capo S. Elia|39.18|9.15|high
3.03|Capo Figari|40.99|9.65|high
3.03|Capo d'Orso|41.18|9.42|high
3.03|Temo-Mündung|40.29|8.47|high
3.03|Tirso-Mündung|39.88|8.55|high
3.03|Flumendosa-Mündung|39.44|9.62|high
3.03|Cedrino-Mündung|40.38|9.75|high
3.03|Porto di Malfatano|38.89|8.80|medium
3.03|Golfo di Cagliari|39.18|9.20|medium
3.03|Caprera|41.22|9.46|high
3.03|Isola Asinara|41.07|8.27|high
3.03|Isola di S. Pietro|39.14|8.28|high
3.03|Isola di S. Antioco|39.03|8.42|high
3.03|Sardara|39.62|8.82|high
3.04|Capo Peloro|38.27|15.65|high
3.04|Capo Rasocolmo|38.29|15.52|high
3.04|Capo Boeo oder Lilibeo|37.80|12.43|high
3.04|Capo Scalambri|36.78|14.48|high
3.04|Capo Pássero|36.69|15.15|high
3.04|Capo Ógnina|36.98|15.27|medium
3.04|Capo S. Croce|37.24|15.25|high
3.04|Capo S. Andrea|37.86|15.30|medium
3.04|Simeto-Mündung|37.40|15.09|high
3.04|Fiume Grande-Mündung|37.97|13.82|high
3.04|Salso-Mündung|37.10|13.95|high
3.04|Ippari-Mündung|36.87|14.45|medium
3.04|Modione-Mündung|37.58|12.83|medium
3.04|Mázaro-Mündung|37.65|12.59|high
3.04|Isola Vulcano|38.40|14.96|high
3.05|Weichsel-Mündung|54.36|18.95|high
3.05|Pregolja-Mündung|54.68|20.30|medium
3.05|Neman-Mündung|55.30|21.20|medium
3.05|Dnjepr-Mündung|46.57|31.60|medium
3.05|Südl. Bug-Mündung|46.95|31.95|medium
3.05|Don|47.10|39.25|medium
3.10|Dnjepr-Mündung|46.57|31.60|medium
3.10|Kaliakra|43.36|28.47|high
3.10|Kamcija-Mündung|43.03|27.88|high
3.10|Dnjestr-Mündung|46.08|30.48|high
3.10|Tiligul-Mündung|46.68|31.10|medium
3.10|Schlangeninsel|45.25|30.20|high
3.11|Igneada Burnu|41.88|28.03|high
3.11|Kara Burun|41.35|28.68|medium
3.11|Nestos-Mündung|40.85|24.80|high
3.11|Evros-Mündung|40.73|26.03|high
3.11|Strand von Midye|41.62|28.10|medium
3.11|Marmara Ereglisi|40.97|27.95|high
3.11|Sofia|42.70|23.32|high
3.13|Kap Paliuri|39.92|23.75|high
3.13|Vjosë-Mündung|40.63|19.32|high
3.13|Strymon-Mündung|40.78|23.85|high
3.13|Gallikos-Mündung|40.62|22.92|medium
3.13|Axios-Mündung|40.53|22.70|medium
3.13|Aliakmon-Mündung|40.47|22.65|medium
3.13|Pinios-Mündung|39.88|22.68|high
3.13|Sperchios-Mündung|38.86|22.58|medium
3.13|Malischer Golf|38.88|22.65|medium
3.13|Kolpos Kassandras|40.25|23.40|medium
3.13|Pojani|40.72|19.48|high
3.13|Eretria|38.40|23.80|high
3.14|Karaburun|40.44|19.32|high
3.14|Acheloos-Mündung|38.33|21.10|medium
3.14|Thyamis-Mündung|39.52|20.17|medium
3.14|Acheron-Mündung|39.24|20.48|high
3.14|Arachthos-Mündung|39.02|21.05|medium
3.14|Kap Dukato|38.56|20.54|high
3.15|Kap Sunion|37.65|24.03|high
3.15|Kap Kafirefs|38.16|24.60|high
3.15|Kap Lichada|38.88|22.83|medium
3.15|Evinos-Mündung|38.31|21.53|medium
3.15|Chalkis am Euripos|38.46|23.60|high
3.15|Eretria|38.40|23.80|high
3.15|Stadt auf Delos|37.40|25.27|high
3.15|Stadt auf Mykonos|37.45|25.33|high
3.15|Stadt auf Andros|37.84|24.94|high
3.15|Stadt auf Tinos|37.54|25.16|high
3.15|Stadt auf Syros|37.44|24.94|high
3.15|Stadt auf Naxos|37.10|25.38|high
3.15|Stadt auf Paros|37.08|25.15|high
3.15|Stadt auf Siphnos|36.97|24.73|high
3.16|Araxos|38.17|21.38|high
3.16|Akra Kyllinis|37.94|21.12|high
3.16|Akra Katakolon|37.64|21.32|high
3.16|Kap Akritas|36.72|21.88|high
3.16|Kap Tainaron|36.39|22.48|high
3.16|Akra Maleas|36.44|23.20|high
3.16|Kap Skileon|37.51|23.53|medium
3.16|Alpheios-Mündung|37.61|21.45|high
3.16|Pamisos-Mündung|37.03|22.03|medium
3.16|Evrotas-Mündung|36.80|22.68|medium
3.16|Ägina|37.75|23.43|high
3.16|Methanon|37.58|23.38|medium
3.17|Gramvusa|35.64|23.58|medium
3.17|Kap Krios|35.27|23.53|high
3.17|Kap Sideros|35.32|26.31|high
3.17|Kap Spatha|35.70|23.73|high
3.17|Kap Drepanon|35.47|24.24|medium
3.17|Milos|36.73|24.42|high
3.17|Kimolos|36.80|24.57|high
4.01|Kap Spartel|35.79|-5.92|high
4.01|Oued Loukkos-Mündung|35.20|-6.15|high
4.01|Oued Bou Regreg-Mündung|34.03|-6.84|high
4.01|Oued Sous-Mündung|30.38|-9.60|high
4.01|Oum er-Rbia-Mündung|33.30|-8.35|high
4.01|Oued Martil-Mündung|35.62|-5.27|medium
4.01|Oued Moulouya-Mündung|35.12|-2.35|high
4.01|Kap Cantin|32.58|-9.28|high
4.01|Mogador|31.51|-9.77|high
4.01|Tanger|35.78|-5.81|high
4.01|Asilah|35.47|-6.03|high
4.01|Monte Acho|35.90|-5.28|medium
4.01|Cap Negro|35.68|-5.28|medium
4.02|Oued Tafna-Mündung|35.30|-1.47|medium
4.02|Oued Chéliff-Mündung|36.04|0.13|high
4.02|Oued Soummam-Mündung|36.73|5.08|high
4.02|Oued Sebaou-Mündung|36.91|3.87|medium
4.02|Oued-el-Kebir-Mündung|36.86|6.08|medium
4.03|Cap Bougaroun|37.09|6.47|high
4.03|Kap Bon|37.08|11.05|high
4.03|Ras Kaboudia|35.24|11.15|high
4.03|Medjerda-Mündung|37.12|10.23|medium
4.03|Cap de Garde|36.97|7.79|high
4.03|Ile Zembra|37.13|10.80|high
4.03|Dougga|36.42|9.22|high
4.03|Kap Misurata|32.38|15.22|high
4.05|Rosetta-Mündung|31.47|30.36|high
4.05|Golf von Suez|29.95|32.55|high
4.05|Abusir|30.95|29.52|high
4.05|El-Bahrije|28.35|28.85|medium
4.05|El-Charge|25.45|30.55|medium
4.05|Dakka|23.18|32.77|high
4.05|Tehneh|28.17|30.77|medium
4.06|Oued Sebou-Mündung|34.27|-6.67|high
4.06|Oued Bou Regreg-Mündung|34.03|-6.84|high
4.06|Oued Dra-Mündung|28.70|-11.13|high
4.06|Massa-Mündung|29.80|-9.67|medium
4.06|Oued Massa-Mündung|29.80|-9.67|medium
4.06|Senegal-Mündung|16.05|-16.52|medium
4.06|Tres Forcas|35.44|-2.96|high
4.06|Djerma|26.55|13.07|high
4.07|Kap Guardafui|11.83|51.28|high
4.07|Rufiji-Mündung|7.80|39.33|medium
4.07|Daressalam|6.80|39.28|medium
4.07|Assab|13.00|42.73|medium
4.07|Tempel von Abu Simbel|22.34|31.63|high
4.07|Kasr Ibrim|22.65|31.99|high
4.07|Kerma|19.60|30.41|high
4.07|Dahlak|15.70|40.10|medium
4.08|Kap Delgado|10.67|40.65|high
5.01|Sakarya-Mündung|41.13|30.65|high
5.01|Erdek|40.40|27.79|high
5.01|Bartin Su-Mündung|41.68|32.23|medium
5.02|Kumkale|40.01|26.20|high
5.02|Baba Burun|39.48|26.07|high
5.02|Kap Sigri|39.21|25.85|high
5.02|Kap Mastiko|38.16|26.05|medium
5.02|Lindos|36.09|28.09|high
5.02|Ialisos|36.40|28.15|high
5.02|Gediz Çayi-Mündung|38.60|26.85|medium
5.02|Büyük Menderes-Mündung|37.55|27.20|medium
5.02.07.10|37.95|27.27|medium
5.02|Eski Hisar|37.84|29.11|high
5.02|Ortaklar|37.85|27.53|high
5.02|Harmandali|37.90|28.15|high
5.02|Kapikiri am Begparmak Dagi|37.50|27.53|high
5.03|Bes Adalari|36.23|30.42|medium
5.03|Esen Çayi-Mündung|36.28|29.30|medium
5.04|Kerembe Burnu|42.02|33.33|high
5.04|Kizil Irmak-Mündung|41.73|35.95|high
5.05|Köpru Çayi-Mündung|36.86|31.17|medium
5.06|Yesil Irmak-Mündung|41.38|36.62|high
5.06|Terme Çayi-Mündung|41.23|36.98|high
5.06|Çoruhsu-Mündung|41.60|41.57|high
5.06|Pitsunda|43.16|40.34|high
5.06|Yasun Burun|41.10|37.69|high
5.06|Konya|37.87|32.49|high
5.08.03.08|36.30|34.05|high
5.08|Incekum Burun|36.23|33.95|medium
5.09|Kertsch|45.36|36.47|high
5.09|Taman|45.21|36.72|high
5.09|Anapa|44.89|37.32|high
5.09|Wolga-Mündung|45.80|47.80|medium
5.09|Terek-Mündung|43.65|47.55|medium
5.09|Kuma-Mündung|44.90|47.10|medium
5.09|Bzyb-Mündung|43.19|40.27|high
5.09|Mzymta-Mündung|43.42|39.92|high
5.10|Bzyb-Mündung|43.19|40.27|high
5.10|Kodori-Mündung|42.82|41.12|high
5.10|Rioni-Mündung|42.18|41.65|high
5.10|Khobi-Mündung|42.30|41.62|medium
5.12|Kura-Mündung|39.32|49.35|medium
5.12|Sulak-Mündung|43.27|47.55|high
5.12|Samur-Mündung|41.90|48.60|high
5.14|Kap Arnauti|35.10|32.28|high
5.14|Kap Akrotiri|34.56|33.03|high
5.14|Kap Kiti|34.82|33.62|high
5.14|Kap Greko|34.96|34.08|high
5.14|Kap Apostolos Andreas|35.70|34.59|high
5.14|Koruçam Burun|35.40|32.92|high
5.14|Polis|35.04|32.43|high
5.15|Nahr el-Asi-Mündung|36.04|35.96|high
5.15|Nahr el-Kebir-Mündung|34.64|35.97|high
5.15|Nahr Ibrahim-Mündung|34.07|35.64|high
5.15|Ras es-Saqqa|34.32|35.70|medium
5.15|Banias|33.25|35.69|high
5.15|Baniyas|35.18|35.95|high
5.15|Aintab|37.07|37.38|medium
5.15|Hinzir Burun|36.38|35.78|medium
5.16|Yavneh|31.92|34.70|medium
5.17|Golf von Suez|29.95|32.55|high
5.17|Ras Muhammad|27.73|34.25|high
5.17|Aqaba|29.53|35.00|high
5.17|Deraa|32.62|36.10|high
5.19|Hail|27.52|41.69|high
5.19|Dumat el-Candal|29.81|39.87|high
6.02|Safid Rud-Mündung|37.47|49.94|medium
6.04|Isfahan|32.65|51.67|high
6.04|Buscher|28.97|50.84|medium
6.07|Ras Fartak|15.62|52.23|high
6.07|Muscat|23.61|58.59|medium
6.07|Ras Oman|26.38|56.40|medium
6.07|Mekka|21.42|39.83|high
6.08|Hormus|27.10|56.45|medium
6.08|Ras al-Kuh|25.64|57.77|medium
6.08|Gwadar|25.12|62.33|high
6.08|Kirman|30.28|57.08|high
6.09|Amu-Darja-Mündung|43.80|59.00|medium
6.10|Merv|37.66|62.19|high
6.10|Nisa|37.95|58.21|high
6.12|Chodschent|40.28|69.62|high
6.13|Taschkurgan|37.77|75.23|medium
6.14|Wolga-Mündung|45.80|47.80|medium
6.14|Ural-Mündung|46.95|51.85|high
6.14|Syr-Darja-Mündung|46.10|61.10|medium
6.16|Dunhuang|40.14|94.66|medium
6.16|Xi'an|34.27|108.94|medium
6.17|Herat|34.35|62.20|high
6.18|Kabul|34.53|69.17|high
6.18|Ghazni|33.55|68.42|high
6.18|Begram|34.95|69.32|high
6.20|Kandahar|31.62|65.71|high
6.20|Charsadda|34.15|71.73|high
7.01|Surat|21.17|72.83|high
7.01|Mahi-Mündung|22.20|72.55|medium
7.01|Kim|21.40|72.93|medium
7.01|Narmada-Mündung|21.65|72.62|high
7.01|bei Bassein|19.42|72.80|high
7.01|bei Bombay|18.95|72.83|medium
7.01|Chaul|18.55|72.93|high
7.01|Dabhol|17.59|73.17|high
7.01|Bankot|17.98|73.04|high
7.01|Vijayadurg|16.56|73.33|high
7.01|Tapti-Mündung|21.10|72.65|high
7.01|Ponnani|10.77|75.92|high
7.01|Cranganur|10.22|76.20|high
7.01|Periyar-Mündung|10.18|76.17|medium
7.01|Kap Comorin|8.08|77.55|high
7.01|Korkei|8.64|78.07|high
7.01|Tamraparni-Mündung|8.75|78.15|medium
7.01|Rameswaram|9.29|79.31|high
7.01|Tranquebar|11.03|79.85|high
7.01|Kaveri-Mündung|11.14|79.85|high
7.01|Virampatnam|11.90|79.82|high
7.01|Subarnarekha-Mündung|21.56|87.39|high
7.01|Charsadda|34.15|71.73|high
7.01|Taxila|33.75|72.82|high
7.01|Sialkot|32.49|74.53|high
7.01|Mathura|27.49|77.67|high
7.01|Hathab|21.60|72.27|medium
7.01|Bharuch|21.70|72.98|high
7.01|Ujjain|23.18|75.78|high
7.01|Nasik|20.00|73.79|high
7.01|Patna|25.61|85.14|high
7.01|Tamluk|22.30|87.92|high
7.01|Tair|18.32|76.15|medium
7.01|Paithan|19.48|75.38|high
7.01|Mudgal|16.01|76.44|medium
7.01|Banavasi|14.53|75.02|high
7.01|Tirukkarur|10.96|78.08|medium
7.01|Madurai|9.92|78.12|high
7.01|Uraiyar|10.83|78.68|high
7.01|Beyt|22.47|69.11|medium
7.01|Jaygarh|17.29|73.22|medium
7.01|Pigeon|14.02|74.33|medium
7.02|Dhauli|20.19|85.84|medium
7.03|bei Hanoi|21.03|105.85|medium
7.04|Point Pedro|9.83|80.23|high
7.04|Dondra Head|5.92|80.59|high
7.04|Foul Point|8.53|81.32|high
7.04|Mahaweli Ganga-Mündung|8.47|81.23|high
7.04|Anuradhapura|8.34|80.40|high
7.04|Tissamaharama|6.28|81.29|high
"""
HAND = {}           # key -> (lat, lon, confidence)
for _l in HAND_TABLE.strip().splitlines():
    if _l.startswith("#"):
        continue
    _p = _l.split("|")
    HAND[_p[0] if len(_p) == 4 else _p[0] + "|" + _p[1]] = (float(_p[-3]), float(_p[-2]), _p[-1])

# Matches dropped after inspection: catalogue id -> reason
REJECT = {
    "5.09.08.03": "Hermonassa: Ptolemy lists it among the Bosporan towns of the Taman peninsula; the identification with Akçaabat near Trabzon (a namesake) does not fit",
    "4.03.11.03": "Makomada: Ptolemy's coastal Macomades on the Lesser Syrtis, not the inland Numidian site at Oum el Bouaghi",
}
