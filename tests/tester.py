#!/usr/bin/env python3
import os




def add_tags(function, tags):
    if tags:
        for tag in tags:
            if tag != None and tag != "":
                print(f"'{tag}' = '{tags[tag]}'")
                #Tags.of(function).add(tag, tags[tag], apply_to_launched_instances = True, priority = 300)




servicenow_tags = { "Project": "Palautteet / ServiceNow", "toinen": "arvo", "": "c" }

add_tags(None, servicenow_tags)