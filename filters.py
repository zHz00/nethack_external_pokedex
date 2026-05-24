from nhconstants_atk import *
from nhconstants_common import *
from nhconstants_flags import *
import json
import utils

groups_titles=[]
groups_filters=dict()

def load_filters(variant):
    global groups_titles
    global groups_filters
    f=open("filters.json",encoding="utf-8")
    try:
        filters_all=json.load(f)
    except Exception as e:
        print("Error loading filters.json! Message:\n"+str(e))
        input()
        return
    groups_titles=[]
    groups_filters=dict()
    for g in filters_all:
        groups_titles.append(g["group_title"])
        groups_filters[g["group_title"]]=[]
        for f in g["filters_list"]:
            variants=f["variants"]
            good=False
            if len(variants[0])==0:#all include
                good=True
            else:
                exclude_mode=False
                for v in variants:
                    if v[0]=="!":
                        exclude_mode=True#if some elements have ! and other don't have, then this is an error in filters.json. now it is not checked
                if exclude_mode==False:#include mode
                    if variant in variants:
                        good=True
                if exclude_mode==True:
                    if "!"+variant not in variants:
                        good=True
            if good:
                groups_filters[g["group_title"]].append(f)
    #print(filters_all)

def make_group_filter(name,idx):
    field=dict()
    field["name"]="group"
    field["name_short"]="group"
    field["variant"]=[""]
    field["type"]="include"
    field["field"]="group"
    field["value"]=0
    f=dict()
    f["name"]=name
    f["short_name"]="<none>" if idx==-1 else groups_filters[idx]["short_name"]
    f["index"]=idx
    f["type"]="group"#not real filter, only index
    f["fields"]=[field]
    return f

def make_letter_filter(fname,letter):
    field=dict()
    field["name"]="Letter"
    field["name_short"]="Letter"
    field["variant"]=[""]
    field["type"]="include"
    field["field"]="symbol"
    field["value"]=letter
    f=dict()
    f["name"]=fname
    if len(letter)>0 and letter!="*":
        f["short_name"]=f"('{letter}')"
    else:
        f["short_name"]="<any>"
    f["type"]="check_fields"
    f["fields"]=[field]
    return f

def make_name_filter(fname,name):
    field=dict()
    field["name"]="Name"
    field["name_short"]="Name"
    field["variant"]=[""]
    field["type"]="include"
    field["field"]="name"
    field["value"]=name
    f=dict()
    f["name"]=fname
    if len(name)>0:
        f["short_name"]=f"*{name[:9]}*"
    else:
        f["short_name"]="<any>"
    f["type"]="check_fields"
    f["fields"]=[field]
    return f

def make_conveyed_filter(fname,res):
    field=dict()
    field["name"]="Conveyed"
    field["name_short"]="Conv"
    field["variant"]=[""]
    field["type"]="include"
    field["field"]="prob"
    field["value"]=res
    f=dict()
    f["name"]=fname
    if len(res)>0:
        f["short_name"]=resists_conv_short[list(resists_conv.keys()).index(res)]
    else:
        f["short_name"]="<any>"
    f["type"]="check_fields"
    f["fields"]=[field]
    return f

def make_param_filter(fname,param,min,max):
    field=dict()
    field["name"]="Parameter"
    field["name_short"]="Param"
    field["variant"]=[""]
    field["type"]="include"
    field["field"]=param
    field["min"]=min
    field["max"]=max
    f=dict()
    f["name"]=fname
    if len(param)>0:
        f["short_name"]=filter_mode_param_short_str[list(param_mode_list.keys()).index(param)]
    else:
        f["short_name"]="<any>"
    f["type"]="check_fields"
    f["fields"]=[field]
    return f

def test_monster_one_field(mon,field):
    f=field["field"]
    test=None
    if "value" in field:
        #checking for exact value
        if f=="symbol":
            test=(monsym[mon[rows[f]]]==field["value"] or field["value"]=="*" or field["value"]=="")
        if f=="name":
            test=(mon[rows[f]].lower().find(field["value"].lower())!=-1 or field["value"]=="*")
        if f=="prob" or f=="conv_special":
            ress_with_prob=mon[rows[f]].split("|")
            ress_names=[]
            for r in ress_with_prob:
                ress_names.append(r.split("=")[0])
            test=(field["value"] in ress_names or len(field["value"])==0 or field["value"] in mon[rows["flags1"]])
        if f=="eat_danger":
            dangers=mon[rows[f]].split("|")
            dangers_names=[]
            for d in dangers:
                dangers_names.append(d.split("=")[0])
            test=(field["value"] in dangers_names)
        if f=="attack":
            attacks_fields=["attack1","attack2","attack3","attack4","attack5","attack6","attack7","attack8","attack9","attack10"]
            test=False
            for a in attacks_fields:
                if mon[rows[a]].find(field["value"])!=-1:
                    test=True
                    break
        if f=="flag":
            flags_fields=["flags1","flags2","flags3","flags4"]
            test=False
            for f in flags_fields:
                if mon[rows[f]].find(field["value"])!=-1:
                    test=True
                    break
        if f=="geno":
            test=False
            if mon[rows["geno"]].find(field["value"])!=-1:
                test=True
    if "min" in field:
        #param test
        if len(f)==0:#empty parameter
            test=True
        else:
            if len(mon[rows[f]])==0:#empty value, this is not dNetHack, but we are testing insight or something similar
                test=False
            else:
                test_value=None
                try:
                    test_value=int(mon[rows[f]])
                except:
                    pass#we'll get exception later if not special cases will be applied
                if f=="geno":#freq
                    test_value=int((mon[rows["geno"]].split("|"))[-1])
                if f=="size":
                    test_value=szs_order[mon[rows[f]]]
                min=int(field["min"])
                max=int(field["max"])
                test=(test_value>=min and test_value<=max)
                
    return test
def test_monster_one_filter(mon,f):
    if "index" in f:#group filter
        if f["index"]==-1:#not selected
            return True
        if test_monster_one_filter(mon,groups_filters[f["name"]][f["index"]])==True:
            return True
    if f["type"]=="monsters_list":
        m_list=f["monsters"]
        for m in m_list:
            if len(m)==1:#monster class
                if monsym[mon[rows["symbol"]]]==m and int((mon[rows["geno"]].split("|"))[-1])!=0:#not randomly generated monsters are excluded
                    return True
            else:
                names=m.split("|")
                if mon[rows["name"]] in names:
                    return True
        return False
    if mon[rows["name"]=="mumak"]:
        f=""
    if f["type"]=="check_fields":#if more than one field present, fields are ORed       
        include_field_present=False
        for field in f["fields"]:
            if field["type"]=="include":
                include_field_present=True
            if test_monster_one_field(mon,field)==True and field["type"]=="exclude":
                return False
            if test_monster_one_field(mon,field)==True:
                return True
        if include_field_present==False:#exclude did'nt work => include
            return True
    return False

def test_monster_one_filter_hl(mon,f):
    if "index" in f:#group filter
        if f["index"]==-1:#not selected
            return False
        if test_monster_one_filter_hl(mon,groups_filters[f["name"]][f["index"]])==True:
            return True
    if f["type"]!="monsters_list":
        return False
    m_list=f["highlight"]
    for m in m_list:
        names=m.split("|")
        if mon[rows["name"]] in names:
            return True
    return False

def check_monster_list(monlist,f):
    absent=[]
    if f["type"]!="monsters_list":
        raise
    m_list=f["monsters"]
    for m in m_list:
        if len(m)>1:#real monster
            names=m.split("|")
            found=False
            for name in names:
                if name in monlist:
                    found=True
            if found==False:
                absent.append(m)
    return absent

def test_monster(mon,filters):
    for f in filters:
        if test_monster_one_filter(mon,f)==False:#several filters are ANDed
            return False
    return True

def test_monster_hl(mon,filters):
    for f in filters:
        if test_monster_one_filter_hl(mon,f)==True:#highlight can be only one, but other filters can be in the list, so several filters are ORed
            return True
    return False
