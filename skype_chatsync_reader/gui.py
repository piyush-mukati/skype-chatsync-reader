#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.6.8 (standalone edition) on Thu Jan 22 07:21:12 2015
#

import wx
from wx.lib.pubsub import Publisher
import os
import os.path
from threading import Thread
import traceback
import warnings
from datetime import datetime
from .scanner import parse_chatsync_profile_dir

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class ChatSyncLoader(Thread):
    '''
    A thread object that loads the chatsync conversation objects from a given dirname.
    When finished sents the "conversations_loaded" message via wx.lib.pubsub.Publisher().
    '''
    
    def __init__(self, dirname):
        Thread.__init__(self)
        self.dirname = dirname
        self.start()
    
    def run(self):
        try:
            conversations = parse_chatsync_profile_dir(self.dirname)
        except:
            traceback.print_exc()
            conversations = []
        wx.CallAfter(Publisher().sendMessage, "conversations_loaded", conversations)


class ConversationSearcher(object):
    '''
    A utility class for implementing Find/FindNext in a list of conversation objects.
    '''
    
    def __init__(self, conversations=[]):
        self.conversations = conversations
        self.current_word = None
    
    def find(self, word):
        self.current_word = word
        self.current_conversation_id = 0
        self.current_message_id = 0
        return self.find_next()
    
    def find_next(self):
        if self.current_word is None or self.current_word == '' or len(self.conversations) == 0:
            return None
        while True:
            if self.current_word in self.conversations[self.current_conversation_id].conversation[self.current_message_id].text:
                result = (self.current_conversation_id, self.current_message_id)
                self.next_message()
                return result
            else:
                if not self.next_message():
                    break
        return False
        
    def next_message(self):
        if len(self.conversations) == 0:
            return False
        self.current_message_id += 1
        if self.current_message_id >= len(self.conversations[self.current_conversation_id].conversation):
            self.current_conversation_id = (self.current_conversation_id + 1) % len(self.conversations)
            self.current_message_id = 0
            if self.current_conversation_id == 0:
                return False
        return True
            
        
        
    
class MainFrame(wx.Frame):
    '''
    The main and only frame of the application.
    '''
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER)
        self.pane_left = wx.Panel(self.splitter, wx.ID_ANY, style=wx.STATIC_BORDER)
        self.list_conversations = wx.ListCtrl(self.pane_left, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER)
        self.pane_right = wx.Panel(self.splitter, wx.ID_ANY, style=wx.NO_BORDER)
        self.text_chatcontent = wx.TextCtrl(self.pane_right, wx.ID_ANY, u"Use Menu \u2192 Open to load the chatsync directory.", style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        # Menu Bar
        self.menubar = wx.MenuBar()
        self.mi_menu = wx.Menu()
        self.mi_open = wx.MenuItem(self.mi_menu, wx.ID_ANY, "&Open...\tCtrl+O", "Specify a chatsync directory to load files from", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.mi_open)
        self.mi_find = wx.MenuItem(self.mi_menu, wx.ID_ANY, "&Find...\tCtrl+F", "Search for text in messages", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.mi_find)
        self.mi_find_next = wx.MenuItem(self.mi_menu, wx.ID_ANY, "Find &next\tF3", "Search for the next occurrence of the same string in messages", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.mi_find_next)
        self.mi_menu.AppendSeparator()
        self.Exit = wx.MenuItem(self.mi_menu, wx.ID_ANY, "&Exit", "Exit", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.Exit)
        self.menubar.Append(self.mi_menu, "&Menu")
        self.SetMenuBar(self.menubar)
        # Menu Bar end

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_conversation_selected, self.list_conversations)
        self.Bind(wx.EVT_MENU, self.on_open, self.mi_open)
        self.Bind(wx.EVT_MENU, self.on_find, self.mi_find)
        self.Bind(wx.EVT_MENU, self.on_find_next, self.mi_find_next)
        self.Bind(wx.EVT_MENU, self.on_quit, self.Exit)
        # end wxGlade
        
        Publisher().subscribe(self.on_conversations_loaded, "conversations_loaded")
        self.searcher = ConversationSearcher()
        self.conversation_message_coords = []   # messageno ->(beginpos, endpos). Used to find begin and end points for selection highlights in the textbox.
        self.mi_find.Enable(False)
        self.mi_find_next.Enable(False)
        
    def __set_properties(self):
        # begin wxGlade: MainFrame.__set_properties
        self.SetTitle("Skype ChatSync File Viewer")
        self.SetSize((750, 420))
        self.text_chatcontent.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainFrame.__do_layout
        sizer_root = wx.BoxSizer(wx.HORIZONTAL)
        sizer_right = wx.BoxSizer(wx.VERTICAL)
        sizer_left = wx.BoxSizer(wx.HORIZONTAL)
        sizer_left.Add(self.list_conversations, 1, wx.ALL | wx.EXPAND, 0)
        self.pane_left.SetSizer(sizer_left)
        sizer_right.Add(self.text_chatcontent, 1, wx.ALL | wx.EXPAND, 0)
        self.pane_right.SetSizer(sizer_right)
        self.splitter.SplitVertically(self.pane_left, self.pane_right, 300)
        sizer_root.Add(self.splitter, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(sizer_root)
        self.Layout()
        # end wxGlade

    def on_open(self, event):  # wxGlade: MainFrame.<event_handler>
        default_dir = os.getenv('APPDATA', None)
        if default_dir is not None:
            default_dir = os.path.join(default_dir, 'Skype')
        else:
            default_dir = os.path.abspath('~/.Skype')
        dialog = wx.DirDialog(self, message='Please, select the "chatsync" directory within a Skype user profile:', defaultPath=default_dir, style=wx.DD_DIR_MUST_EXIST | wx.RESIZE_BORDER)
        if (dialog.ShowModal() == wx.ID_OK):
            self.list_conversations.ClearAll()
            self.text_chatcontent.Clear()
            self.text_chatcontent.SetValue("Please wait...")
            self.mi_open.Enable(False)
            ChatSyncLoader(dialog.GetPath())
            
    def on_quit(self, event):  # wxGlade: MainFrame.<event_handler>
        self.Close()

    def on_conversations_loaded(self, conversations):
        conversations = [c for c in conversations.data if not c.is_empty and len(c.conversation) > 0]
        conversations.sort(lambda x,y: x.timestamp - y.timestamp)
        self.conversations = conversations
        self.searcher = ConversationSearcher(conversations)
        
        if len(conversations) == 0:
            self.text_chatcontent.SetValue("Done. No non-empty conversations found or could be loaded.")
            self.mi_find.Enable(False)
            self.mi_find_next.Enable(False)
        else:
            self.text_chatcontent.SetValue("Done. Select a conversations using the list on the left to view.")
            self.mi_find.Enable()
            self.mi_find_next.Enable()
            self.list_conversations.ClearAll()
            self.list_conversations.InsertColumn(0, "Time")
            self.list_conversations.InsertColumn(1, "From")
            self.list_conversations.InsertColumn(2, "To")
            for c in conversations:
                dt = datetime.fromtimestamp(c.timestamp)
                self.list_conversations.Append((dt.strftime("%Y-%m-%d %H:%M"), c.participants[0], c.participants[1]))
        self.mi_open.Enable()
    
    def on_conversation_selected(self, event):  # wxGlade: MainFrame.<event_handler>
        sel_idx = self.list_conversations.GetFirstSelected()
        if sel_idx == -1:
            return
        if sel_idx >= len(self.conversations):
            self.text_chatcontent.SetValue("Error... :(")
        else:
            self.text_chatcontent.SetValue("")
            self.conversation_message_coords = []
            if len(self.conversations[sel_idx].conversation) == 0:
                self.text_chatcontent.AppendText("[empty]")
            total_len = 0
            for c in self.conversations[sel_idx].conversation:
                dt = datetime.fromtimestamp(c.timestamp).strftime("[%Y-%m-%d %H:%M]")
                txt = u"%s [%s]" % (dt, c.author)
                if c.is_edit:
                   txt += u" [edit]"
                txt += u": "
                txt += c.text + "\n"
                txt.replace('\r\n', '\n')
                text_len = len(txt)                 
                if len(os.linesep) == 2:
                    # Note that there is a discrepancy between lineseparators of the control's "Value" and its actual internal state
                    text_len += txt.count('\n')
                self.conversation_message_coords.append((total_len, total_len + text_len - 2))
                total_len += text_len
                self.text_chatcontent.AppendText(txt)

    def on_find(self, event):  # wxGlade: MainFrame.<event_handler>
        dlg = wx.TextEntryDialog(self,message="Enter text to search for:")
        if (dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != ''):
            result = self.searcher.find(dlg.GetValue())
            if result is None:
                wx.MessageBox(self, 'Text not found', 'Search result', wx.ICON_INFORMATION | wx.OK)
            else:
                self.highlight(result)
    
    def on_find_next(self, event):  # wxGlade: MainFrame.<event_handler>
        if self.searcher.current_word is None:
            self.on_find(event)
        else:
            result = self.searcher.find_next()
            if result is None:
                wx.MessageBox(self, 'Reached end of conversation list', 'Search result', wx.ICON_INFORMATION | wx.OK)
            else:
                self.highlight(result)
                
    def highlight(self, coords):
        self.list_conversations.Select(coords[0])
        wx.CallAfter(self.highlight_message, coords)
    
    def highlight_message(self, coords):
        if self.list_conversations.GetFirstSelected() == coords[0]:
            self.text_chatcontent.SetSelection(*self.conversation_message_coords[coords[1]])
            self.text_chatcontent.SetFocus()
            
# end of class MainFrame

class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        main_frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(main_frame)
        main_frame.Show()
        return 1

# end of class MyApp

def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == "__main__":
    main()