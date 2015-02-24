# coding=utf-8
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Count, Avg, Sum, Q
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import *
from namerater.models import *
from datetime import datetime, date, timedelta
from django.conf import settings

import json, urllib2, time
import random

ADS         = True      # Adsense
TRACKING    = True      # Analytics
ALLOW_ANON  = True      # Anonymous Submissions
ANON_LIMIT  = 3         # Anon Submissions per IP per day
READ_ONLY   = False     # Prevent Submissions
PAGE_SIZE   = 12        # Listings per page

if settings.ENV == "DEV":
    LOGIN_URL = ""
else:
    LOGIN_URL = "https://namerater.gayriots.com"

# This needs to be updated with the DB sprite table
TILESETS = {"red-green":"Red / Green",
    "red-blue":"Red / Blue",
    "yellow":"Yellow",
    "gold":"Gold",
    "silver":"Silver",
    "crystal":"Crystal",
    "ruby-sapphire":"Ruby / Sapphire",
    "emerald":"Emerald",
    "firered-leafgreen":"Fire Red / Leaf Green",
    "diamond-pearl":"Diamond / Pearl",
    "platinum":"Platinum",
    "heartgold-soulsilver":"Heart Gold / Soul Silver",
    "black-white":"Black / White",
    "x-y":"X / Y / ORAS"}

POKEDEX = {"Abomasnow":460, "Abra":63, "Absol":359, "Accelgor":617, "Aegislash":681, "Aerodactyl":142, "Aggron":306, "Aipom":190, "Alakazam":65, "Alomomola":594, "Altaria":334, "Amaura":698, "Ambipom":424, "Amoonguss":591, "Ampharos":181, "Anorith":347, "Arbok":24, "Arcanine":59, "Arceus":493, "Archen":566, "Archeops":567, "Ariados":168, "Armaldo":348, "Aromatisse":683, "Aron":304, "Articuno":144, "Audino":531, "Aurorus":699, "Avalugg":713, "Axew":610, "Azelf":482, "Azumarill":184, "Azurill":298, "Bagon":371, "Baltoy":343, "Banette":354, "Barbaracle":689, "Barboach":339, "Basculin":550, "Bastiodon":411, "Bayleef":153, "Beartic":614, "Beautifly":267, "Beedrill":15, "Beheeyem":606, "Beldum":374, "Bellossom":182, "Bellsprout":69, "Bergmite":712, "Bibarel":400, "Bidoof":399, "Binacle":688, "Bisharp":625, "Blastoise":9, "Blaziken":257, "Blissey":242, "Blitzle":522, "Boldore":525, "Bonsly":438, "Bouffalant":626, "Braixen":654, "Braviary":628, "Breloom":286, "Bronzong":437, "Bronzor":436, "Budew":406, "Buizel":418, "Bulbasaur":1, "Buneary":427, "Bunnelby":659, "Burmy":412, "Butterfree":12, "Cacnea":331, "Cacturne":332, "Camerupt":323, "Carbink":703, "Carnivine":455, "Carracosta":565, "Carvanha":318, "Cascoon":268, "Castform":351, "Caterpie":10, "Celebi":251, "Chandelure":609, "Chansey":113, "Charizard":6, "Charmander":4, "Charmeleon":5, "Chatot":441, "Cherrim":421, "Cherubi":420, "Chesnaught":652, "Chespin":650, "Chikorita":152, "Chimchar":390, "Chimecho":358, "Chinchou":170, "Chingling":433, "Cinccino":573, "Clamperl":366, "Clauncher":692, "Clawitzer":693, "Claydol":344, "Clefable":36, "Clefairy":35, "Cleffa":173, "Cloyster":91, "Cobalion":638, "Cofagrigus":563, "Combee":415, "Combusken":256, "Conkeldurr":534, "Corphish":341, "Corsola":222, "Cottonee":546, "Cradily":346, "Cranidos":408, "Crawdaunt":342, "Cresselia":488, "Croagunk":453, "Crobat":169, "Croconaw":159, "Crustle":558, "Cryogonal":615, "Cubchoo":613, "Cubone":104, "Cyndaquil":155, "Darkrai":491, "Darmanitan":555, "Darumaka":554, "Dedenne":702, "Deerling":585, "Deino":633, "Delcatty":301, "Delibird":225, "Delphox":655, "Deoxys":386, "Dewgong":87, "Dewott":502, "Dialga":483, "Diggersby":660, "Diglett":50, "Ditto":132, "Dodrio":85, "Doduo":84, "Donphan":232, "Doublade":680, "Dragalge":691, "Dragonair":148, "Dragonite":149, "Drapion":452, "Dratini":147, "Drifblim":426, "Drifloon":425, "Drilbur":529, "Drowzee":96, "Druddigon":621, "Ducklett":580, "Dugtrio":51, "Dunsparce":206, "Duosion":578, "Durant":632, "Dusclops":356, "Dusknoir":477, "Duskull":355, "Dustox":269, "Dwebble":557, "Eelektrik":603, "Eelektross":604, "Eevee":133, "Ekans":23, "Electabuzz":125, "Electivire":466, "Electrike":309, "Electrode":101, "Elekid":239, "Elgyem":605, "Emboar":500, "Emolga":587, "Empoleon":395, "Entei":244, "Escavalier":589, "Espeon":196, "Espurr":677, "Excadrill":530, "Exeggcute":102, "Exeggutor":103, "Exploud":295, "Farfetch'd":83, "Fearow":22, "Feebas":349, "Fennekin":653, "Feraligatr":160, "Ferroseed":597, "Ferrothorn":598, "Finneon":456, "Flaaffy":180, u"Flabébé":669, "Flareon":136, "Fletchinder":662, "Fletchling":661, "Floatzel":419, "Floette":670, "Florges":671, "Flygon":330, "Foongus":590, "Forretress":205, "Fraxure":611, "Frillish":592, "Froakie":656, "Frogadier":657, "Froslass":478, "Furfrou":676, "Furret":162, "Gabite":444, "Gallade":475, "Galvantula":596, "Garbodor":569, "Garchomp":445, "Gardevoir":282, "Gastly":92, "Gastrodon":423, "Genesect":649, "Gengar":94, "Geodude":74, "Gible":443, "Gigalith":526, "Girafarig":203, "Giratina":487, "Glaceon":471, "Glalie":362, "Glameow":431, "Gligar":207, "Gliscor":472, "Gloom":44, "Gogoat":673, "Golbat":42, "Goldeen":118, "Golduck":55, "Golem":76, "Golett":622, "Golurk":623, "Goodra":706, "Goomy":704, "Gorebyss":368, "Gothita":574, "Gothitelle":576, "Gothorita":575, "Gourgeist":711, "Granbull":210, "Graveler":75, "Greninja":658, "Grimer":88, "Grotle":388, "Groudon":383, "Grovyle":253, "Growlithe":58, "Grumpig":326, "Gulpin":316, "Gurdurr":533, "Gyarados":130, "Happiny":440, "Hariyama":297, "Haunter":93, "Hawlucha":701, "Haxorus":612, "Heatmor":631, "Heatran":485, "Heliolisk":695, "Helioptile":694, "Heracross":214, "Herdier":507, "Hippopotas":449, "Hippowdon":450, "Hitmonchan":107, "Hitmonlee":106, "Hitmontop":237, "Honchkrow":430, "Honedge":679, "Ho-Oh":250, "Hoothoot":163, "Hoppip":187, "Horsea":116, "Houndoom":229, "Houndour":228, "Huntail":367, "Hydreigon":635, "Hypno":97, "Igglybuff":174, "Illumise":314, "Infernape":392, "Inkay":686, "Ivysaur":2, "Jellicent":593, "Jigglypuff":39, "Jirachi":385, "Jolteon":135, "Joltik":595, "Jumpluff":189, "Jynx":124, "Kabuto":140, "Kabutops":141, "Kadabra":64, "Kakuna":14, "Kangaskhan":115, "Karrablast":588, "Kecleon":352, "Keldeo":647, "Kingdra":230, "Kingler":99, "Kirlia":281, "Klang":600, "Klefki":707, "Klink":599, "Klinklang":601, "Koffing":109, "Krabby":98, "Kricketot":401, "Kricketune":402, "Krokorok":552, "Krookodile":553, "Kyogre":382, "Kyurem":646, "Lairon":305, "Lampent":608, "Landorus":645, "Lanturn":171, "Lapras":131, "Larvesta":636, "Larvitar":246, "Latias":380, "Latios":381, "Leafeon":470, "Leavanny":542, "Ledian":166, "Ledyba":165, "Lickilicky":463, "Lickitung":108, "Liepard":510, "Lileep":345, "Lilligant":549, "Lillipup":506, "Linoone":264, "Litleo":667, "Litwick":607, "Lombre":271, "Lopunny":428, "Lotad":270, "Loudred":294, "Lucario":448, "Ludicolo":272, "Lugia":249, "Lumineon":457, "Lunatone":337, "Luvdisc":370, "Luxio":404, "Luxray":405, "Machamp":68, "Machoke":67, "Machop":66, "Magby":240, "Magcargo":219, "Magikarp":129, "Magmar":126, "Magmortar":467, "Magnemite":81, "Magneton":82, "Magnezone":462, "Makuhita":296, "Malamar":687, "Mamoswine":473, "Manaphy":490, "Mandibuzz":630, "Manectric":310, "Mankey":56, "Mantine":226, "Mantyke":458, "Maractus":556, "Mareep":179, "Marill":183, "Marowak":105, "Marshtomp":259, "Masquerain":284, "Mawile":303, "Medicham":308, "Meditite":307, "Meganium":154, "Meloetta":648, "Meowstic":678, "Meowth":52, "Mesprit":481, "Metagross":376, "Metang":375, "Metapod":11, "Mew":151, "Mewtwo":150, "Mienfoo":619, "Mienshao":620, "Mightyena":262, "Milotic":350, "Miltank":241, "Mime Jr.":439, "Minccino":572, "Minun":312, "Misdreavus":200, "Mismagius":429, "Moltres":146, "Monferno":391, "Mothim":414, "Mr. Mime":122, "Mudkip":258, "Muk":89, "Munchlax":446, "Munna":517, "Murkrow":198, "Musharna":518, "Natu":177, "Nidoking":34, "Nidoqueen":31, u"Nidoran♀":29, u"Nidoran♂":32, "Nidorina":30, "Nidorino":33, "Nincada":290, "Ninetales":38, "Ninjask":291, "Noctowl":164, "Noibat":714, "Noivern":715, "Nosepass":299, "Numel":322, "Nuzleaf":274, "Octillery":224, "Oddish":43, "Omanyte":138, "Omastar":139, "Onix":95, "Oshawott":501, "Pachirisu":417, "Palkia":484, "Palpitoad":536, "Pancham":674, "Pangoro":675, "Panpour":515, "Pansage":511, "Pansear":513, "Paras":46, "Parasect":47, "Patrat":504, "Pawniard":624, "Pelipper":279, "Persian":53, "Petilil":548, "Phanpy":231, "Phantump":708, "Phione":489, "Pichu":172, "Pidgeot":18, "Pidgeotto":17, "Pidgey":16, "Pidove":519, "Pignite":499, "Pikachu":25, "Piloswine":221, "Pineco":204, "Pinsir":127, "Piplup":393, "Plusle":311, "Politoed":186, "Poliwag":60, "Poliwhirl":61, "Poliwrath":62, "Ponyta":77, "Poochyena":261, "Porygon":137, "Porygon2":233, "Porygon-Z":474, "Primeape":57, "Prinplup":394, "Probopass":476, "Psyduck":54, "Pumpkaboo":710, "Pupitar":247, "Purrloin":509, "Purugly":432, "Pyroar":668, "Quagsire":195, "Quilava":156, "Quilladin":651, "Qwilfish":211, "Raichu":26, "Raikou":243, "Ralts":280, "Rampardos":409, "Rapidash":78, "Raticate":20, "Rattata":19, "Rayquaza":384, "Regice":378, "Regigigas":486, "Regirock":377, "Registeel":379, "Relicanth":369, "Remoraid":223, "Reshiram":643, "Reuniclus":579, "Rhydon":112, "Rhyhorn":111, "Rhyperior":464, "Riolu":447, "Roggenrola":524, "Roselia":315, "Roserade":407, "Rotom":479, "Rufflet":627, "Sableye":302, "Salamence":373, "Samurott":503, "Sandile":551, "Sandshrew":27, "Sandslash":28, "Sawk":539, "Sawsbuck":586, "Scatterbug":664, "Sceptile":254, "Scizor":212, "Scolipede":545, "Scrafty":560, "Scraggy":559, "Scyther":123, "Seadra":117, "Seaking":119, "Sealeo":364, "Seedot":273, "Seel":86, "Seismitoad":537, "Sentret":161, "Serperior":497, "Servine":496, "Seviper":336, "Sewaddle":540, "Sharpedo":319, "Shaymin":492, "Shedinja":292, "Shelgon":372, "Shellder":90, "Shellos":422, "Shelmet":616, "Shieldon":410, "Shiftry":275, "Shinx":403, "Shroomish":285, "Shuckle":213, "Shuppet":353, "Sigilyph":561, "Silcoon":266, "Simipour":516, "Simisage":512, "Simisear":514, "Skarmory":227, "Skiddo":672, "Skiploom":188, "Skitty":300, "Skorupi":451, "Skrelp":690, "Skuntank":435, "Slaking":289, "Slakoth":287, "Sliggoo":705, "Slowbro":80, "Slowking":199, "Slowpoke":79, "Slugma":218, "Slurpuff":685, "Smeargle":235, "Smoochum":238, "Sneasel":215, "Snivy":495, "Snorlax":143, "Snorunt":361, "Snover":459, "Snubbull":209, "Solosis":577, "Solrock":338, "Spearow":21, "Spewpa":665, "Spheal":363, "Spinarak":167, "Spinda":327, "Spiritomb":442, "Spoink":325, "Spritzee":682, "Squirtle":7, "Stantler":234, "Staraptor":398, "Staravia":397, "Starly":396, "Starmie":121, "Staryu":120, "Steelix":208, "Stoutland":508, "Stunfisk":618, "Stunky":434, "Sudowoodo":185, "Suicune":245, "Sunflora":192, "Sunkern":191, "Surskit":283, "Swablu":333, "Swadloon":541, "Swalot":317, "Swampert":260, "Swanna":581, "Swellow":277, "Swinub":220, "Swirlix":684, "Swoobat":528, "Sylveon":700, "Taillow":276, "Talonflame":663, "Tangela":114, "Tangrowth":465, "Tauros":128, "Teddiursa":216, "Tentacool":72, "Tentacruel":73, "Tepig":498, "Terrakion":639, "Throh":538, "Thundurus":642, "Timburr":532, "Tirtouga":564, "Togekiss":468, "Togepi":175, "Togetic":176, "Torchic":255, "Torkoal":324, "Tornadus":641, "Torterra":389, "Totodile":158, "Toxicroak":454, "Tranquill":520, "Trapinch":328, "Treecko":252, "Trevenant":709, "Tropius":357, "Trubbish":568, "Turtwig":387, "Tympole":535, "Tynamo":602, "Typhlosion":157, "Tyranitar":248, "Tyrantrum":697, "Tyrogue":236, "Tyrunt":696, "Umbreon":197, "Unfezant":521, "Unown":201, "Ursaring":217, "Uxie":480, "Vanillish":583, "Vanillite":582, "Vanilluxe":584, "Vaporeon":134, "Venipede":543, "Venomoth":49, "Venonat":48, "Venusaur":3, "Vespiquen":416, "Vibrava":329, "Victini":494, "Victreebel":71, "Vigoroth":288, "Vileplume":45, "Virizion":640, "Vivillon":666, "Volbeat":313, "Volcarona":637, "Voltorb":100, "Vullaby":629, "Vulpix":37, "Wailmer":320, "Wailord":321, "Walrein":365, "Wartortle":8, "Watchog":505, "Weavile":461, "Weedle":13, "Weepinbell":70, "Weezing":110, "Whimsicott":547, "Whirlipede":544, "Whiscash":340, "Whismur":293, "Wigglytuff":40, "Wingull":278, "Wobbuffet":202, "Woobat":527, "Wooper":194, "Wormadam":413, "Wurmple":265, "Wynaut":360, "Xatu":178, "Xerneas":716, "Yamask":562, "Yanma":193, "Yanmega":469, "Yveltal":717, "Zangoose":335, "Zapdos":145, "Zebstrika":523, "Zekrom":644, "Zigzagoon":263, "Zoroark":571, "Zorua":570, "Zubat":41, "Zweilous":634, "Zygarde":718}
keys = POKEDEX.keys()
SPECIES = keys.sort()
ALL = []
MAX_SPECIES = 718 # Zygarde
for key in keys:
    ALL.append((key, POKEDEX[key]))
    
# Pokemon that always have some form
ALWAYS_FORM = [201, 412, 421, 422, 423, 493, 585, 586, 666, 669, 670, 671, 716, 386, 413, 492, 487, 479, 351, 550, 555, 648, 641, 642, 645, 646, 647, 678, 681, 710, 711]
    
CAPTCHA = {1:"bulbasaur", 4:"charmander", 6:"charizard", 7:"squirtle", 12:"butterfree", 25:"pikachu", 26:"raichu", 39:"jigglypuff", 52:"meowth", 54:"psyduck", 
    129:"magikarp", 133:"eevee", 143:"snorlax", 150:"mewtwo", 151:"mew", 448:"lucario"}

SLURS = [u"nigger", u"niggers", u"faggot", u"faggots", u"fag", u"fags", u"cunt", u"cunts", u"bitch", u"bitches", u"kike", u"kikes", u"chink", u"chinks", u"rape", u"raped", u"rapist", u"rapes", u"raping"]

def generate_identifier(type="submission"):
    chars = "1234567890abcdefghijklmnopqrstuvwxyz"
    while True:
        identifier = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
        if type == "submission" and not Submission.objects.filter(key=identifier).count():
            break
        elif type == "user" and not User.objects.filter(key=identifier).count():
            break
    return identifier
    
def update_session(request, user):
    request.session["logged_in"] = True
    request.session["user_id"] = user.id
    request.session["userkey"] = user.key
    request.session["username"] = user.name
    request.session["icon"] = user.icon
    request.session["active"] = user.active
    request.session["admin"] = user.admin
    request.session["submissions"] = user.submissions
    request.session["submission_limit"] = user.submission_limit
    return True