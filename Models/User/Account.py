from google.appengine.ext import ndb
from Models.User.Cart import Cart
from Models.Money.Promo import PromoCode
import logging
import json

class UserAccounts(ndb.Model):
    valid = ndb.BooleanProperty(default=False)
    email = ndb.StringProperty()
    pwhash = ndb.StringProperty() # hashed pw
    tel = ndb.StringProperty()
    addr_deliv = ndb.KeyProperty() # default address for deliveries
    addr_bill = ndb.KeyProperty() # default address for billing - might not need this
    cust_id = ndb.StringProperty() # customer payment ID
    cc = ndb.StringProperty()
    fullname = ndb.StringProperty()
    last_active = ndb.DateTimeProperty(auto_now=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

    def init(self, promo=None):
        # create cart on acct creation
        c = Cart(parent=self.key)
        if promo:
            c.populate(code=promo.key, promo=promo.amount)
            # give credit to referrer
            if promo.user:
                UserCredit(referral=self.key, parent=promo.user, amount=promo.amount).put()
        c.put()
        PromoCode(user=self.key, code=str(self.key.id())[-4:], amount=10.00).put()
        # UserStats(parent=self.key, refcode=str(self.key.id())[-4:]).put()
        return


    @classmethod
    def by_email(cls, email):
        u = cls.query(cls.email == email).get()
        return u

    @classmethod
    def by_userid(cls, userid):
        return cls.get_by_id(int(userid))

    @classmethod
    def by_code(cls, code):
        u = UserStats.query(UserStats.refcode == code).get()
        if u:
            return u.key.parent()

    def user_id(self):
        return self.key.id()

    def to_dict(self, addr=False):
        p = { 'email' : self.email }

        if self.fullname:
            p['name'] = self.fullname
        if self.tel:
            p['tel'] = self.tel
        if addr and self.addr_deliv:
            a = self.addr_deliv.get()
            p['addr'] = a.to_dict()
        return p

    def cardimg_link(self):
        r = '/imgdown/%s' % (self.cardimg)
        return r

    def code(self):
        return str(self.key.id())[-4:]

    def cart_total(self):
        c = Cart.query(ancestor=self.key).get()
        if c:
            return c.item_count()
        else:
            return 0


class WebAccount(ndb.Model):
    email = ndb.StringProperty()
    location = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
