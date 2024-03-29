from Handlers.BaseHandler import *
from Models.User.Account import *
from Utils.UserUtils import *
from Models.Money.Promo import PromoCode
from google.appengine.api import taskqueue
import hashlib
import logging
import json
import urlparse

class AccountHandler(BaseHandler):
    """ User sign up page """
    def get(self, action=None):
        if self.user_prefs: # if user is logged in, redirect to profile
            self.redirect("/")
        elif action=='signup':
            promo = self.request.get('code')
            if promo and PromoCode.valid_code(promo):
                self.params['promo'] = promo
            self.render('signup.html', **self.params)
        elif action=='signin':
            self.render('signin.html')
        elif action=='signout':
            self.__signout()

    """ User Sign Out Page """
    def __signout(self):
        logging.info('Log out')
        self.logout() # deletes cookie
        self.redirect('/')

    def post(self, action=None):
        if action=='signup':
            self.__signup()
        elif action=='signin':
            self.__signup(False)
        elif action=='web':
            self.__web()

    def __signup(self, newacct=True):
        self.response.headers['Content-Type'] = "application/json"
        data = json.loads(self.request.body)
        logging.info(data)
        # retrieve information
        password = data.get('password')
        email = data.get('email')
        promo = data.get('promo')
        mm={'error':None}
        mm['next_url'] = '/m/profile'
        if not valid_email(email):
            mm['error']="That's not a valid email address."
        else:
            mm['email'] = email
        u = UserAccounts.by_email(email)
        if u:
            # already have account, sign them in
            self.__signin(u,password)
            return
        # if not valid_pw(password):
        #     mm['error'] = "That wasn't a valid password."
        if not newacct:
            mm['error']="Not an existing user."
        else:
            u = UserAccounts(email = email, pwhash = make_pw_hash(email, password))
            u.put()
            # create related data structures
            if promo:
                p = PromoCode.valid_code(promo)
                u.init(p)
            else:
                u.init()
            # return mobile login cookies
            mm['status'] = 'new'
            logging.info(u.user_id())
            self.login(u.user_id())
            self.set_current_user()
        if mm['error'] is not None:
            mm['status'] = 'error'
        self.write(json.dumps(mm))
        return

    def send_user_info(self, email):
        htmlbody =  self.render_str('email/welcome_user.html', **self.params)
        textbody = welcome_user
        send_info(email, welcome_user_sub, textbody, htmlbody)


    def __signin(self,u,password):
        mm = {}
        if valid_pwhash(u.email, password, u.pwhash):
            self.login(u.user_id())
            self.set_current_user()
            mm['status'] = 'ok'
            logging.info('login')
            logging.info(u)
            # check to see where the user left off in account process
            if not u.addr_deliv:
                mm['next_url'] = '/m/profile'
            elif not u.cardimg:
                mm['next_url'] = '/m/photoid'
            else:
                mm['next_url'] = '/m/catalog'
        else:
            mm['status'] = 'error'
            mm['error'] = "Invalid Login."
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(mm))

    def __web(self):
        self.response.headers['Content-Type'] = "application/json"
        data = json.loads(self.request.body)
        logging.info(data)
        # retrieve information
        location = data.get('location')
        email = data.get('email')
        u = WebAccount(email=email, location=location)
        u.put()
        mm = {'status': 'ok'}
        self.write(json.dumps(mm))
