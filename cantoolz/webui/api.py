import json
import collections
import traceback

from flask import Flask, request, render_template


app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/vircar.html')
def vircar():
    return render_template('vircar.html')


@app.route('/api/get_conf')
def get_conf():
    response = {"queue": []}
    modz = app.can_engine.get_modules_list()
    try:
        for name, module, params in modz:
            response['queue'].append({'name': name, "params": params})
        return json.dumps(response, ensure_ascii=False)
    except Exception as e:
        traceback.print_exc()
        resp_code = 500
        return "{ \"error\": " + json.dumps(str(e)) + "}"


@app.route('/api/help/<path:module>')
def help(module):
    try:
        help_list = app.can_engine.get_modules_list()[app.can_engine.find_module(module)][1]._cmdList
        response_help = collections.OrderedDict()
        for key, cmd in help_list.items():
            response_help[key] = {'descr': cmd.description, 'descr_param': cmd.desc_params, 'param_count': cmd.num_params}
        return json.dumps(response_help, ensure_ascii=False)
    except Exception as e:
        traceback.print_exc()
        resp_code = 500
        return "{ \"error\": " + json.dumps(str(e)) + "}"


@app.route('/api/start')
def start():
    try:
        modz = app.can_engine.start_loop()
        return json.dumps({"status": modz})
    except Exception as e:
        traceback.print_exc()
        resp_code = 500
        return "{ \"error\": " + json.dumps(str(e)) + "}"


@app.route('/api/stop')
def stop():
    try:
        modz = app.can_engine.stop_loop()
        return json.dumps({"status": modz})
    except Exception as e:
        traceback.print_exc()
        resp_code = 500
        return "{ \"error\": " + json.dumps(str(e)) + "}"


@app.route('/api/status')
def status():
    try:
        modz = app.can_engine.status_loop
        modz2 = app.can_engine.get_modules_list()
        modz3 = {}
        for name, module, params in modz2:
            btns = {}
            for key, cmd in module._cmdList.items():
                btns[key] = cmd.is_enabled
            sts = module.get_status_bar()
            modz3[name] = {
                "bar": sts['bar'], "text": sts['text'], "status": module.is_active, "buttons": btns}
        return json.dumps({"status": modz, "progress": modz3})
    except Exception as e:
        traceback.print_exc()
        resp_code = 500
        return "{ \"error\": " + json.dumps(str(e)) + "}"


@app.route('/api/edit/<int:id>', methods=['POST'])
def edit(id):
    try:
        paramz = request.get_json()
        if app.can_engine.edit_module(id, paramz) >= 0:
            print(id)
            mode = 1 if app.can_engine.get_modules_list()[id][1].is_active else 0
            print(mode)
            if mode == 1:
                app.can_engine.get_modules_list()[id][1].do_activate(0, 0)
            if not app.can_engine._stop.is_set():
                app.can_engine.get_modules_list()[id][1].do_stop(paramz)
                app.can_engine.get_modules_list()[id][1].do_start(paramz)
            if mode == 1:
                app.can_engine.get_modules_list()[id][1].do_activate(0, 1)

            new_params = app.can_engine.get_module_params(id)
            resp_code = 200
            return json.dumps(new_params, ensure_ascii=False)
        else:
            resp_code = 404
            return "{ \"error\": \"module not found!\"}"
    except Exception as e:
        traceback.print_exc()
        resp_code = 500
        return "{ \"error\": " + json.dumps(str(e)) + "}"


@app.route('/api/cmd/<path:module>', methods=['POST'])
def cmd(module):
    try:
        paramz = request.get_json().get("cmd")
        text = app.can_engine.call_module(app.can_engine.find_module(module), str(paramz))
        resp_code = 200
        return json.dumps({"response": str(text)})
    except Exception as e:
        traceback.print_exc()
        resp_code = 500
        return "{ \"error\": " + json.dumps(str(e)) + "}"
