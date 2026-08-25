import os
import re
from collections import defaultdict

from flask import Flask, render_template
from kubernetes import client, config

app = Flask(__name__)

LABEL_SELECTOR = "demo.redhat.com/userinfo"
SECTIONS = []


def load_configmaps():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    namespace = os.environ.get("NAMESPACE", "rhdp-userinfo")
    cms = v1.list_namespaced_config_map(namespace, label_selector=LABEL_SELECTOR)

    sections = []
    for cm in cms.items:
        data = cm.data or {}
        section = {
            "name": cm.metadata.name,
            "order": int(data["order"]) if "order" in data else None,
            "demo_title": data.get("demo_title", cm.metadata.name),
            "demo_url": data.get("demo_url"),
            "access_instructions": data.get("access_instructions"),
            "fields": [],
        }

        field_nums = set()
        for key in data:
            m = re.match(r"label_(\d+)$", key)
            if m:
                field_nums.add(int(m.group(1)))

        for n in sorted(field_nums):
            field = {
                "label": data.get(f"label_{n}", ""),
                "content": data.get(f"content_{n}", ""),
                "content_url": data.get(f"content_url_{n}"),
            }
            section["fields"].append(field)

        sections.append(section)

    ordered = sorted([s for s in sections if s["order"] is not None], key=lambda s: s["order"])
    unordered = sorted([s for s in sections if s["order"] is None], key=lambda s: s["name"])
    return ordered + unordered


def init_app():
    global SECTIONS
    SECTIONS = load_configmaps()


@app.route("/")
def index():
    return render_template("index.html", sections=SECTIONS)


@app.route("/healthz")
def healthz():
    return "ok"


init_app()
