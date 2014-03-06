# -*- coding: UTF-8 -*-
#######################################################################
#
#    MyMetrixLite by arn354 & svox
#    based on
#    MyMetrix
#    Coded by iMaxxx (c) 2013
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################

from . import _, initWeatherConfig, COLOR_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from enigma import ePicLoad

#############################################################

class WeatherSettingsView(ConfigListScreen, Screen):
    skin = """
 <screen name="MyMetrixLiteWeatherView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <eLabel position="60,55" size="560,50" text="MyMetrixLite - MetrixWeather" font="Regular; 40" valign="center" transparent="1" backgroundColor="#00000000" />
    <widget name="config" position="61,114" size="590,500" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <widget source="info" position="61,590" size="590,66" render="Label" font="Regular; 18" foregroundColor="00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="70,640" size="160,30" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="257,640" size="160,30" text="Save" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
  </screen>
"""

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["helperimage"] = Pixmap()

        self["info"] = StaticText("")
        self["info"].setText(_("Get your local MetrixWeather ID from www.mymetrix.de"))

        initWeatherConfig()

        ConfigListScreen.__init__(
            self,
            self.getMenuItemList(),
            session = session,
            on_change = self.__changedEntry
        )

        self["actions"] = ActionMap(
        [
            "OkCancelActions",
            "DirectionActions",
            "InputActions",
            "ColorActions"
        ],
        {
            "left": self.keyLeft,
            "down": self.keyDown,
            "up": self.keyUp,
            "right": self.keyRight,
            "red": self.exit,
            "green": self.save,
            "cancel": self.exit
        }, -1)

        self.onLayoutFinish.append(self.UpdatePicture)

    def getMenuItemList(self):
        list = []

        list.append(getConfigListEntry(_("Enabled"), config.plugins.MetrixWeather.enabled, "WEATHER_ENABLED"))

        if config.plugins.MetrixWeather.enabled.getValue() is True:
            list.append(getConfigListEntry(_("MetrixWeather ID"), config.plugins.MetrixWeather.woeid))
            list.append(getConfigListEntry(_("Unit"), config.plugins.MetrixWeather.tempUnit))
            list.append(getConfigListEntry(_("Refresh Interval (min)"), config.plugins.MetrixWeather.refreshInterval))

        return list

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
        self.PicLoad.startDecode(COLOR_IMAGE_PATH % "MyMetrixLiteWeather")

    def DecodePicture(self, PicInfo = ""):
        ptr = self.PicLoad.getData()
        self["helperimage"].instance.setPixmap(ptr)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keyDown(self):
        self["config"].instance.moveSelection(self["config"].instance.moveDown)

    def keyUp(self):
        self["config"].instance.moveSelection(self["config"].instance.moveUp)

    def showInfo(self):
        self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

    def save(self):
        for x in self["config"].list:
            if len(x) > 1:
                x[1].save()
            else:
                pass

        configfile.save()
        self.exit()

    def exit(self):
        for x in self["config"].list:
            if len(x) > 1:
                    x[1].cancel()
            else:
                    pass
        self.close()

    def __changedEntry(self):
        cur = self["config"].getCurrent()
        cur = cur and len(cur) > 2 and cur[2]

        # change if type is BACKUP
        if cur == "WEATHER_ENABLED":
            self["config"].setList(self.getMenuItemList())
