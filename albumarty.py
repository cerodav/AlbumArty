'''
Error#1 Multiple source taking incase of --max
Error#3 Limiting the range of app activity to within a folder and not reccursively deep
'''
import os
import argparse
import re
import sys
import urllib.request as urllib2
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import eyed3
import eyed3.id3

class albumarty(object):
	def __init__(self,location=None,searchoption='min'):
		self.location=location
		self.searchoption=searchoption
		if self.location == None:
			sys.exit("\n##Please specify location of directory containing the music files\n")
		self.main()

	def art_source_fetch(self,searchtag):
		searchtag=searchtag.replace(" ","+")
		search_url='http://www.covermytunes.com/search.php?search_query=%s&x=0&y=0' % (searchtag)
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

		try: 
			html_req=urllib2.Request(search_url,headers=hdr)
			html=urllib2.urlopen(html_req)
		except urllib2.HTTPError:
			try:
				html_req=urllib2.Request(search_url,headers=hdr)
				html=urllib2.urlopen(html_req)
			except urllib2.HTTPError:
				logging.warning("An error occured while getting the results for albumart search. Please try again")

		soup=BeautifulSoup(html.read())

		src=[]
		if self.searchoption=='max':
			
			productImage=soup.find_all(class_="ProductImage")
			sort1=[]
			try:
				for files in productImage:
					if files:
						sort1.append(files.find("img"))
			except:
				sort1=""

			try:
				for files in sort1:
					if files:
						src.append(files.get('src'))
			except:
				src=""

			#dir(productImage)
			return src

		else:
			productImage=soup.find(class_="ProductImage")
			try:
				if productImage:
					productImage=productImage.find("img")
			except:
				productImage=False

			try:
				if productImage:
					src.append(productImage.get('src'))
				else:
					src=""
			except:
				src=""

			print(src)
			return src

	def setalbumart(self,songname,song_filename,location):
		albumart_path=location+'/albumarty/'+songname+'.jpeg'
		song_path=location+'/'+song_filename

		#sys.stdout.write("\n%s\n" % (song_path))

		if os.path.exists(song_path):
			try:
				audio = ID3(song_path)
			except error:
				audio=MP3(song_path)
				audio.add_tags()
				audio=ID3(song_path)


			insert_image=APIC(3,u'image/jpeg',3,songname,open(albumart_path,'rb').read())
			audio.add(insert_image)
			audio.save()

			'''
			Refer to format for APIC frames from here
			APIC(
        	encoding=0, # 3 is for utf-8
        	mime='image/jpeg', # image/jpeg or image/png
        	type=3, # 3 is for the cover image
        	desc=u'Cover',
        	data=open(albumart_path,encoding="Latin-1").read()
    		)
			
			'''

		else:
			sys.stdout.write("\n##Nothing\n")

	def main(self):
		filenames=self.verify(self.location)

		for filename in filenames:
			sys.stdout.write("\nSongname : %s ---------\n" % (filename['song_name']))
			src=self.art_source_fetch(filename['song_name'])
			
			if src == "" or not src:
				sys.stdout.write("\n++ No matching album arts found ## Sorry\n")
				continue
			else:
				for source in src:
					if self.downloadart(source,filename['song_name'],self.location):
						sys.stdout.write("\n++ Download complete ## Setting albumart\n")
						self.setalbumart(filename['song_name'],filename['file_name'],self.location)
						if self.searchoption=='max':
							sys.stdout.write("\n++ Setting Albumart complete ## Is that the correct album art ? (Y/N) ")
							choice=input("")
							if choice=='y' or choice=='Y':
								break
						else:
							break


	def downloadart(self,source,artname,location):
		url_res=urllib2.urlopen(source)

		if not os.path.exists(location+'/albumarty/'):
			os.makedirs(location+'/albumarty/')

		path=location+'/albumarty/'
		file_res=open(path+artname+'.jpeg','wb')

		meta=url_res.info()

		file_size = int(meta.get_all("Content-Length")[0])
		
		file_size_dl = 0
		block_size = 8192
		while True:
			buffer = url_res.read(block_size)
			if not buffer:
				break
				file_size_dl += len(buffer)
			file_res.write(buffer)
		file_res.close()
		return True;

	def verify(self,location):
		if not os.path.exists(location):
			sys.exit("\n## Please specify a valid directory location\n")

		mp3tag=re.compile('.mp3')
		count=0
		file_results=[]

		for (dirpath,dirnames,filenames) in os.walk(location):
			for f_name in filenames:
				#sys.stdout.write("%s"%filename)
				result=mp3tag.findall(str(f_name))
				if result:
					#sys.stdout.write("%s"%str(f_name))
					count=count+1
					filename_clear=str(f_name).replace(".mp3","")
					node={}
					node['song_name']=filename_clear
					node['file_name']=f_name
					file_results.append(node)

		if count==0:
			sys.exit("\n## The location doesnt contain any MP3 files, try another location\n")
		sys.stdout.write("\n++ Number of MP3 files found in location : %d\n" %count)

		return file_results

def main():
	try:
		parser=argparse.ArgumentParser(description="Adds Album Art To All The Songs Preset Within The Given Destination")
		parser.add_argument('--max',dest='searchoption',action='store_const',const='max',default='min',help='Efficiency of search (Default: Minimum time, weak matching)')
		parser.add_argument('location',help='The location or directory containing the music files')

		args=parser.parse_args()

		albumarty(args.location,args.searchoption)

	except KeyboardInterrupt:
		sys.exit("\nProgram was closed by user\n")

if __name__=='__main__':
	main()