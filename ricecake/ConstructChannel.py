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

import os
import warnings

from ini2json import ini_to_json
from ricecooker.classes.nodes import ChannelNode, TopicNode, VideoNode, AudioNode, DocumentNode
from ricecooker.exceptions import FileNotFoundException
from exceptions import *

def construct_channel(**kwargs):

	#check path
	root_folder = kwargs[key]
	if not os.path.isdir(root_folder):
		raise FileNotFoundException("Invalid path. Path {0} does not exist".format([root_folder]))
	
	if not os.path.exists(os.path.join(root_folder,'/channelmetadata.ini')):
		raise FileNotFoundException("Invalid path. Path to '/channelmetadata.ini' does not exist within {0}".format([root_folder]))
	
	#check ini file
	channel_config = ini_to_json(os.path.join(root_folder,'/channelmetadata.ini'))
	if len(channel_config) < 1:
		raise InvalidConfigFile("Channel configuration file contains no channel sections")
		
	if len(channel_config) > 1:
		raise InvalidConfigFile("Channel configuration file contains multiple channel sections")
	
	#check folder to ensure only 1 "root" directory
	dirs = []
	for file in os.listdir(root_folder):
		if file != '.' and file != '..' and os.path.isdir(os.path.join(root_folder,file)):
			dirs.append(os.path.join(root_folder,file))		
	if len(dirs) < 1:
		raise InvalidRootFolder("Missing root channel folder in {0}".format([root_folder]))
	if len(dirs) > 1:
		raise InvalidRootFolder("Multiple root channel folders in {0}".format([root_folder]))
	
	channel = ChannelNode(
		source_domain 	= channel_config[0]["domain"],
		source_id 		= channel_config[0]["source_id"],
		title 			= channel_config[0]["title"],
		description 	= channel_config[0].get("description"),
		thumbnail 		= channel_config[0].get("thumbnail")
	)
	
	#start recursive channel build
	build_tree(channel,dirs[0])    

	return channel
	
def build_tree(parent_node,root_folder):

	#check ini file
	if not os.path.exists(os.path.join(root_folder,'/metadata.ini')):
		raise FileNotFoundException("Missing 'metadata.ini' configuration file in {0}".format([root_folder]))
		
	content_config = ini_to_json(os.path.join(root_folder,'/metadata.ini'))
	
	#loop directory
	for file in os.listdir(root_folder):
	
		# separate file name from ext
		file_name, ext = parse_file_name(file)
	
		#check to see is file exists in metadata.ini file
		if not content_config.get( file_name ):
				warnings.warn("File {0} has no configuration in {1}... SKIPPED".format([file,os.path.join(root_folder,'/metadata.ini')]))
				
		#if file is a directory, create TOPIC node and step into dir
		elif os.path.isdir(os.path.join(root_folder,file)) and file != '.' and file != '..':
			topic = TopicNode(
				source_id	= content_config[file_name]["id"],
				title		= content_config[file_name]["title"],
				author		= content_config[file_name].get("author"),
				description	= content_config[file_name].get("description"),
				thumbnail	= content_config[file_name].get("thumbnail"),
			)
			parent_node.add_child(topic)
			build_tree(topic,os.path.join(root_folder,file))
			
		elif ext == "mp4": #in VIDEO:
			child = VideoNode(
				source_id		= content_config[file_name]["id"],
				title			= content_config[file_name]["title"],
				license			= content_config[file_name].get("license"),
				author			= content_config[file_name].get("author"),
				description		= content_config[file_name].get("description"),
				derive_thumbnail= True, # video-specific data
				thumbnail		= content_config[file_name].get("thumbnail"),
			)
			add_files(child, content_config[file_name].get("files") or [])
			parent_node.add_child(child)
			
		elif ext == "mp3": #in AUDIO:
			child = AudioNode(
				source_id	= content_config[file_name]["id"],
				title		= content_config[file_name]["title"],
				license		= content_config[file_name].get("license"),
				author		= content_config[file_name].get("author"),
				description	= content_config[file_name].get("description"),
				thumbnail	= content_config[file_name].get("thumbnail"),
			)
			add_files(child, content_config[file_name].get("files") or [])
			parent_node.add_child(child)
		
		elif ext == "pdf": #in DOCUMENT:
			child = DocumentNode(
				source_id	= content_config[file_name]["id"],
				title		= content_config[file_name]["title"],
				license		= content_config[file_name].get("license"),
				author		= content_config[file_name].get("author"),
				description	= content_config[file_name].get("description"),
				thumbnail	= content_config[file_name].get("thumbnail"),
			)
			add_files(child, content_config[file_name].get("files") or [])
			parent_node.add_child(child)
			
		else:
			continue
		
def parse_file_name(file):
	if file:
		fp = file.split('.')
		if len(fp) == 1:
			return (''.join(fp), None)
		else:
			return (''.join(fp[:-1]), fp[-1])
	else:
		return None