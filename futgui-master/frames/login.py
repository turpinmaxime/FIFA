import tkinter as tk
import json
import core.constants as constants

from frames.base import Base
from api.delayedcore import DelayedCore
from os.path import expanduser


class Login(Base):
    def __init__(self, master, controller):
        #init Base
        Base.__init__(self, master, controller)

        # Values
        self.controller = controller
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.secret = tk.StringVar()
        self.code = tk.StringVar()
        self.platform = tk.StringVar()
        self.emulate = tk.StringVar()
        self.debug = tk.IntVar()
        self.data = []
        self._keepalive = None

        # Search for settings
        try:
            with open(constants.LOGIN_FILE, 'r') as f:
                self.data = json.load(f)

            if not isinstance(self.data, list):
                self.data = [self.data]

            self.username.set(self.data[0]['username'])
            self.password.set(self.data[0]['password'])
            self.secret.set(self.data[0]['secret'])
            self.code.set(self.data[0]['code'])
            self.platform.set(self.data[0]['platform'])
            self.emulate.set(self.data[0]['emulate'])
        except:
            self.platform.set('xbox')
            self.emulate.set('pc')

        mainframe = tk.Frame(self, bg='#1d93ab')
        mainframe.pack(expand=True)

        self.loginlbl = tk.Label(
            mainframe,
            text='\nWe need to collect your login information in order to connect to the FIFA servers.  This information will be saved on your computer for future use.',
            anchor='w', justify='left', wraplength=500,
            fg='#fff', bg='#1d93ab', font=('KnulBold', 16)
        )
        # self.loginlbl.grid(column=0, row=0)
        self.loginlbl.pack()
        loginfr = tk.Frame(mainframe)
        # loginfr.grid(column=0, row=1, sticky='ns')
        loginfr.pack()

        # init user input
        userlbl = tk.Label(loginfr, text='Email:', font=('KnulBold', 16, 'bold'))
        userlbl.grid(column=0, row=1, sticky='e', padx=5, pady=5)
        userbox = tk.Entry(loginfr, textvariable=self.username)
        userbox.bind('<KeyRelease>', self.search)
        userbox.grid(column=1, row=1, sticky='w', padx=5, pady=5)
        passlbl = tk.Label(loginfr, text='Password:', font=('KnulBold', 16, 'bold'))
        passlbl.grid(column=0, row=2, sticky='e', padx=5, pady=5)
        passbox = tk.Entry(loginfr, textvariable=self.password, show='*')
        passbox.grid(column=1, row=2, sticky='w', padx=5, pady=5)
        secretlbl = tk.Label(loginfr, text='Secret Question:', font=('KnulBold', 16, 'bold'))
        secretlbl.grid(column=0, row=3, sticky='e', padx=5, pady=5)
        secretbox = tk.Entry(loginfr, textvariable=self.secret, show='*')
        secretbox.grid(column=1, row=3, sticky='w', padx=5, pady=5)
        codelbl = tk.Label(loginfr, text='Access Code:', font=('KnulBold', 16, 'bold'))
        codelbl.grid(column=0, row=4, sticky='e', padx=5, pady=5)
        codebox = tk.Entry(loginfr, textvariable=self.code)
        codebox.grid(column=1, row=4, sticky='w', padx=5, pady=5)
        platformlbl = tk.Label(loginfr, text='Platform:', font=('KnulBold', 16, 'bold'))
        platformlbl.grid(column=0, row=5, sticky='e', padx=5, pady=5)
        platformsel = tk.OptionMenu(loginfr, self.platform, 'pc', 'xbox', 'xbox360', 'ps3', 'ps4')
        platformsel.grid(column=1, row=5, sticky='w', padx=5, pady=5)
        emulatelbl = tk.Label(loginfr, text='Emulate:', font=('KnulBold', 16, 'bold'))
        emulatelbl.grid(column=0, row=6, sticky='e', padx=5, pady=5)
        emulatesel = tk.OptionMenu(loginfr, self.emulate, 'pc', 'android', 'iOS')
        emulatesel.grid(column=1, row=6, sticky='w', padx=5, pady=5)
        # debugLbl = tk.Label(loginfr, text='Enable Debug:', font=('KnulBold', 16, 'bold'))
        # debugLbl.grid(column=0, row=7, sticky='e')
        # debugCheckbox = tk.Checkbutton(loginfr, variable=self.debug)
        # debugCheckbox.grid(column=1, row=7, sticky='w')
        loginbtn = tk.Button(loginfr, text='Login', command=self.login)
        loginbtn.grid(column=0, row=7, columnspan=2, padx=5, pady=5)

    def search(self, event=None):
        i = self.find(self.data, 'username', self.username.get())
        if i != -1:
            self.loginlbl.config(text='\nLoaded saved login info for %s' % (self.username.get()))
            self.password.set(self.data[i]['password'])
            self.secret.set(self.data[i]['secret'])
            self.code.set(self.data[i]['code'])
            self.platform.set(self.data[i]['platform'])
            self.emulate.set(self.data[i]['emulate'])

    def login(self, switchFrame=True):

        try:
            if self.username.get() and self.password.get() and self.secret.get() and self.platform.get() and self.emulate.get():
                # Show loading frame
                if switchFrame:
                    self.master.config(cursor='wait')
                    self.master.update()
                    self.controller.show_frame(Loading)

                    # Save settings
                    self.save_settings()

                # Convert emulate
                if self.emulate.get() == 'android':
                    emulate = 'and'
                elif self.emulate.get() == 'iOS':
                    emulate = 'ios'
                else:
                    emulate = None

                # Start API and update credits
                cookies_file = constants.SETTINGS_DIR + self.username.get().split('@')[0]+'.txt'
                self.controller.api = DelayedCore(self.username.get(), self.password.get(), self.secret.get(), self.platform.get(), self.code.get(), emulate, False, cookies_file)
                self.controller.status.set_credits(str(self.controller.api.credits))
                self.controller.user = self.username.get()
                self._keepalive = self.keepalive()

                if switchFrame:
                    self.controller.status.set_status('Successfully Logged In!')
                    self.master.config(cursor='')
                    self.master.update()
                    self.controller.show_frame(PlayerSearch)
            else:
                raise FutError('Invalid Login Information')

        except (FutError, RequestException) as e:
            self.controller.show_frame(Login)
            self.master.config(cursor='')
            self.loginlbl.config(text='\nError logging in: %s (%s)' % (e.reason, type(e).__name__))
            self.controller.status.set_status('Error logging in')

    def logout(self, switchFrame=True):
        if switchFrame:
            self.controller.show_frame(Login)
        else:
            if self.controller.api is not None:
                self.controller.api.logout()
                self.controller.api = None
                if self._keepalive is not None:
                    self.after_cancel(self._keepalive)
                    self._keepalive = None

    def save_settings(self, *args):
        try:
            login = {
                'username': self.username.get(),
                'password': self.password.get(),
                'secret': self.secret.get(),
                'code': self.code.get(),
                'platform': self.platform.get(),
                'emulate': self.emulate.get()
            }
            i = self.find(self.data, 'username', self.username.get())
            if i != -1:
                self.data[i] = login
            else:
                self.data.append(login)
            with open(constants.LOGIN_FILE, 'w') as f:
                json.dump(self.data, f)
        except:
            pass

    def find(self, lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    def keepalive(self):
        try:
            if self.controller.api is not None:
                self.controller.api.keepalive()
            self.after(480000, self.keepalive)
        except (FutError, RequestException):
            self.controller.show_frame(Login)

    def active(self):
        Base.active(self)
        self.logout(switchFrame=False)

from fut.exceptions import FutError
from requests.exceptions import RequestException
from frames.loading import Loading
from frames.playersearch import PlayerSearch
