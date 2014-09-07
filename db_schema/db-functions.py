#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys


def connect_db():
    con = mdb.connect('localhost', 'root', '', 'snapcash');

    cur = con.cursor()
    return con

def close_db(db):
    db.close()
    return


#
#
def addFriendByEmail(user_id, friend_email):
    db = connect_db()

    cur = db.cursor()
#    cur.execute('SELECT id FROM UserAccount WHERE email="%s"', "abcom")
    cur.execute('SELECT id FROM UserAccount WHERE email = "%s"' % friend_email)
    friend_id = cur.fetchone()[0]

    cur.execute("INSERT INTO Friend VALUES (default, %s, %s)",
                (str(user_id), str(friend_id)))
    cur.execute("INSERT INTO Friend VALUES (default, %s, %s)",
                            (str(friend_id), str(user_id)))
    
    db.commit()
    close_db(db)


#
#
def addFriendByPhone(user_id, friend_phone):
    db = connect_db()
    
    cur = db.cursor()
    #cur.execute('SELECT id FROM UserAccount WHERE phone_number="%s"',(friend_phone))
    cur.execute('SELECT id FROM UserAccount WHERE phone_number="%s"' % friend_phone)
    
    friend_id = cur.fetchone()[0]
    
    cur.execute("INSERT INTO Friend VALUES (default, %s, %s)",
                (str(user_id), str(friend_id)))
    cur.execute("INSERT INTO Friend VALUES (default, %s, %s)",
                (str(friend_id), str(user_id)))

                
    db.commit()
    close_db(db)


#
# Adds payment info for a user
def addPayment(user_id, token, provider):
    db = connect_db()

    cur = db.cursor()
    cur.execute("INSERT INTO PaymentInfo values (default, %s, %s)",
                (token, provider))
    
    cur.execute("SELECT id FROM PaymentInfo WHERE token = %s AND provider = %s",
                (token, provider))
                
    paymentInfoId = cur.fetchone()[0]
    
    cur.execute("INSERT INTO UserPaymentInfo values (default, %s, %s)",
                (str(user_id), str(paymentInfoId)))

    db.commit()
    
    close_db(db)


#
# Adds UserAccount
def addUserAccount(first_name, last_name, email, phone_number):
    db = connect_db()

    cur = db.cursor()
    cur.execute("INSERT INTO UserAccount VALUES (default, %s, %s, %s, %s)",
            (first_name, last_name, email, phone_number))

    cur.execute("SELECT * FROM UserAccount \
                         WHERE first_name = %s \
                         AND last_name = %s \
                         AND email = %s \
                         AND phone_number = %s",
                         (first_name, last_name, email, phone_number))

    userID = cur.fetchone()[0]

    db.commit()
    close_db(db)

    return userID


#
# Creates a transaction and spreads the dollar amount among the sender's friends
# returns the transactionID
def startTransaction(amount, sending_id, receiving_id):
    db = connect_db()
    cur = db.cursor()
    
    cur.execute("INSERT INTO Transaction VALUES (default, %s, %s, %s, NOW())",
                (str(amount), str(sending_id), str(receiving_id)))

    transactionID = cur.lastrowid
    
    cur.execute("SELECT UserAccount_id FROM UserPaymentInfo \
                WHERE id = %s",
                (str(sending_id)))
        
    userID = cur.fetchone()[0]
    
    # select all the payment accounts of friends
    cur.execute("SELECT UserPaymentInfo.id FROM Friend \
                LEFT JOIN UserPaymentInfo ON Friend.friend_id = UserPaymentInfo.UserAccount_id \
                WHERE Friend.user_id = %s \
                AND UserPaymentInfo.id IS NOT NULL",
                (str(userID)))
    
    friendsPaymentInfoIDs = cur.fetchall()
    
    numAccounts = len(friendsPaymentInfoIDs)
    sharedAmount = amount / numAccounts
    
    for friendPaymentID in friendsPaymentInfoIDs:
        cur.execute("INSERT INTO TransactionAgent VALUES (default, %s, %s, %s)",
                   (str(friendPaymentID[0]), str(transactionID), str(sharedAmount)))
    

    db.commit()
    close_db(db)

    return transactionID


#
#
def getPhoneNumbersForTransaction(transactionID):
    db = connect_db()
    cur = db.cursor()

    cur.execute("SELECT phone_number FROM TransactionAgent \
                LEFT JOIN UserPaymentInfo ON ")

    db.commit()
    close_db(db)
    
    return phoneNumbers


#
# Get all the friends for the specified user_id
def getFriends(user_id):
    db = connect_db()
    
    cur = db.cursor()
    cur.execute("SELECT UserAccount.id, first_name, last_name, email, phone_number \
                          FROM Friend \
                          LEFT JOIN UserAccount ON UserAccount.id = Friend.friend_id \
                          WHERE user_id = %s ",
                (str(user_id)))
    
    friends = cur.fetchall()

    close_db(db);

    return friends


## Poor man's unit tests

#addFriendByPhone(7, "7175729454")

#print addUserAccount("John", "Doe", "john.doe@gmail.com", "1234567890")

#addPayment(1, "abcdef", "Chase")
#addPayment(2, "abcdef", "Chase")
#addPayment(3, "abcdef", "Chase")
#addPayment(4, "abcdef", "Chase")
#addPayment(5, "abcdef", "Chase")

#startTransaction(100000, 3, 4)

#friends = getFriends(2)

#for friend in friends:
#    print friend
