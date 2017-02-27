import sys, json
from configparser import ConfigParser

def ini_to_json(ini_file):

	config = ConfigParser()
	config.read(ini_file)

	dictionary = {}
	for section in config.sections():
		dictionary[section] = {}
		dictionary[section]['__name__'] = section
		for option in config.options(section):
			dictionary[section][option] = config.get(section, option)
			
	return dictionary

if __name__ == "__main__":
    if len(sys.argv) > 1:
        f = sys.argv[1]
    else:
        f = sys.stdin
    print (json.dumps(ini_to_json(f),sort_keys=True,indent=4))