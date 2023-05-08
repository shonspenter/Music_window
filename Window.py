import wx
import vlc
import os
import eyed3
import numpy as np

mp3_directory = "mp3"

song_dict = {f:{"location":os.path.join(mp3_directory,f)} for f in os.listdir(mp3_directory) if os.path.isfile(os.path.join(mp3_directory,f))}

for i,song in enumerate(song_dict.keys()):
    song_dict[song]["album"] = eyed3.load(song_dict[song]["location"]).tag.album
    song_dict[song]["ID"] = i

#All the different albums
Albums_dict = {a:{"ID":i,"Occurences":[sd["album"]for sd in song_dict.values()].count(a)} for i,a in enumerate(np.unique([sd["album"]for sd in song_dict.values()]))}


class Music_Panel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        self.playing_dict = {}
        self.player_dict = {}
        self.button_dict = {}

        prev_occ = 0
        for album,album_dict in Albums_dict.items():            
            occ = album_dict["Occurences"]
            
            Albums_dict[album]["staticbox"] = wx.StaticBox(self,label=album,pos=(5,10+50*prev_occ),size=(550,50*(occ+0.5)))
            prev_occ += occ+0.5
            Albums_dict[album]["nrChildren"] = 0

        for song in song_dict.keys():
            ID = song_dict[song]["ID"]
            album = song_dict[song]["album"]
            i = Albums_dict[album]["nrChildren"] 
            playbutton=wx.Button(Albums_dict[album]["staticbox"],ID,song,(15,50*i+30))
            self.button_dict[ID] = playbutton

            self.playing_dict[ID] = False
            p = vlc.MediaPlayer(song_dict[song]["location"])
            self.player_dict[ID] = p

            self.Bind(wx.EVT_BUTTON,self.Play_song,playbutton)
            Albums_dict[album]["nrChildren"] +=1

        self.Center()
    

    def Play_song(self,event):
        Id = event.GetId()
        p =  self.player_dict[Id] 

        song = [song for song,sd in song_dict.items() if sd["ID"]==Id][0]

        if not self.playing_dict[Id]:
            p.play()
            button = self.button_dict[Id]
            button.SetLabel("(playing) "+song)
            button.SetSize((button.GetSize()[0]+60,button.GetSize()[1]))
            self.playing_dict[Id] = True

        else:
            p.stop()
            button = self.button_dict[Id]
            button.SetLabel(song)
            button.SetSize((button.GetSize()[0]-60,button.GetSize()[1]))
            self.playing_dict[Id] = False





def main():

    app = wx.App()
    frame = wx.Frame(None,size=(900, 800), title='Music master+')
    Music_Panel(frame)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()