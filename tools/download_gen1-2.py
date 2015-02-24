#!/usr/bin/python
# coding=utf-8
from wikitools import wiki, wikifile

""" Because the Veekun sprite rips of gen1/2 are non-transparent, they must be downloaded from Bulbapedia instead """

def main():
    site = wiki.Wiki("http://bulbapedia.bulbagarden.net/w/api.php")
    img_root = "/var/projects/namerater/assets/pokemon/"
    for num in xrange(1,252): #252
        dex = ("00"+str(num))[-3:]
        print num
        # Gen 1
        if num <= 151:
            # R/G front
            f = wikifile.File(site, "File:Spr_1g_"+dex+".png")
            f.download(location=img_root+"red-green/"+str(num)+".png")
            # R/G back
            f = wikifile.File(site, "File:Spr_b_g1_"+dex+".png")
            f.download(location=img_root+"red-green/back/"+str(num)+".png")
            
            # R/B front
            f = wikifile.File(site, "File:Spr_1b_"+dex+".png")
            f.download(location=img_root+"red-blue/"+str(num)+".png")
            # R/B back
            f = wikifile.File(site, "File:Spr_b_g1_"+dex+".png")
            f.download(location=img_root+"red-blue/back/"+str(num)+".png")
            
            # Y front
            f = wikifile.File(site, "File:Spr_1y_"+dex+".png")
            f.download(location=img_root+"yellow/"+str(num)+".png")
            # Y back
            f = wikifile.File(site, "File:Spr_b_g1_"+dex+".png")
            f.download(location=img_root+"yellow/back/"+str(num)+".png")
        
        # Gen 2
        # Gold front
        f = wikifile.File(site, "File:Spr_2g_"+dex+".png")
        f.download(location=img_root+"gold/"+str(num)+".png")
        # Gold back
        f = wikifile.File(site, "File:Spr_b_2g_"+dex+".png")
        f.download(location=img_root+"gold/back/"+str(num)+".png")
        
        # Gold shiny front
        f = wikifile.File(site, "File:Spr_2g_"+dex+"_s.png")
        f.download(location=img_root+"gold/shiny/"+str(num)+".png")
        # Gold shiny back
        f = wikifile.File(site, "File:Spr_b_2g_"+dex+"_s.png")
        f.download(location=img_root+"gold/back/shiny/"+str(num)+".png")
        
        # Silver front
        f = wikifile.File(site, "File:Spr_2s_"+dex+".png")
        f.download(location=img_root+"silver/"+str(num)+".png")
        # Silver back
        f = wikifile.File(site, "File:Spr_b_2g_"+dex+".png")
        f.download(location=img_root+"silver/back/"+str(num)+".png")
        
        # Silver shiny front
        f = wikifile.File(site, "File:Spr_2s_"+dex+"_s.png")
        f.download(location=img_root+"silver/shiny/"+str(num)+".png")
        # Silver shiny back
        f = wikifile.File(site, "File:Spr_b_2g_"+dex+"_s.png")
        f.download(location=img_root+"silver/back/shiny/"+str(num)+".png")
        
        # Crystal front
        f = wikifile.File(site, "File:Spr_2c_"+dex+".gif")
        f.download(location=img_root+"crystal/"+str(num)+".png")
        # Crystal back
        f = wikifile.File(site, "File:Spr_b_2c_"+dex+".png")
        f.download(location=img_root+"crystal/back/"+str(num)+".png")
        
        # Crystal shiny front
        f = wikifile.File(site, "File:Spr_2c_"+dex+"_s.gif")
        f.download(location=img_root+"crystal/shiny/"+str(num)+".png")
        # Crystal shiny back
        f = wikifile.File(site, "File:Spr_b_2g_"+dex+"_s.png")
        f.download(location=img_root+"crystal/back/shiny/"+str(num)+".png")
        
        
    return
    
if __name__ == "__main__": main()