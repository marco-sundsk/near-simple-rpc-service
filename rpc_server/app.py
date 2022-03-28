#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Marco'

from flask import Flask
from flask import request, send_file
from rpc_provider import JsonProviderError,  JsonProvider
import gzip
from io import BytesIO
from base64 import b64encode, b64decode
import json
import logging


def fetch_state_at_height(height, contract_id, prefix):
    ret = None

    prefix_key = b''
    if prefix:
        prefix_key = b64encode(prefix)

    qurey_args = {
        "request_type": "view_state",
        "account_id": contract_id,
        "prefix_base64": prefix_key.decode(),
    }
    if height:
        qurey_args["block_id"] = int(height)
    else:
        qurey_args["finality"] = "final"

    flag = False

    try:
        conn = JsonProvider(("127.0.0.1", 3030))
        ret = conn.query(qurey_args)
        # print(ret)
        flag = True
    except JsonProviderError as e:
        print("RPC Error: ", e)
    except Exception as e:
        print("Error: ", e)

    if not flag:
        raise Exception("Error fetch state on %s" %
                        (contract_id, ))

    return ret


Welcome = 'Welcome to simple rpc server, version 20220328.01'
# 实例化，可视为固定格式
app = Flask(__name__)

@app.route('/')
def hello_world():
    return Welcome

@app.route('/get-contract-state', methods=['GET'])
def handle_get_contract_state():
    """
    get-contract-state
    """
    contract_id = request.args.get("contract_id", "N/A") 
    height = request.args.get("block_height", "") 
    state = fetch_state_at_height(height, contract_id, b'')
    if state:
        content = json.dumps(state, indent=2)
        f= BytesIO()
        with gzip.open(f, 'wb') as gf:
            gf.write(content.encode())
        f.seek(0)
        dl_name = "state_%s_%s.json.gz" % (contract_id, height)
        return send_file(f, attachment_filename=dl_name, as_attachment=True)
    else:
        return "Encounter Error"

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    app.logger.info(Welcome)
    app.run(host='0.0.0.0', port=28080, debug=False)
