# -*- coding: utf-8 -*-
import subprocess
from crontab import CronTab

from adapt.intent import IntentBuilder
from os.path import dirname
import urllib
import urllib2
from bs4 import BeautifulSoup

from mycroft.skills.core import MycroftSkill


class AVmusicSkill(MycroftSkill):
    def __init__(self):
        super(AVmusicSkill, self).__init__(name="AVmusicSkill")
        self.process = None

    def initialize(self):
        playnow_intent = IntentBuilder("playnow_intent"). \
            require("AgreementKeyword").build()
        self.register_intent(playnow_intent, self.handle_playnow_intent)

        pause_intent = IntentBuilder("pause_intent"). \
            require("PauseKeyword").build()
        self.register_intent(pause_intent, self.handle_pause_intent)
        self.disable_intent('pause_intent')

        not_now_intent = IntentBuilder("not_now_intent"). \
            require("DeclineKeyword").build()
        self.register_intent(not_now_intent, self.handle_not_now_intent)

        AVmusic = IntentBuilder("AVmusicKeyword"). \
            require("AVmusicKeyword").build()
        self.register_intent(AVmusic, self.AVmusic)

        self.load_data_files(dirname(__file__))

        self.disable_intent('playnow_intent')
        self.disable_intent('not_now_intent')

    @staticmethod
    def search(text):
        query = urllib.quote(text)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
            if not vid['href'].startswith(u"https://googleads.g.doubleclick.net/‌​") \
                    and not vid['href'].startswith(u"/user") and not vid['href'].startswith(u"/channel"):
                return "http://www.youtube.com/" + vid['href']

    def AVmusic(self, message):
        self.stop()
        self.speak('Would you like me to play it now?')

        utterance = message.data.get('utterance').lower()
        utterance = utterance.replace(
               message.data.get('AVmusicKeyword'), '')
        self.vid = self.search(utterance)

        self.enable_intent('playnow_intent')
        self.enable_intent('not_now_intent')

    def handle_playnow_intent(self,message):
        try:
            self.process = subprocess.Popen(["mpv", self.vid],
                                            stdin=subprocess.PIPE)
            self.enable_intent('pause_intent')
            self.speak_dialog('SayStop')

        except TypeError:
            self.speak_dialog('TryAgain')
            self.stop()

        self.disable_intent('not_now_intent')
        self.disable_intent('playnow_intent')

    def handle_not_now_intent(self, message):
        self.speak_dialog('ChangeMind')
        self.disable_intent('not_now_intent')

    def handle_pause_intent(self, message):
        self.process.Popen.communicate("P")

    def stop(self):
        if self.process:
            self.process.terminate()
        pass


def create_skill():
    return AVmusicSkill()
