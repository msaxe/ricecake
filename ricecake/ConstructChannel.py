# MIT License

# Copyright (c) 2017 Mark Saxer

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os, sys
import warnings

from ricecooker.classes 	  	import files
from ricecooker.classes.nodes 	import ChannelNode, TopicNode, VideoNode, AudioNode, DocumentNode
from ricecake.ini2json 			import ini_to_json
from ricecake.exceptions 		import *

def construct_channel(**kwargs):

	#check path
	root_folder = kwargs['folder_path']
	if not os.path.isdir(root_folder):
		raise FileNotFoundException("Invalid path! Path {0} does not exist".format(root_folder))
	
	if not os.path.exists(os.path.join(root_folder,'channelmetadata.ini')):
		raise FileNotFoundException("Invalid path! Path to configuration file '{0}/channelmetadata.ini' does not exist".format(root_folder))
	
	#check ini file
	channel_config = ini_to_json(os.path.join(root_folder,'channelmetadata.ini'))
	if len(list(channel_config)) < 1:
		raise InvalidConfigFile("Channel configuration file contains no channel sections")
		
	if len(list(channel_config)) > 1:
		raise InvalidConfigFile("Channel configuration file contains multiple channel sections")
	
	#check folder to ensure only 1 "root" directory
	dirs = []
	for file in os.listdir(root_folder):
		if file != '.' and file != '..' and os.path.isdir(os.path.join(root_folder,file)):
			dirs.append(os.path.join(root_folder,file))		
	if len(dirs) < 1:
		raise InvalidRootFolder("Missing root channel folder in {0}".format(root_folder))
	if len(dirs) > 1:
		raise InvalidRootFolder("Multiple root channel folders in {0}".format(root_folder))
	
	channel_sec = list(channel_config)[0]
	channel = ChannelNode(
		source_domain 	= channel_config[channel_sec]["domain"],
		source_id 		= channel_config[channel_sec]["source_id"],
		title 			= channel_config[channel_sec]["title"],
		description 	= channel_config[channel_sec].get("description"),
		thumbnail 		= channel_config[channel_sec].get("thumbnail")
	)
	
	#start recursive channel build
	build_tree(channel,dirs[0])    

	return channel
	
def build_tree(parent_node,root_folder):

	#check ini file
	if not os.path.exists(os.path.join(root_folder,'metadata.ini')):
		raise FileNotFoundException("Missing 'metadata.ini' configuration file in {0}".format([root_folder]))
		
	content_config = ini_to_json(os.path.join(root_folder,'metadata.ini'))
	
	#loop directory
	for file in os.listdir(root_folder):
	
		# separate file name from ext
		file_name, ext = parse_file_name(file)
	
		#check to see is file exists in metadata.ini file
		if not content_config.get( file_name ):
			if ext != 'ini':
				warnings.warn("File {} has no configuration in {}... SKIPPED".format(file,os.path.join(root_folder,'metadata.ini')))
				
		#if file is a directory, create TOPIC node and step into dir
		elif os.path.isdir(os.path.join(root_folder,file)) and file != '.' and file != '..':
			topic = TopicNode(
				source_id	= content_config[file_name]["__name__"],
				title		= content_config[file_name]["title"],
				author		= content_config[file_name].get("author"),
				description	= content_config[file_name].get("description"),
				thumbnail	= content_config[file_name].get("thumbnail"),
			)
			parent_node.add_child(topic)
			build_tree(topic,os.path.join(root_folder,file))
			
		elif ext == "mp4": #in VIDEO:
			child = VideoNode(
				source_id		= content_config[file_name]["__name__"],
				title			= content_config[file_name]["title"],
				license			= content_config[file_name].get("license"),
				author			= content_config[file_name].get("author"),
				description		= content_config[file_name].get("description"),
				derive_thumbnail= True, # video-specific data
				thumbnail		= content_config[file_name].get("thumbnail"),
			)
			add_files(child, [os.path.join(root_folder,file)] + (content_config[file_name].get("files") or []))
			parent_node.add_child(child)
			
		elif ext == "mp3": #in AUDIO:
			child = AudioNode(
				source_id	= content_config[file_name]["__name__"],
				title		= content_config[file_name]["title"],
				license		= content_config[file_name].get("license"),
				author		= content_config[file_name].get("author"),
				description	= content_config[file_name].get("description"),
				thumbnail	= content_config[file_name].get("thumbnail"),
			)
			add_files(child, [os.path.join(root_folder,file)] + (content_config[file_name].get("files") or []))
			parent_node.add_child(child)
		
		elif ext == "pdf": #in DOCUMENT:
			child = DocumentNode(
				source_id	= content_config[file_name]["__name__"],
				title		= content_config[file_name]["title"],
				license		= content_config[file_name].get("license"),
				author		= content_config[file_name].get("author"),
				description	= content_config[file_name].get("description"),
				thumbnail	= content_config[file_name].get("thumbnail"),
			)
			add_files(child, [os.path.join(root_folder,file)] + (content_config[file_name].get("files") or []))
			parent_node.add_child(child)
			
		else:
			continue

def add_files(node, file_list):
	for f in file_list:
		file_name, file_type = parse_file_name(f)
		print (f)
		if file_type == 'mp3':#FileTypes.AUDIO_FILE:
			node.add_file(files.AudioFile(path=f))
		#elif file_type == FileTypes.THUMBNAIL:
		#	node.add_file(files.ThumbnailFile(path=f['path']))
		elif file_type == 'pdf':#FileTypes.DOCUMENT_FILE:
			node.add_file(files.DocumentFile(path=f))
		#elif file_type == FileTypes.HTML_ZIP_FILE:
		#	node.add_file(files.HTMLZipFile(path=f['path'], language=f.get('language')))
		elif file_type == 'mp4':#FileTypes.VIDEO_FILE:
			node.add_file(files.VideoFile(path=f))
		#elif file_type == FileTypes.SUBTITLE_FILE:
		#	node.add_file(files.SubtitleFile(path=f['path'], language=f['language']))
		#elif file_type == FileTypes.BASE64_FILE:
		#	node.add_file(files.Base64ImageFile(encoding=f['encoding']))
		#elif file_type == FileTypes.WEB_VIDEO_FILE:
		#	node.add_file(files.WebVideoFile(web_url=f['web_url'], high_resolution=f.get('high_resolution')))
		#elif file_type == FileTypes.YOUTUBE_VIDEO_FILE:
		#	node.add_file(files.YouTubeVideoFile(youtube_id=f['youtube_id'], high_resolution=f.get('high_resolution')))
		else:
			raise UnknownFileTypeError("Unrecognised file type '{0}'".format(f['path']))
			
def parse_file_name(file):
	if file:
		fp = file.split('.')
		if len(fp) == 1:
			return (''.join(fp), None)
		else:
			return (''.join(fp[:-1]), fp[-1])
	else:
		return None
		
if __name__ == '__main__':
	keyargs = {'folder_path':sys.argv[1],'display':True}
	construct_channel(**keyargs)