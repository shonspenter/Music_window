import wx
import vlc
import os
import eyed3
import numpy as np
import time
import csv

#Having two sliders for different audio seems a little impossible unfortunately.

class Song:
    def __init__(self,location,soundtrack):
        self.location = location
        self.soundtrack = soundtrack
        self.p = None
        self.length = None
        self.volume = None

        self.name =str(os.path.basename(location)).split(".mp3")[0]
        self.album = str(eyed3.load(location).tag.album)
        self.track_num = eyed3.load(location).tag.track_num[0]
        self.genre = str(eyed3.load(location).tag.genre).split(')',1)[-1]

        self.Playing = False
        self.Playing_ID = None
        #Determine how a loop should play (loop start is prob at 7.131 in base) (loop end is around 3m 20s)

class Genre:
    def __init__(self,name,Album=None):
        self.name = name
        self.Songdict = {}
    
    def AddSong(self,song):
        if song.genre == self.name:
            self.Songdict[song.name] = song
        else:
            print(f"can't add song with genre {song.genre} to genre with name {self.name}")

class Album:
    def __init__(self,name):
        self.name = name
        self.totSongs = 0
        self.totGenres = 0
        self.Songdict = {}
        self.Genredict = {}
        self.AllSongdict = {}
                
        self.num_playing = 0
        self.Max_songs = 0
        self.Buttondict = {}
        self.SliderTextdict = {}
    
    def AddSong(self,song):
        if song.genre is None:
            if song.album == self.name:
                self.Songdict[song.name] = song
                self.AllSongdict[song.name] = song
                self.totSongs +=1
            else:
                print(f"can't add song with album {song.album} to album with name {self.name}")
        else:
            if song.genre not in self.Genredict.keys():
                self.AddGenre(Genre(song.genre))
            self.Genredict[song.genre].AddSong(song)
            self.AllSongdict[song.name] = song
            self.totSongs +=1
        

    def AddGenre(self,Genre):
        if Genre.name not in self.Genredict.keys():
            self.Genredict[Genre.name] = Genre
            self.totGenres += 1
        else:
            print(f"can't add Genre with name {Genre.name} to album with name {self.name}")

class Music_Panel(wx.Panel):

    def __init__(self, parent,Albumdict):
        wx.Panel.__init__(self,parent)
        self.playingDict = {}

        self.start_volume = 40
        self.Max_songs = {"Queen_fight": 2,"Background":1}
        self.sliderwidth = 100
        self.sliderheight = 150

        self.button_length = 30
        self.button_delta = 0
        self.Genrebox_delta = 20
        self.Albumbox_delta = 20
        self.xtop = 5
        
        ytop = 10
        ID = 0
        num_sliders = 0
        for i,album in enumerate(Albumdict.values()):        
            album.Max_songs = self.Max_songs[album.name] if album.name in self.Max_songs.keys() else 1 

            #value 550 should depend on longest title string
            length = (self.button_length+self.button_delta)*album.totSongs+2*self.Albumbox_delta +self.Genrebox_delta*album.totGenres
            Box = self.MakeStaticBox(album,(self.xtop,ytop),(550,length))
            num_sliders = self.MakeSliders(num_sliders,album,ytop)
            ytop += self.Albumbox_delta
            
            for j,genre in enumerate(album.Genredict.values()):                
                length = len(genre.Songdict)*(self.button_length+self.button_delta) + self.Genrebox_delta
                Box = self.MakeStaticBox(genre,(self.xtop*4,ytop),(500,length))
                ytop += self.Genrebox_delta
                for k, song in enumerate(genre.Songdict.values()):
                    Button = self.MakeButton(album,song,ID,(self.xtop*6,ytop))

                    ID +=1
                    ytop += self.button_length+self.button_delta
            ytop += self.Albumbox_delta

        self.Center()


    def MakeStaticBox(self,Container,pos,size):
        Box = wx.StaticBox(self,label=Container.name,pos=pos,size=size)
        Container.StaticBox = Box
        return Box
    
    def MakeButton(self,album,song,ID,pos):
        Button = wx.Button(self,id=ID,label=song.name,pos=pos)
        album.Buttondict[ID] = Button
        song.Button = Button

        self.Bind(wx.EVT_BUTTON,lambda event: self.Play_song(event,song,album),Button)
        return Button
    
    def MakeSliders(self,ID,album,y):
        for id in range(album.Max_songs):
            soundslider = wx.Slider(self, id=ID, value=self.start_volume, minValue=0, maxValue=100, pos= (600+self.sliderwidth*id,y), style= wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE)
            self.Bind(wx.EVT_SCROLL,lambda event: self.Change_volume(event,id,album),soundslider)
            Slidertext = wx.StaticText(self,label="",pos = (575+self.sliderwidth*id*1.25,y+self.sliderheight+25*id))
            album.SliderTextdict[id] = Slidertext
            ID+=1
        return ID

    def Play_song(self,event,song,album):
        button = event.GetEventObject()
        print(song.name,album.name)
        #Get the player (p)
        if song.p != None:
            p = song.p
        else:
            p = vlc.MediaPlayer(song.location)
            p.audio_set_volume(song.volume if song.volume != None else self.start_volume)
            song.p = p
            song.length = p.get_length()
        

        #If the song is already playing (stop it)
        if song.Playing:
            self.playingDict[song.album].pop((song.Playing_ID))
            print(self.playingDict)
            album.SliderTextdict[song.Playing_ID].SetLabel("")
            p.stop()
            song.p = None
            button.SetLabel(song.name)
            button.SetSize((button.GetSize()[0]-5,button.GetSize()[1]))
            song.Playing = False
            song.Playing_ID = None
            album.num_playing -= 1
            print(f"DEBUG: number of songs playing in album {album.name}: {album.num_playing}")

        #If the song is not playing yet and there are not too many songs playing
        elif not song.Playing and album.num_playing < album.Max_songs:            
            #If there are more than one song playing
            if album.num_playing >= 1:
                song2 =list(self.playingDict[song.album].values())[0]
                p2 = song2.p
                p2.stop()
                p.play()
                #p.set_time(p2.get_time())
                p2.play()
                time.sleep(10)
                self.Syncplayers(p,p2)
                song.Playing_ID = min([x for x in range(album.Max_songs) if x not in self.playingDict[song.album].keys()])
            else:
                p.play()
                song.Playing_ID = 0
            
            button.SetLabel(f"{song.Playing_ID}: {song.name}")
            button.SetSize((button.GetSize()[0]+5,button.GetSize()[1]))
            song.Playing = True
            album.SliderTextdict[song.Playing_ID].SetLabel(song.name)
            if song.album not in self.playingDict.keys():
                self.playingDict[song.album] = {song.Playing_ID:song}
            else:
                self.playingDict[song.album][song.Playing_ID] = song

            print(self.playingDict)
            album.num_playing += 1
            print(f"DEBUG: number of songs playing in album {album.name}: {album.num_playing}")
        
    def Syncplayers(self,p1,p2):
        pt = p1.get_time()
        p2t = p2.get_time()
        dt = abs(p2t-pt)
        print(pt,p2t)
        if pt > p2t:
            p1.pause()
            time.sleep(dt/1000)
            p1.play()
        else:
            p2.pause()
            time.sleep(dt/1000)
            p2.play()


    def Change_volume(self,event,id,album):
        slider = event.GetEventObject()
        vol = slider.Value
        songsplaying = {song.Playing_ID: song for song in album.AllSongdict.values() if song.Playing}
        for song in songsplaying.values():
            print(song.p.get_time())
        if len(songsplaying) > id:
            song = songsplaying[id]
            song.p.audio_set_volume(vol)
            song.volume = vol

def main():
    mp3_directory = "mp3"
    Songdict = {}
    Albumdict = {}
    soundtrack = 0
    for f in os.listdir(mp3_directory):
        location = os.path.join(mp3_directory,f)
        if os.path.isfile(location):
            S = Song(location,soundtrack)
            Songdict[S.name] = S
            if S.album not in Albumdict.keys():
                Albumdict[S.album] = Album(S.album)
            Albumdict[S.album].AddSong(S)
            soundtrack += 1

    app = wx.App()
    frame = wx.Frame(None,size=(900, 1500), title='Music master+')
    Music_Panel(frame,Albumdict)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

