from flask import Flask
from flask import make_response
from flask import render_template, request, url_for, redirect, session, flash
from flask import jsonify
from  Utils.data.defs import twilio_auth, twilio_sid
import MySQLdb as mdb
import twilio.twiml
from werkzeug.contrib.cache import SimpleCache
from twilio.rest import TwilioRestClient
import re
from db_schema.db_functions import *
from Handlers.Account import signup_account, read_cookie, update_account, update_contacts


cache = SimpleCache()
CACHE_TIMEOUT = 3600


DB_USERNAME = 'sendwithfriends'
DB_PASSWORD = 'sendwithfriends'
DB_TABLE = 'sendwithfriends'


class cached(object):
    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.path)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.path, response, self.timeout)
            return response
        return decorator


def get_db():
    """ get database connection"""
    return mdb.connect('localhost', DB_USERNAME, DB_PASSWORD, DB_TABLE);


app = Flask(__name__)
app.secret_key = open('app_secret.txt').read().strip()


"""
user flow
signup --(post)--> signup --(redirect)-->
profile --(post)--> add_payment --(redirect)-->
add_contact --(post)--> add_contact --(redirect)-->
send_money --(post)--> send_money --(redirect)--> confirmation

sms
send sms to friends
process replys from friends
message sender with percentage completion
message sender when transactions completed
"""


@app.route("/", methods=['GET', 'POST'])
def hello():
    """Home page"""
    return render_template('signup.html')


@app.route("/web", methods=['GET'])
def web():
    """Home page"""
    return render_template('web.html')


@app.route("/signup", methods=['GET'])
def signup():
    """Signup page"""
    return render_template('signup.html')

@app.route("/signin", methods=['GET'])
def signin():
    """Signup page"""
    return render_template('signin.html')

@app.route("/signup", methods=['POST'])
# /signup?fullname=bob
def signup_post():
    """Handle signup submission"""
    return signup_account()


@app.route("/profile", methods=['GET'])
def profile():
    # request.args.get('user')
    """Show profile and prompt user to add payment method"""
    return render_template('profile.html')


@app.route("/profile", methods=['POST'])
def update_profile():
    return update_account()

@app.route("/add_payment", methods=['POST'])
def add_payment():
    """Handle adding new payment method"""
    return render_template('add_payment.html')


@app.route("/add_contact", methods=['GET'])
def add_contact():
    """Prompt user to add contact"""
    return render_template('add_contact.html')


@app.route("/add_contact", methods=['POST'])
def add_contact_post():
    """Add contact to db"""
    return  update_contacts()


@app.route("/send_money", methods=['GET'])
def send_money():
    """Show send money page"""
    userid = read_cookie()
    friends = getFriends(userid)
    return render_template('send_money.html', friends=friends)


@app.route("/send_money", methods=['POST'])
def send_money_post():
    """Handle send money submission from user"""
    userid = read_cookie()
    sender = getUser(userid)
    data = request.json
    print data
    print 'x'
    amount = data.get('amount')
    friend = data.get('friend')

    sender_number = userid
    recipient = int(friend)
    full_amt = int(amount)
    token = getPaymentTokenForUser(sender_number, 'braintree')
    # charge sender
    trans_id = startTransaction(full_amt, sender_number, recipient)
    numbers = getPhoneNumbersForTransaction(trans_id)
    for user, number, amt in numbers:
        # disburse payment to each receiver (assume braintree for now)
        recv_token = getPaymentTokenForUser(user, 'braintree')
        msg = create_message(trans_id, number, amt)
        # send_message(number, msg)
    mm={'error':None, 'status':'ok'}
    mm['next_url'] = '/confirmation'
    if mm['error'] is not None:
        mm['status'] = 'error'
    resp = make_response(jsonify(mm))
    resp.headers['Content-Type'] = "application/json"
    return resp


@app.route("/confirmation", methods=['GET'])
def confirmation():
    """Confirm reception of send money request"""
    return render_template('confirmation.html')


@app.route('/create_account.json', methods=['POST'])
def create_account_json():
    d = {'status': 'failed'}
    return jsonify(d)

#######
# SMS #
#######

@app.route("/sms", methods=['GET'])
def sms():
    """Show send money page"""
    # send_message('+14157125465', 'snapcash')
    return render_template('send_money.html')


@app.route("/hive", methods=['GET'])
def hive():
    print 'hive'
    return render_template('hive.html')


@app.route("/receive_sms", methods=['GET', 'POST'])
def receive_sms():
    """Respond to incoming calls with a simple text message.
        When an sms is received, this indicates that the intermediary
        is ready to forward the payment.
    """
    import logging
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None)
    # body = request.args.get('Body')
    logging.info(body)
    # app.logger.debug(body)
    # print body
    matches = re.search('\d+', body)
    reply_msg = 'Transaction Rejected.'
    if matches:
        reply_msg = "SCID: %s confirmed!" % matches.group(0)
        # do braintree transaction corresponding to SCID and middle person
    resp = twilio.twiml.Response()
    resp.message(reply_msg)
    return str(resp)


def create_message(trans_id, sender, amt):
    msg = 'SCID: %s, %s wants to send %s through you. Reply back w/ transaction id to allow.' % (trans_id, sender, amt)
    return msg


def send_message(to, body="Hello there!"):
    account_sid = twilio_sid
    auth_token = twilio_auth
    client = TwilioRestClient(account_sid, auth_token)
    message = client.messages.create(to='+1' + to, from_="+16264145990", body=body)


@app.route('/example.json')
def example_json():
    d = {}
    return jsonify(d)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
