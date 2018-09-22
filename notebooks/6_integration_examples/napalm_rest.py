from flask import Flask, jsonify
from nornir import InitNornir
from nornir.plugins.tasks.networking import napalm_get

app = Flask(__name__)


def get_nr():
    return InitNornir(
        inventory={
            "options": {
                "host_file": "inventory/hosts.yaml",
                "group_file": "inventory/groups.yaml",
                "defaults_file": "inventory/defaults.yaml",
            }
        }
    )


def to_json(results):
    return jsonify({host: result[0].result for host, result in results.items()})


@app.route("/get_users")
def get_users():
    nr = get_nr()
    r = nr.run(task=napalm_get, getters=["users"])
    return to_json(r)


@app.route("/get_facts")
def get_facts():
    nr = get_nr()
    r = nr.run(task=napalm_get, getters=["facts"])
    return to_json(r)
