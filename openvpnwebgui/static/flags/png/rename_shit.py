import glob
import os

import pycountry as pycountry

flags = glob.glob('*.png')

print(pycountry.countries)
unknown_flags = []

for flag in flags:
    try:
        country = pycountry.countries.get(common_name=flag.split(".")[0].capitalize().replace("-", " "))
        print(country)
        os.rename(flag, country.alpha_2.lower() + '.png')

    except:
        unknown_flags.append(flag)

print(unknown_flags)
