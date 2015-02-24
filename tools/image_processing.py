#!/usr/bin/python
# -*- coding: utf-8 -*-
from PIL import Image
import sys, os

def main():
    if len(sys.argv) < 2:
        print "image_processing.py <input> <output> [commands]"
        print "COMMANDS:"
        print "\t-x <width> <height> <anchorNSEWC>          Expand canvas size"
        print "\t-c <top> <left> <right> <bottom>           Crop image"
        sys.exit()
    
    wip = Image.open(sys.argv[1])
    output_name = sys.argv[2]
    for x in xrange(3, len(sys.argv)):
        if sys.argv[x][0] != "-":
            continue
            
        if sys.argv[x] == "-x":
            wip = expand_canvas(wip, sys.argv[x+1], sys.argv[x+2], sys.argv[x+3])
        if sys.argv[x] == "-c":
            wip = crop_image(wip, sys.argv[x+1], sys.argv[x+2], sys.argv[x+3], sys.argv[x+4])
    
    wip.save(output_name)
    return
    
def expand_canvas(wip, w, h, anchor):
    w = int(w)
    h = int(h)
    src_width, src_height = wip.size
        
    anchors = {"NW":(0,0), "N":((w - src_width) / 2,0), "NE":((w - src_width),0),
        "W":(0,(h - src_height) / 2), "C":((w - src_width) / 2,(h - src_height) / 2), "E":(w - src_width, (h - src_height) / 2),
        "SW":(0,(h - src_height)), "S":((w - src_width) / 2,(h - src_height)), "SE":((w - src_width),(h - src_height))}
    
    out = Image.new("RGBA", (w, h), (0,0,0,0))
    x, y = anchors[anchor]
    out.paste(wip, (x,y))
    return out
    
def crop_image(wip, top, left, right, bottom):
    top = int(top)
    left = int(left)
    right = int(right)
    bottom = int(bottom)
    crop = wip.crop((top,left,right,bottom))
    return crop
    
if __name__ == "__main__": main()