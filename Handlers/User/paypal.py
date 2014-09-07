from paypalrestsdk import CreditCard, Payment
import logging

"""
    Payment process: 
        init_paypal()
        create_cc()
        create_payment()
        execute_payment()
"""


paypal_oauth = 'https://api.sandbox.paypal.com/v1/oauth2/token'

paypal_email = 'elaine.ou-facilitator@gmail.com'
paypal_endpoint = 'api.sandbox.paypal.com'
paypal_clientid = 'AfMOeRDCZiywxWHI6aT4gtkI5wMa1euyR8TWkMUsiLB8Kk1e6deHtBIixLOf'
paypal_secret = 'EFLt-hARfRnFzVh-e-T92C8NFauiJsU03hDyC2kp_zztnC7JUAYJ2DQ3HmK0'
## Paypal live credentials
# paypal_endpoint = 'api.paypal.com'
# paypal_clientid = 'Aavv8xDil5nG2sGtNR4DvW-gm3MgH1cACm9M8Y817t-V6UsQer9HPz_rvV9D'
# paypal_secret = 'EDuVDBBHUgvS-i3dhjmNQ15BhGz3BLUX_lNdLb8SxxoOzc0JvLBdco2Sw_tB'


def init_paypal():
    # req = urllib2.Request(paypal_oauth)
    # req.add_header("Content-Type", "application/json")
    # req.add_header("Authorization", "Bearer %s" % base64string) 
    paypalrestsdk.configure({
      "mode": "sandbox", # sandbox or live
      "client_id": "EBWKjlELKMYqRNQ6sYvFo64FtaRLRR5BdHEESmha49TM",
      "client_secret": "EO422dn3gQLgDbuwqTjzrFgFtaRLRR5BdHEESmha49TM" })
    
def create_cc(userid, type, cc, month, year, cvv, firstname, lastname):
    credit_card = CreditCard({
       # ###CreditCard
       # A resource representing a credit card that can be
       # used to fund a payment.
       "payer_id": userid, 
       "type": type,
       "number": cc,
       "expire_month": month,
       "expire_year": year,
       "cvv2": cvv,
       "first_name": firstname,
       "last_name": lastname})
       
    # Creates the credit card as a resource
    # in the PayPal vault.
    if credit_card.create():
        logging.info("CreditCard[%s] created successfully"%(credit_card.id))
        # TODO: Save id in user account
    else:
        logging.error("Error while creating CreditCard:")
        logging.error(credit_card.error)
      
def find_cc(ccid):
    # retrieve a previously saved
    # Credit Card using the 'vault' API.
    # API used: GET /v1/vault/credit-card/{id}
    try:
        # Retrieve the CreditCard  by calling the
        # static `find` method on the CreditCard class,
        # and pass CreditCard ID
        credit_card = CreditCard.find(ccid)
        return credit_card

    except ResourceNotFound as error:
        logging.error("CreditCard Not Found")
        
def create_payment(ccid, amount, userid):
    payment = Payment({
      "intent": "sale",
      # A resource representing a Payer that funds a payment
      # Use the List of `FundingInstrument` and the Payment Method
      # as 'credit_card'
      "payer": {
        "payment_method": "credit_card",

        # ###FundingInstrument
        # A resource representing a Payeer's funding instrument.
        # In this case, a Saved Credit Card can be passed to
        # charge the payment.
        "funding_instruments": [{
          # ###CreditCardToken
          # A resource representing a credit card that can be
          # used to fund a payment.
          "credit_card_token": {
            "credit_card_id": ccid }}]},

        # ###Transaction
        # A transaction defines the contract of a
        # payment - what is the payment for and who
        # is fulfilling it
        "transactions": [{

        # ### ItemList
        "item_list": {
          "items": [{
            "name": "snapcash",
            "sku": "item",
            "price": amount,
            "currency": "USD",
            "quantity": 1 }]},

        # ###Amount
        "amount": {
          "total": amount,
          "currency": "USD" },
        "description": "Snapcash transaction." }]})

    # Create Payment and return status
    if payment.create():
        logging.info("Payment[%s] created successfully"%(payment.id))
        # no reason to store this, just execute
        execute_payment(payment.id, userid)
    else:
        logging.error("Error while creating payment:")
        logging.error(payment.error)
        
def execute_payment(paymentid, userid):
    # ID of the payment. This ID is provided when creating payment.
    payment = Payment.find(paymentid)

    # PayerID is required to approve the payment.
    if payment.execute({"payer_id": userid}):  
      logging.info("Payment[%s] execute successfully"%(paymentid))
    else:
      logging.error(payment.error)