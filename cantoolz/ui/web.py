import json
import traceback
import collections

from flask import Flask, request, render_template, Response


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
    response = {'queue': [{'name': name, "params": params} for name, _, params in app.can_engine.actions]}
    return Response(json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@app.route('/api/help/<path:module>')
def help(module):
    try:
        help_list = app.can_engine.actions[app.can_engine.find_module(module)][1].commands
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': 'An unexpected error occured. Please consult the server logs.'}), status=500, mimetype='application/json')
    response_help = collections.OrderedDict()
    for key, cmd in help_list.items():
        response_help[key] = {'descr': cmd.description, 'descr_param': cmd.desc_params, 'param_count': cmd.num_params}
    return Response(json.dumps(response_help, ensure_ascii=False), status=200, mimetype='application/json')


@app.route('/api/start')
def start():
    try:
        status = app.can_engine.start_loop()
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': 'An unexpected error occured. Please consult the server logs.'}), status=500, mimetype='application/json')
    return Response(json.dumps({'status': status}), status=200, mimetype='application/json')


@app.route('/api/stop')
def stop():
    try:
        status = app.can_engine.stop_loop()
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': 'An unexpected error occured. Please consult the server logs.'}), status=500, mimetype='application/json')
    return Response(json.dumps({'status': status}), status=200, mimetype='application/json')


@app.route('/api/status')
def status():
    status = app.can_engine.status_loop
    progress = {}
    for name, module, params in app.can_engine.actions:
        btns = {}
        for key, cmd in module.commands.items():
            btns[key] = cmd.is_enabled
        sts = module.get_status_bar()
        progress[name] = {'bar': sts['bar'], 'text': sts['text'], 'status': module.is_active, 'buttons': btns}
    return Response(json.dumps({"status": status, "progress": progress}), status=200, mimetype='application/json')


@app.route('/api/edit/<int:id>', methods=['POST'])
def edit(id):
    paramz = request.get_json(silent=True)
    if paramz is None:
        return Response(json.dumps({'error': 'Invalid JSON configuration'}), status=400, mimetype='application/json')
    try:
        ret = app.can_engine.edit_module(id, paramz)
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': 'An unexpected error occured. Please consult the server logs.'}), status=500, mimetype='application/json')
    if ret:
        active = app.can_engine.actions[id][1].is_active
        if active:
            app.can_engine.actions[id][1].do_activate(0, 0)
        if app.can_engine.status_loop:
            # Restart the module if possible.
            app.can_engine.actions[id][1].do_stop(paramz)
            app.can_engine.actions[id][1].do_start(paramz)
        if active:
            app.can_engine.actions[id][1].do_activate(0, 1)
        new_paramz = app.can_engine.actions[id][2]
        return Response(json.dumps(new_paramz, ensure_ascii=False), status=200, mimetype='application/json')
    return Response(json.dumps({'error': "Module id {} could not be found".format(id)}), status=404, mimetype='application/json')


@app.route('/api/cmd/<path:module>', methods=['POST'])
def cmd(module):
    paramz = request.get_json(silent=True)
    if paramz is None:
        return Response(json.dumps({'error': 'Invalid JSON configuration'}), status=400, mimetype='application/json')
    if 'cmd' not in paramz:
        return Response(json.dumps({'error': 'Missing JSON cmd parameter'}), status=400, mimetype='application/json')
    try:
        text = app.can_engine.call_module(app.can_engine.find_module(module), str(paramz['cmd']))
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': 'An unexpected error occured. Please consult the server logs.'}), status=500, mimetype='application/json')
    return Response(json.dumps({'response': str(text)}), status=200, mimetype='application/json')
