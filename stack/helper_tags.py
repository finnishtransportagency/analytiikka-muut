from aws_cdk import (
    Tags
)

"""
Lisää tagit
"""
def add_tags(item, tags):
    if tags:
        for tag in tags:
            if tag != None and tag != "":
                #print(f"'{tag}' = '{tags[tag]}'")
                Tags.of(item).add(tag, tags[tag], apply_to_launched_instances = True, priority = 300)

