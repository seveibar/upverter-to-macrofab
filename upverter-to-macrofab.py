# Upverter to Macrofab Converter
# See README.md for usage instructions

# TODO this currently requires a tempo.json file, which is the tempo automation
# file that upverter exports, this file isn't used by tempo automation so it
# will likely be deprecated in the future

import sys

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print("USAGE: tempo-to-mf.py <upverter.upv> <tempo.json> [component key file]")
    sys.exit(1)

import json

upv = json.load(open(sys.argv[1]))
tempo = json.load(open(sys.argv[2]))

# ----------------------------
# PARSE UPVERTER FILE
# ----------------------------
# The only thing we currently care about (because we leverage the tempo format)
# is the mechanical details layer offset
board_offset = None
for path in upv['paths']:
    if path['layer'] == 'mechanical details':
        # Find the bottom left point (it's usually the first one)
        # this can be done by finding the miniumum (x - y)
        # here's a bad algorithm:
        top_left = sorted(path['points'], key=lambda p: p['x'] + p['y'])[0]
        # Upverter's units are in nm, we convert to meters then to inches
        board_offset = (top_left['x'] / 10.0**9 * 39.37, top_left['y']/ 10.0**9 * 39.37)
        break
print(board_offset)
if not board_offset:
    print("Couldn't find board offset from mechanical details layer")
    sys.exit(1)

# ----------------------------
# GENERATE/READ KEY FILE
# ----------------------------

comp_keys = None
if len(sys.argv) == 4:
    comp_keys = json.load(open(sys.argv[3]))
else:
    print("You did not specify a key file, beginning generation...")
    print("You will be asked for the MPN for each component type in the file")
    comp_keys = {}
    for comp_id in tempo["components"]:
        print("\n")
        comp = tempo["components"][comp_id]
        print("Component {}".format(comp_id))
        print("Manufacturer: {}".format(comp["Manufacturer"]))
        mf_name = raw_input("Macrofab MPN (\"SKIP\" to skip):")
        if mf_name.lower().strip() == "skip": continue
        smd = raw_input("SMD (S) or Throughole (T)? [SMD]:")
        value = raw_input("Value:")
        footprint = raw_input("Footprint (e.g. 0403):")
        comp_keys[comp_id] = {
            "MPN": mf_name,
            "Type": smd == "T" and 2 or 1,
            "Value": value,
            "Footprint": footprint
        }
    print("\nWriting the key file to \"keyfile.json\"")
    json.dump(comp_keys, open("keyfile.json",'w'))


# ----------------------------
# GENERATE XYRS FILE
# ----------------------------

lines = [
    ["#Designator","X-Loc","Y-Loc","Rotation","Side","Type","X-Size","Y-Size","Value","Footprint","Populate","MPN"]
]
for placement,i in zip(tempo["placements"], range(len(tempo['placements']))):
    if placement["ComponentId"] not in comp_keys:
        continue
    cinfo = comp_keys[placement["ComponentId"]]
    lines.append([
        placement['DesignName'] + str(i), # Designator
        (placement['BoardLocationX'] - board_offset[0]) * 1000, #X-Loc
        (placement['BoardLocationY'] - board_offset[1]) * 1000, #Y-Loc
        (270 + 360 - placement['Rotation'])%360, # Rotation
        placement['Layer'], # Side
        cinfo['Type'], # Type
        100, 100, # X-Size, Y-Size
        cinfo['Value'], # Value
        cinfo['Footprint'], # Footprint
        1, # Populate (yes)
        cinfo["MPN"] # MPN
    ])

# ----------------------------
# WRITE OUTPUT FILE
# ----------------------------

print("Writing to output file \"output.XYRS\"")
open("output.XYRS",'w').write("\n".join(["\t".join(map(str, l)) for l in lines]))
