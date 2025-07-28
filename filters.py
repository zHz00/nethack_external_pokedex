from nhconstants_atk import *
from nhconstants_common import *
from nhconstants_flags import *

def make_letter_filter(fname,letter):    
    field=dict()
    field["type"]="include"
    field["field"]="symbol"
    field["value"]=letter
    f=dict()
    f["name"]=fname
    if len(letter)>0:
        f["short_name"]=f"('{letter}')"
    else:
        f["short_name"]="<any>"
    f["fields"]=[field]
    return f

def make_name_filter(fname,name):
    field=dict()
    field["type"]="include"
    field["field"]="name"
    field["value"]=name
    f=dict()
    f["name"]=fname
    if len(name)>0:
        f["short_name"]=f"*{name}*"
    else:
        f["short_name"]="<any>"
    f["fields"]=[field]
    return f

def make_conveyed_filter(fname,res):
    field=dict()
    field["type"]="include"
    field["field"]="resconv"
    field["value"]=res
    f=dict()
    f["name"]=fname
    f["name_short"]="(res)"
    f["fields"]=[field]
    return f

def make_param_filter(fname,param,min,max):
    field=dict()
    field["type"]="include"
    field["field"]=param
    field["min"]=min
    field["max"]=max
    f=dict()
    f["name"]=fname
    f["name_short"]="(param)"
    f["fields"]=[field]
    return f

def test_monster_one_field(mon,field):
    f=field["field"]
    test=None
    if "value" in field:
        #checking for exact value
        if f=="symbol":
            test=(monsym[mon[rows[f]]]==field["value"] or field["value"]=="*")
        if f=="name":
            test=(mon[rows[f]].lower().find(field["value"].lower())!=-1 or field["value"]=="*")
    return test
def test_monster_one_filter(mon,f):
    for field in f["fields"]:
        if test_monster_one_field(mon,field)==False:
            return False

def test_monster(mon,filters):
    for f in filters:
        if test_monster_one_filter(mon,f)==False:
            return False
    return True
