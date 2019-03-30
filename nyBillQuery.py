#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: AEM
    Python Version: 2.7
    Description:
        Command line tool to perform a search on the NY state and NY city legislative systems, to find lists of recent bills on a given topic. 
        Requires the user to have an API key - they can be generated here:
        NYS - https://legislation.nysenate.gov/
        NYC - https://council.nyc.gov/legislation/api/
'''
# Module imports-----------------------
import requests
import datetime
import argparse

# Argument parsing -----------------------

example1 = "\n ->python nyBillQuery.py -ck (my NYC key) -sk (my NYS key) -f csv"
example2 = "\n ->python nyBillQuery.py -ck (my NYC key) -sk (my NYS key) -it A10165 T2018-1413 "
example3 = "\n ->python nyBillQuery.py -ck (my NYC key) -sk (my NYS key) -kt 'evil robots' 'a real mad-max style scenario' 'free coffee at the office' -it A10165 T2018-1413 "

parser = argparse.ArgumentParser(description='Command line tool to perform a search on the NY state and NY city legislative systems, to find lists of recent bills on a given topic.'+example1+example2+example3,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-ck", "--cityKey",    type=str, help= "API key for searching NYC database",required=True)
parser.add_argument("-sk", "--stateKey",   type=str, help= "API key for searching the NYS database",required=True)
parser.add_argument("-f", "--format",      type=str, help= "Output format, human-friendly text or csv (note: csv output will replace ',' in bills with '/' to improve cross-application use", choices=["txt","csv"], default="txt")
parser.add_argument("-it","--ignoreText",  type=str, help= "a list of bills to ignore (if omitted, a pre-made list of bills unrelated to tech are used)",nargs='+')
#parser.add_argument("-if","--ignoreFile",  type=str, help= "TBD") If we allow a user to provide a file, it could make this easier to automate / share
parser.add_argument("-kt","--keywordText", type=str, help= "a list of keywords to search on (if omitted, a pre-made list of tech keywords are used)",nargs='+')
#parser.add_argument("-kf","--keywordFile", type=str, help= "TBD")
parser.add_argument("-v", "--verbosity", help="increase output verbosity",action="store_true")
args = parser.parse_args()

# Global variables -----------------------
keywords = ["software", "data", "algorithm","blockchain", "block-chain", "block chain", "cryptography", "camera", "web", "wifi", "broadband", "internet","computer","cyber","tech","technology"]
if args.keywordText:
        keywords = args.keywordText
ignore = ['A10165','T2018-1413','T2017-5911','0988-2018','T2017-5912','T2017-5976','T2017-6070','T2018-1901','T2018-1904','T2018-1413','T2018-1414','T2017-5603','T2017-5602','T2019-3797','T2019-3799','T2017-6079']
if args.ignoreText:
        ignore = args.ignoreText

# Search functions -----------------------
def searchCity(search): 
    resp = requests.get('https://webapi.legistar.com/v1/nyc/matters?token='+args.cityKey+'&$filter=substringof(\''+search+'\', MatterTitle) eq true and  MatterAgendaDate+ge+datetime%272018-01-01%27+and+MatterAgendaDate+lt+datetime%272019-12-01%27')
    return resp
def searchState(search,year):
    stateParams = {'key': args.stateKey}
    resp = requests.get('https://legislation.nysenate.gov/api/3/bills/'+year+'/search?term='+search,params=stateParams)
    return resp

# text formatting for readability -----------------------
def addBillToListCity(data,billList):
    for l in data.json():
        if args.format == "csv":
            billList.append( (l['MatterFile']+','+l['MatterTitle'].replace("\r","").replace(",","/") ) )
        else:
            billList.append( (l['MatterFile']+' - '+l['MatterTitle'].replace("\r","") ) )
    return billList
def addBillToListState(data,billList):
    for l in data.json()['result']['items']:
        if args.format == "csv":
            
            billList.append(l['result']['basePrintNo'] + "," + (l['result']['title'].replace(",","/")) )
        else:
            billList.append(l['result']['basePrintNo'] + " - " + l['result']['title'])
    return billList

# Output bills, removing duplicates & ignored bills -----------------------
def printBills(billList):
    billList.sort()
    prevBill = ''
    for b in billList:
        bill = b.replace(","," ")
        bill = bill.split()[0]
        if bill == "Res" or bill == "Int":
            bill = b.split()[1]
        if (bill != prevBill) and (bill not in ignore):
            print b.encode('utf-8')
        prevBill = bill

# top level function to conduct overall search -----------------------
def runSearch():
    if args.verbosity:
        print "Performing search, this might take some time"
        print('--------------------')
    b_city = []
    b_state = []
    if args.verbosity:
        print("performed search on NY state bills between 2018-2019 on following keywords:"),
    for k in keywords:
        if args.verbosity:
            print (k+','),
        resp = searchCity(k)
        b_city = addBillToListCity(resp,b_city) 
        resp = searchState(k,'2018') 
        b_state = addBillToListState(resp,b_state)   
        resp = searchState(k,'2019') 
        b_state = addBillToListState(resp,b_state) 
    if args.verbosity:
        print ""  
        print('--------------------')
        if len(ignore)>= 1:
            print("the following bills have been ignored from the results above:")
        for i in ignore:
            print(i+" ")
    print('--------------------')
    print("Matching results from NY state:\n\n")
    printBills(b_state)
    print('--------------------')
    print("Matching results from NYC\n\n")
    printBills(b_city)

if __name__ == "__main__":
    runSearch()