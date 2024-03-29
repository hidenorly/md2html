#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (C) 2016, 2023 hidenorly
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import markdown
from optparse import OptionParser, OptionValueError
import sys
import codecs
import subprocess

cset = 'utf-8'

html_header = '''<!DOCTYPE html>
<html>
<head>
	<meta charset="'''
html_header_cset_title = '''">
	<title>'''
html_css = '''<link rel="stylesheet" type="text/css" href="'''
html_header_title_css = '''</title>
	''' + html_css
html_header_css_body = '''">
</head>
<body>
'''

html_fotter = '''
</body>
</html>
'''

def fileRead(filename):
	if filename == sys.stdin:
		reader = filename
	else:
		reader = open(filename, "r", encoding=cset)

	buf = ""
	for line in reader:
		buf = buf + line

	reader.close()
	return buf

def fileWriter(filename, buf):
	if filename == None:
		print(buf)
	else:
		writer = open(filename, "w", encoding=cset)
		writer.write(buf)
		writer.close()

def getExecResult(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout_data, stderr_data = p.communicate()
	return stdout_data.decode('utf-8')

def replaceResult(inBuf, replacers):
	result = inBuf

	for aReplacer in replacers:
		posE = aReplacer.find("=")
		if posE!=-1:
			key = aReplacer[0:posE]
			keyLen = len(key)
			value = aReplacer[posE+1:len(aReplacer)]
			pos = 0
			while pos!=-1:
				pos = result.find(key, pos)
				if pos!=-1:
					result = result[0:pos] + value + result[pos+keyLen:len(result)]
					pos = pos + keyLen

	return result

def getValWithStrip(cmd):
	posE = cmd.find("=")
	val = None
	if posE != -1:
		val = cmd[posE+1:len(cmd)]
		if val[0]=='"' or val[0]=="'":
			val = val[1:len(val)]
		if val[len(val)-1]=='"' or val[len(val)-1]=="'":
			val = val[0:len(val)-1]
	return val

def doTinyTemplate(cmd):
	result = cmd
	val = getValWithStrip(cmd)

	if ("include" in cmd) and val != None:
		result = fileRead(val)
	elif ("exec" in cmd) and val != None:
		result = getExecResult(val)

	return result

def tinyTemplate(inBuf):
	result = inBuf
	pos = result.find("<%")
	while pos != -1:
		pos2 = result.find("%>", pos)
		if pos2 == -1:
			break
		cmd = result[pos+2:pos2]
		tempResult = doTinyTemplate(cmd)
		result = result[0:pos] + tempResult + result[pos2+2:len(result)]
		pos = result.find("<%", pos+len(tempResult))

	return result

def addPreStringIfNeed(result, key, preVal, pos):
	pos = result[0].find(key, pos)
	if pos!=-1:
		pos = pos + len(key) + 1
		if not result[0][pos:pos+7] == "http://" and not result[0][pos:pos+8] == "https://":
			# found relative link, should add cid:
			result[0] = result[0][0:pos] + preVal + result[0][pos:len(result[0])]
	return pos


def linkConvert(inBuf):
	result = [inBuf]

	pos = 0
	pos2 = 0
	while pos!=-1 or pos2!=-1:
		# href link
		pos = addPreStringIfNeed(result, "href=", "cid:", pos)
		pos2 = addPreStringIfNeed(result, "src=", "cid:", pos2)

	return result[0]

def embedCSS(result, cssFile):
	posS = result.find(html_css)
	posE = result.find('''">''', posS)
	if posS!=-1 and posE!=-1:
		css = fileRead(cssFile)
		result = result[0:posS] + '''<style type="text/css">
<!--
''' + css + '''
//!-->
</style>''' + result[posE+2:len(result)]

	return result

def expandMultipleArgs(args):
	if args is not None:
		if isinstance(args, list) and len(args)==1:
			if args[0].find(",")!=-1:
				args = args[0].split(",")
	else:
		args = []

	return args

if __name__ == '__main__':
	md = markdown.Markdown(
		extensions=[
			'markdown.extensions.extra',
			'markdown.extensions.nl2br',
			'markdown.extensions.sane_lists',
			'markdown.extensions.smarty',
			'pymdownx.emoji',
			'pymdownx.tasklist',
			'pymdownx.superfences',
			'pymdownx.details',
			'pymdownx.tilde',
			'pymdownx.highlight',
			'pymdownx.inlinehilite'
		]
	)
	parser = OptionParser()

	parser.add_option("-t", "--title", action="store", type="string", dest="title", default="", help="Specify title")
	parser.add_option("-c", "--charset", action="store", type="string", dest="charset", default=cset, help="Specify charset")
	parser.add_option("-o", "--output", action="store", type="string", dest="outFilename", default=None, help="Specify output filename")
	parser.add_option("-s", "--css", action="store", type="string", dest="css", default="bootstrap-md.css", help="Specify css filename")
	parser.add_option("-m", "--mode", action="store", type="string", dest="mode", default="web", help="Specify web or email")
	parser.add_option("-r", "--replace", action="append", type="string", dest="replacers", default=None, help="Specify replace key=value,...")
	parser.add_option("-b", "--bodyonly", action="store_true", dest="bodyonly", default=False, help="--b if no header/footer")

	(options, args) = parser.parse_args()

	inFilename = sys.stdin
	if args:
		inFilename = args[0]

	# set charset
	cset = options.charset

	# get key-value for replacement
	replacers = expandMultipleArgs( options.replacers )

	# read markdown
	buf = fileRead(inFilename)

	# Pre-filter : tiny template engine
	buf = replaceResult(buf, replacers)
	buf = tinyTemplate(buf)

	# convert markdown
	result = md.convert(buf)

	# create complete html
	if not options.bodyonly:
		result = html_header + options.charset + html_header_cset_title + options.title + html_header_title_css + options.css + html_header_css_body + result + html_fotter

	# Post filter
	result = replaceResult(result, replacers)

	# replace href link
	if options.mode.find("email")!=-1:
		result = embedCSS(result, options.css)
		result = linkConvert(result)

	# output the processed html
	fileWriter( options.outFilename, result )