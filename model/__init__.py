#!/usr/bin/env python
"""
Project: Nimbus Web Simple Shopping Web App
File: Model Module Index
Author: Ben Knisley [benknisley@gmail.com]
Date: Mar/26/2016
This file holds and controls all functions and objects related to the model.
    Meaning it holds functions that deal with the database and any output actions.
    For example it holds the functions getProductByID(), sessionExist(), etc.
    This file should be writen so that the database backend can be switch quickly.
"""
## Import sqlite
import sqlite3, random, time, json, stripe

## Make path to database global
#! Do best to remove hardcode
SQL_FILE = "./model/database.db"

## Import product class
import product

### PRODUCT FUNCTIONS ###

def productExist(ID): ## Read Only
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Setup query
    query = "SELECT EXISTS(SELECT 1 FROM products WHERE ID='%s');" % (ID)
    ## Send query to database
    sql.execute(query)

    ## Extract and return data
    if sql.fetchone()[0] == 1:
        return True
    else:
        return False

def getAllProducts():
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Setup query
    query = "SELECT * FROM products;"
    ## Send query to database
    sql.execute(query)

    ## Get data from query
    entrys = sql.fetchall()

    ## Create return list
    retn = list()

    ## For each entry create product from data
    for data in entrys:
        retn.append( product.product(data[0], data[1], data[2], data[3], data[4]) )

    ## Return ste of products
    return retn

def getProductsWTag(tag):
    ## Call getAllProducts to get all products
    allProducts = getAllProducts()

    ## Create new list for tagged products
    taggedProducts = list()

    ## For each product if tag is in product.tags, add to taggedProducts
    for product in allProducts:
        if tag in product.tags:
            taggedProducts.append(product)

    ## Return taggedProducts
    return taggedProducts

def getProductsBySearch(query):
        ## Break down query into words
        queryList = query.split()

        ## Call getAllProducts to get all products
        allProducts = getAllProducts()

        ## Create list of results
        results = list()

        ## For each product
        for product in allProducts:
            ## For each word in queryList
            for word in queryList:
                ## If word is contained in name, add to results
                if (word in product.name):
                    results.append(product)
                ## If word is contained in description, add to results
                if (word in product.description):
                    results.append(product)
                ## If word is contained in tags, add to results
                if (word in product.tags):
                    results.append(product)

        ## Remove duplicates from results
        results = list(set(results))

        ## return results
        return results

def getProductByID(ID): ## Read only
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Setup query
    query = "SELECT * FROM products WHERE ID='%s';" % (ID)
    ## Send query to database
    sql.execute(query)

    ## Get data from query
    data = sql.fetchone()

    ## Create product from data
    retnProduct = product.product(data[0], data[1], data[2], data[3], data[4])

    ## Return product
    return retnProduct

### VISITOR FUNCTIONS ###

def visitor_exist(ID):
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Setup query
    query = "SELECT EXISTS(SELECT 1 FROM visitors WHERE ID='%s');" % (ID)
    ## Send query to database
    sql.execute(query)

    ## Extract and return data
    if sql.fetchone()[0] == 1:
        return True
    else:
        return False

def newVisitor(ipAddr):
    ## Generate new visitorID

    ## Create pool of chars and numbers to select from, abd lenght of ID
    IDLen = 56
    chars = 'abcdefghijklmnopqrstuvwxyz'
    digits = '0123456789'

    ## Get one random char, can't be digit

    ## Create rest of string
    randStr = ''.join(random.choice(chars + digits) for _ in range(IDLen - 7))
    visitorID = 'visitor:' + randStr

    ## Get timestamp
    timestamp = str( int( time.time() ) )


    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Setup query
    query = "INSERT INTO visitors VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (visitorID, timestamp, timestamp, ipAddr, '[]', "[]")
    ## Send query to database
    sql.execute(query)

    ## Add changes to database
    conn.commit()

    return visitorID

def pageVisit(ID, pageTitle):
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Get current pageVisits
    query = "SELECT PAGEVISITS FROM visitors WHERE ID='%s';" % (ID)
    sql.execute(query)
    data = sql.fetchone()

    ## Load JSON from data
    pages = json.loads(data[0])

    ## Only if page title is not the same as last page
    if (len(pages) == 0) or (pages[len(pages) - 1] != pageTitle):
        ## Add new page to JSON
        pages.append(pageTitle)

    ## Convert python to JSON string
    jsonString = json.dumps(pages)

    ## get timestamp
    timestamp = str( int( time.time() ) )

    ## Update database
    query = "UPDATE visitors SET LASTTIME = '%s', PAGEVISITS = '%s' WHERE ID = '%s';" % (timestamp, jsonString, ID)
    ## Send query to database
    sql.execute(query)

    ## Add changes to database
    conn.commit()

### CART FUNCTIONS ###

def addToCart(ID, productID):
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Get current pageVisits
    query = "SELECT CART FROM visitors WHERE ID='%s';" % (ID)
    sql.execute(query)
    data = sql.fetchone()

    ## Load JSON from data
    cart = json.loads(data[0])

    ## Add productID to cart list
    cart.append(productID)

    ## Convert python to JSON string
    jsonString = json.dumps(cart)

    ## get timestamp
    timestamp = str( int( time.time() ) )

    ## Update database
    query = "UPDATE visitors SET LASTTIME = '%s', CART = '%s' WHERE ID = '%s';" % (timestamp, jsonString, ID)
    ## Send query to database
    sql.execute(query)

    ## Add changes to database
    conn.commit()

def cartCount(ID):
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Get current pageVisits
    query = "SELECT CART FROM visitors WHERE ID='%s';" % (ID)
    sql.execute(query)
    data = sql.fetchone()

    ## Load JSON from data
    cart = json.loads(data[0])

    ## Return the size of cartCount
    return len(cart)

def getProductsInCart(ID):
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Get current pageVisits
    query = "SELECT CART FROM visitors WHERE ID='%s';" % (ID)
    sql.execute(query)
    data = sql.fetchone()

    ## Load JSON from data
    productIDs = json.loads(data[0])

    ## Create list to hold products objects
    productList = list()

    ## Convert ID to products and add to productList
    for newID in productIDs:
        productList.append( getProductByID(newID) )

    ## Return products
    return productList

def clearCart(ID):
    ## Create database connection and cursor
    conn = sqlite3.connect(SQL_FILE)
    sql = conn.cursor()

    ## Update database
    query = "UPDATE visitors SET CART = '%s' WHERE ID = '%s';" % ('[]', ID)
    ## Send query to database
    sql.execute(query)

    ## Add changes to database
    conn.commit()

## CREDIT CARD FUNCTIONS ##

def luhnChecksumPass(card_number):
    """
    """

    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])

        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit

    return ( (sum % 10) == 0 )

def processCard(ID, number, month, year, cvv):
    '''
    '''

    ## Get Items in cart
    products = getProductsInCart(ID)

    ## Calulate price
    subtotal = 0
    for product in products:
        subtotal += product.price
    tax = int(0.07 * subtotal)
    total = subtotal + tax

    ## Get Stripe Key
    stripe.api_key = open('./stripekey.txt', 'r').read().rstrip()

    ## Try Card charge
    try:
        chargeData = stripe.Charge.create(
            amount=total,
            currency="usd",
            source={"number": number, "exp_month": month, "exp_year": year, "cvc": cvv}, description="Stripe Test 1"
        )
    except stripe.error.CardError as e:
        return False

    return True


## ORDER FUNCTIONS ##

def addOrder(*args):
    None






## Fin
