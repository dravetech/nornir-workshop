import logging

import ruamel.yaml

from nornir import InitNornir

from nornir.plugins.tasks.networking import napalm_configure, napalm_get
from nornir.plugins.tasks.text import template_file

from nornir.plugins.functions.text import print_result


nr = InitNornir(
    num_workers=1,
    inventory={
        "options": {
            "host_file": "inventory/hosts.yaml",
            "group_file": "inventory/groups.yaml",
            "defaults_file": "inventory/defaults.yaml",
        }
    },
)


def manage_users(task, desired_users):
    state_users = task.run(
        task=napalm_get, getters=["users"], severity_level=logging.DEBUG
    )

    users_to_remove = []
    for user in state_users.result["users"]:
        if user not in desired_users:
            users_to_remove.append(user)

    users_config = task.run(
        task=template_file,
        path=f"templates/{task.host.platform}",
        template="users.j2",
        desired_users=desired_users,
        remove_users=users_to_remove,
        severity_level=logging.DEBUG,
    )

    task.run(task=napalm_configure, configuration=users_config.result)


yaml = ruamel.yaml.YAML()
with open("data/users.yaml", "r") as f:
    desired_users = yaml.load(f.read())

spines = nr.filter(role="spine")
r = spines.run(task=manage_users, desired_users=desired_users)

print_result(r)
