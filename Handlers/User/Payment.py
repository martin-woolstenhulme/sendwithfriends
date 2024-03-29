from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Utils.data.defs import *
from Utils.XML2dict import *
import datetime
import logging
import json
import stripe
import xml
import urllib2

"""
    Payment process: Store card, get token. Store token in user account.
        If it's a MC, use MC API. Otherwise, paypal.
    Charge card when sending money
"""

class PaymentHandler(BaseHandler):
    """ Create addresses """
    def get(self, action=None):
        if not self.user_prefs: # if user is not logged in, redirect
            self.redirect("/signup")
        if action=='cc':
            self.__cc()
        elif action=='checkout':
            self.__checkout()

    def post(self, action=None):
        if action=='cc':
            self.__createcc()
        elif action=='checkout':
            self.__charge()
        elif action=='createmc':
            self.__mc()
            
    def __mc(self):
        req = urllib2.Request(url=mastercard_url, 
                     data=card_xml, 
                     headers={'Content-Type': 'application/xml'})
        urllib2.urlopen(req)
        # get mapping id
        root = ElementTree.XML(req)
        xmldict = XmlDictConfig(root)
        mapping_id = xmldict.get('MappingId')
        # store in user profile

    def __cc(self):
        if self.user_prefs.cc:
            self.params['cc'] = self.user_prefs.cc
            self.params['has_cc'] = True
        else:
            self.params['has_cc'] = False
        self.render('payment.html', **self.params)

    def __createcc(self):
        stripe.api_key = stripe_key
        self.response.headers['Content-Type'] = "application/json"
        data = json.loads(self.request.body)
        logging.info(data)

        u = self.user_prefs

        # Get the credit card details submitted by the form
        token = data.get('stripeToken')
        cc = data.get('cc')
        userid = u.user_id()

        # Create a Customer
        customer = stripe.Customer.create(
            card=token,
            description=userid,
            email=u.email
        )

        #save id to user account
        u.cust_id = customer.id
        u.cc = cc
        u.put()
        mm = {'status':'ok'}
        self.write(json.dumps(mm))
        return

    def __charge(self):
        stripe.api_key = stripe_key
        self.response.headers['Content-Type'] = "application/json"
        data = json.loads(self.request.body)
        logging.info(data)

        u = self.user_prefs

        instr = data.get('instr')
        total = data.get('total')

        charge = int(100*float(total))
        # Charge the Customer instead of the card
        stripe.Charge.create(
            amount=charge, # in cents
            currency="usd",
            customer=u.cust_id
        )
        #record transaction
        cart = Cart.by_key(self.user_prefs.key)
        t = Transaction(customer = u.key, cart = cart.key, amount = float(total))
        t.put()

        #notify self
        notify_order(t)

        mm = {'status':'ok'}
        mm['next_url'] = '/deliv/' + t.key.urlsafe()
        self.write(json.dumps(mm))
        return

    def __checkout(self):
        cart = Cart.by_key(self.user_prefs.key)
        self.params['total'] = '%.2f' % cart.total()
        self.params['customer'] = self.user_prefs.to_dict(True)
        self.params['cc'] = self.user_prefs.cc
        now = datetime.datetime.now().time()
        if now < open_biz or now > close_biz:
            self.params['after_hours'] = True
        self.render('checkout.html', **self.params)

def notify_order(trans):
    subject = 'Lemmiwink Order Notification'
    msg = str(trans.to_dict())
    send_alert(msg,subject)
