class LambdaProperties:

    def __init__(self, vpc = None, securitygroups = None, timeout: int = None, memory: int = None, environment: dict = None, tags: dict = None):
        self.vpc = vpc
        self.subnets = None
        self.memory = memory
        self.environment = environment
        self.tags = tags


def add_tags(function, tags):
    if tags:
        for k in tags:
            v = tags[k]
            print(f"tag '{k}' = '{v}'")
            #Tags.of(function).add(k, v, apply_to_launched_instances = True, priority = 300)



l = LambdaProperties(tags = {
    "eka": "arvo",
    "toinen": "joo"
})


add_tags(None, l.tags)