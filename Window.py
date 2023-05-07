import wx
import vlc
import time


mp3_directory = "mp3"

class Music_window():

    def __init__(self, parent, title):
        self.frame = wx.Frame(parent, title=title,size=(900, 800))

        self.panel = wx.Panel(self.frame, wx.ID_ANY)
        self.playbutton=wx.Button(self.panel,wx.ID_ANY,"test",(10,10))
        song = "vo.mp3"
        media = vlc.MediaPlayer(mp3_directory+"/"+song)
        self.playbutton.Bind(wx.EVT_BUTTON,self.Play_song(media))

        self.frame.Centre()
    

    def Play_song(self,media):
        media.play()
        #time.sleep(15)
        #media.stop()




def main():

    app = wx.App()
    Mw = Music_window(None, title='Music master+')
    Mw.frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()