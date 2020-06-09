from openalpr import Alpr
import sys


def check_image(path):
    alpr = Alpr("us", "/mnt/f/objectenv/lib/python3.8/openalpr/openalpr.conf", "/mnt/f/objectenv/lib/python3.8/openalpr/runtime_data")
    if not alpr.is_loaded():
        print("Error loading OpenALPR")
        sys.exit(1)

    #set_top_n set number of results to be displayed pre found plate   
    alpr.set_top_n(1)
    #counrty set to eu to recognise SA plates
    alpr.set_country("eu")

    #name of file to be prased
    results = alpr.recognize_file(path)

    i = 0
    for plate in results['results']:
        i += 1
        print("Plate #%d" % i)
        print("   %12s %12s" % ("Plate", "Confidence"))
        for candidate in plate['candidates']:
            prefix = "-"
            if candidate['matches_template']:
                prefix = "*"

            print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))

    # Call when completely done to release memory
    alpr.unload()