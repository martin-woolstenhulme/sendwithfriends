import braintree
import logging

braintree_merch_id = '77whpz52p35z2png'
braintree_publickey = 'g69vfjnykrkytt34'
braintree_privatekey = '5aaefa2a6ec71a6efbec4c756d60501a'
braintree_cse_key = 'MIIBCgKCAQEAs1ia5JR0bYc8iFpfCwBherqzbrLmnvj8LhLp5e8xce24IcoHTs2fknst+yRouEacafhoHLbGVxsm/ORCRsZRwB9NTikZtX1VWbqO8phqvCCD51zPP/5ZROq7Ux9AMvEirq4OwBSDJK69C7YZCg00kfW1Gt4sEThtH9Z6HotrRzCkbLk6d7PME7IGaKd3ZQJ2naWQC85OP3+BrJ+rb1P0dnKpO5Oc48CGaYLbPKKvoT2vEeDEmqS/f0QcrThf359dwvhE7caksza8p2sjLvnjc//Ca8WvmnRoplJaLJyzkP/YXB5TB5qRn+2g/gt8W+b8enkXiKCja4UfAtRBrRmLGwIDAQAB'

def init_braintree():
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        '77whpz52p35z2png',
        'g69vfjnykrkytt34',
        '5aaefa2a6ec71a6efbec4c756d60501a'
    )
    
def create_customer(firstname, lastname, cc, expmonth, expyear, cvv):
    result = braintree.Customer.create({
        "first_name": firstname,
        "last_name": lastname,
        "credit_card": {
            "number": cc,
            "expiration_month": expmonth,
            "expiration_year": expyear }
    })
    if result.is_success:
        return result.customer.id, result.customer.credit_cards[0].token
    else:
        return result.message