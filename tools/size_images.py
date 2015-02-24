#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, glob

from PIL import Image # Gen 6 only

def main():
    #files = glob.glob("/var/projects/namerater/assets/pokemon/x-y/*.png")
    files = []
    
    #files += glob.glob("/var/projects/namerater/assets/pokemon/x-y/back/*.png")
    #files += glob.glob("/var/projects/namerater/assets/pokemon/x-y/back/female/*.png")
    #files += glob.glob("/var/projects/namerater/assets/pokemon/x-y/back/shiny/*.png")
    #files += glob.glob("/var/projects/namerater/assets/pokemon/x-y/back/shiny/female*.png")
    
    files += glob.glob("/var/projects/namerater/assets/pokemon/x-y/female/*.png")
    files += glob.glob("/var/projects/namerater/assets/pokemon/x-y/shiny/*.png")
    files += glob.glob("/var/projects/namerater/assets/pokemon/x-y/shiny/female/*.png")
    
    files.sort()
    for file in files:
        #command = "/var/projects/misc/image_processing.py {} {} -rn 112 112 -x 128 128 C".format(file, file) # R/G, R/B, Y
        #command = "/var/projects/misc/image_processing.py {} {} -rn 2x 2x -x 128 128 C".format(file, file) # G,S,C
        #command = "/var/projects/misc/image_processing.py {} {} -rn 2x 2x".format(file, file) # R/S,E,FR/LG
        #command = "/var/projects/misc/image_processing.py {} {} -x 128 128 C".format(file, file) # D/P, Pt, HG/SS, BW+B2W2
        
        #print command + "\n"
        #os.system(command)
        
        """ Gen 6 """
        wip = Image.open(file)
        output_name = file
        
        clamp_w = False
        clamp_h = False
        w = wip.size[0]
        h = wip.size[1]
        
        if wip.size[0] > 128 and wip.size[1] > 128:
            if wip.size[0] > wip.size[1]:
                clamp_w = True
            else:
                clamp_h = True
        
        if wip.size[0] > 128 or clamp_w:
            w = 128
            h = int(round(wip.size[1] * (1.0 * w / wip.size[0])))
            print "A FILE:", file
            print w, h
            wip = wip.resize((int(w),int(h)), Image.BICUBIC)
        elif wip.size[1] > 128 or clamp_h:
            h = 128
            w = int(round(wip.size[0] * (1.0 * h / wip.size[1])))
            wip = wip.resize((int(w),int(h)), Image.BICUBIC)
            
        
        print file, " -- RESIZED TO:", w, h
        
        src_width = w
        src_height = h
        out = Image.new("RGBA", (128, 128), (0,0,0,0))
        x, y = ((128 - src_width) / 2,(128 - src_height) / 2)
        out.paste(wip, (x,y))
        print "Saving..."
        out.save(output_name)
    return
    
if __name__ == "__main__": main()