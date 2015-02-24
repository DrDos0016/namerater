#!/usr/bin/python
# coding=utf-8
import json, os, sys, glob
sys.path.append("/var/projects/namerater")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rater.settings")
from namerater.models import *

data = {}

"""
for (path, dirs, files) in os.walk("/var/projects/namerater/assets/pokemon"):
    #print path
    #print dirs
    #print files
    for file in files:
        all_files[] = path + "/" + fil
"""

tilesets = Sprite.objects.all()

for tileset in tilesets:
    print tileset.name.upper()
    data[tileset.directory] = {}
    base_images = glob.glob("/var/projects/namerater/assets/pokemon/"+tileset.directory+"/*.png")
    print "\tBase", len(base_images)
    for image in base_images:
        data[tileset.directory][image[40 + len(tileset.directory):-4]] = {}
    
    # Back sprites
    back_images = glob.glob("/var/projects/namerater/assets/pokemon/"+tileset.directory+"/back/*.png")
    print "\tBack", len(back_images)
    for image in back_images:
        try:
            data[tileset.directory][image[45 + len(tileset.directory):-4]]["has_back"] = True
        except:
            pass
    
    # Shiny sprites
    shiny_images = glob.glob("/var/projects/namerater/assets/pokemon/"+tileset.directory+"/shiny/*.png")
    print "\tShiny", len(shiny_images)
    for image in shiny_images:
        try:
            data[tileset.directory][image[46 + len(tileset.directory):-4]]["has_shiny"] = True
        except:
            pass
    
    # Female sprites
    female_images = glob.glob("/var/projects/namerater/assets/pokemon/"+tileset.directory+"/female/*.png")
    print "\tFemale", len(female_images)
    for image in female_images:
        try:
            data[tileset.directory][image[47 + len(tileset.directory):-4]]["has_female"] = True
        except:
            pass

"""
json_data = json.dumps(data)
dump = open("/var/projects/namerater/assets/data/images.json", "w")
dump.write(json_data)
dump.close()
"""


#print data

for tileset in tilesets:
    for key in data[tileset.directory].keys():
        print "Saving", tileset.name, key
        detail, created = Detail.objects.get_or_create(directory=tileset.directory, species=key, has_back=data[tileset.directory][key].get("has_back", False), 
            has_shiny=data[tileset.directory][key].get("has_shiny", False), has_female=data[tileset.directory][key].get("has_female", False))