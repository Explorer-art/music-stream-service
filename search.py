import os
import re
import requests
from bs4 import BeautifulSoup

class Track:
	def __init__(self, title=None, artist=None, url=None, duration=None, image_url=None, download_url=None):
		self.title = title
		self.artist = artist
		self.duration = duration
		self.image_url = image_url
		self.download_url = download_url

	def download(self, filename=None, directory=None):
		if filename is None:
			filename = os.path.basename(self.download_url)

		if directory is None:
			directory = os.getcwd()

		response = requests.get(self.download_url)

		with open(directory + "/" + filename, "wb") as file:
			file.write(response.content)

class Hitmo:
	def __init__(self, url = "https://rus.hitmotop.com"):
		self.query = None
		self.url = url

	def search(self, query):
		self.query = query

		try:
			response = requests.get(self.url + "/search?q=" + query.replace(" ", "+"))

			if response.status_code != 200:
				raise Exception("Error GET request")

			soup = BeautifulSoup(response.text, "html.parser")

			track_list = soup.find("ul", class_="tracks__list").find_all("li")

			if not track_list:
				raise("Track list not found")

			results = []

			for track in track_list:
				track_title = track.find("div", class_="track__title").text.strip()
				track_artist = track.find("div", class_="track__desc").text
				track_duration = track.find("div", class_="track__fulltime").text
				track_image_styles = track.find("div", class_="track__img").get("style")
				track_image_url = re.search(r"url\(['\"]?([^'\"]+)['\"]?\)", track_image_styles).group(1)
				track_download_url = track.find("a", class_="track__download-btn", href=True)["href"]

				track_data = Track(
					title=track_title,
					artist=track_artist,
					duration=track_duration,
					image_url = track_image_url,
					download_url=track_download_url)

				results.append(track_data)

			return results
		except:
			return None