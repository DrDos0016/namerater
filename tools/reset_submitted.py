#!/usr/bin/python
import os, sys
sys.path.append("/var/projects/namerater")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rater.settings")
from namerater.models import User

def main():
    # Reset daily submission limit
    User.objects.update(submissions=0)
    
    # Check for promotions

if __name__ == "__main__": main()