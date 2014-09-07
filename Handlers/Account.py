from flask import make_response
from flask import render_template, request, url_for, redirect, session, flash
from db_schema.db_functions import *
import json
from flask import jsonify
import logging

def signup_account():
    data = request.json
    print data
    # retrieve information
    password = data.get('password')
    email = data.get('email')
    userid = addUserAccount('', '', email, '')
    mm={'error':None, 'status':'ok'}
    mm['next_url'] = '/profile'    
    if mm['error'] is not None:
        mm['status'] = 'error'    
    mm['userid'] = userid
    resp = make_response(jsonify(mm))
    resp.headers['Content-Type'] = "application/json"
    return resp

def update_account():
    data = request.json
    print data
    token = data.get('token')
    provider = 'braintree'
    userid = read_cookie()
    # retrieve information
    name = data.get('name').split()
    firstname = name[0]
    lastname = name[1]
    phone = data.get('tel')
    user = getUser(userid)
    email = user[2]
    userid = updateUserAccount(userid, firstname, lastname, email, phone)
    addPayment(userid, token, provider)
    mm={'error':None, 'status':'ok'}
    mm['next_url'] = '/add_contact'    
    if mm['error'] is not None:
        mm['status'] = 'error'    
    resp = make_response(jsonify(mm))
    resp.headers['Content-Type'] = "application/json"
    return resp
    
def update_contacts():
    data = request.json
    print data    
    emails = data.get('emails')
    userid = read_cookie()
    for e in emails:
        addFriendByEmail(userid, e)
    mm={'error':None, 'status':'ok'}
    mm['next_url'] = '/send_money'           
    resp = make_response(jsonify(mm))
    resp.headers['Content-Type'] = "application/json"
    return resp        
    
def read_cookie():
    return request.cookies.get('userid')