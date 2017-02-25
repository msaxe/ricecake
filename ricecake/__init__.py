import argparse
from subprocess import call
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Upload folder as channel.')
	parser.add_argument('token', help='Your account token')
	parser.add_argument('path', help='Path to channel folder')
	args = parser.parse_args()
	
	call(['python','-m','ricecooker','uploadchannel',
		  'ConstructChannel.py',
		  ''.join(['--token=',args.token]),
		  ''.join(['folder_path=',args.path])
		  ])