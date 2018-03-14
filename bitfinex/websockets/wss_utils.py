"""Module for websocket utilities"""
import datetime

def UtcNow():
    now = datetime.datetime.utcnow()
    return int(float(now.strftime("%s.%f"))*10000000)

def order_pair(pair):
    pair = 't' + pair if not pair.startswith('t') else pair
    return pair

ERROR_CODES = {
    10000:	"Unknown error",
    10001:	"Generic error",
    10008:	"Concurrency error",
    10020:	"Request parameters error",
    10050:	"Configuration setup failed",
    10100:	"Failed authentication",
    10111:	"Error in authentication request payload",
    10112:	"Error in authentication request signature",
    10113:	"Error in authentication request encryption",
    10114:	"Error in authentication request nonce",
    10200:	"Error in un-authentication request",
    10300:	"Failed channel subscription",
    10301:	"Failed channel subscription: already subscribed",
    10400:	"Failed channel un-subscription: channel not found",
    11000:	"Not ready, try again later",
    20051:	"Websocket server stopping... please reconnect later",
    20060:	"Websocket server resyncing... please reconnect later",
    20061:	"Websocket server resync complete. please reconnect",
    5000:	"Info message",
}

# Abbreviation Glossary
# https://bitfinex.readme.io/v2/docs/abbreviations-glossary#section-abbreviation-glossary
NOTIFICATION_CODES = {
    "bu":	"balance update",
    "ps":	"position snapshot",
    "pn":	"new position",
    "pu":	"position update",
    "pc":	"position close",
    "ws":	"wallet snapshot",
    "wu":	"wallet update",
    "os":	"order snapshot",
    "on":	"order new",
    "ou":	"order update",
    "oc":	"order cancel",
    "ox_multi": "order multi-op",
    "oc-req":	"order cancel request",
    "oc_multi-req":	"multiple orders cancel request",
    "te":	"trade executed",
    "tu":	"trade execution update",
    "fte":	"funding trade execution",
    "ftu":	"funding trade update",
    "hos":	"historical order snapshot",
    "mis":	"margin information snapshot",
    "miu":	"margin information update",
    "n":	"notification",
    "fos":	"funding offer snapshot",
    "fon":	"funding offer new",
    "fou":	"funding offer update",
    "foc":	"funding offer cancel",
    "hfos":	"historical funding offer snapshot",
    "fcs":	"funding credits snapshot",
    "fcn":	"funding credits new",
    "fcu":	"funding credits update",
    "fcc":	"funding credits close",
    "hfcs":	"historical funding credits snapshot",
    "fls":	"funding loan snapshot",
    "fln":	"funding loan new",
    "flu":	"funding loan update",
    "flc":	"funding loan close",
    "hfls":	"historical funding loan snapshot",
    "hfts":	"historical funding trade snapshot",
    "uac":	"user custom price alert",
}

def get_notification_code(description):
    index = list(NOTIFICATION_CODES.values()).index(description)
    return list(NOTIFICATION_CODES.keys())[index]

ORDER_TYPES = [
    "MARKET",
    "EXCHANGE MARKET",
    "LIMIT",
    "EXCHANGE LIMIT",
    "STOP",
    "EXCHANGE STOP",
    "TRAILING STOP",
    "EXCHANGE TRAILING STOP",
    "FOK",
    "EXCHANGE FOK",
    "STOP LIMIT",
    "EXCHANGE STOP LIMIT",
]
