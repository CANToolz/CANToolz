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
    response = {"queue": []}
    modz = app.can_engine.actions
    try:
        for name, module, params in modz:
            response['queue'].append({'name': name, "params": params})
        return Response(json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': traceback.format_exc()}), status=400, mimetype='application/json')


@app.route('/api/help/<path:module>')
def help(module):
    try:
        help_list = app.can_engine.actions[app.can_engine.find_module(module)][1].commands
        response_help = collections.OrderedDict()
        for key, cmd in help_list.items():
            response_help[key] = {'descr': cmd.description, 'descr_param': cmd.desc_params, 'param_count': cmd.num_params}
        return Response(json.dumps(response_help, ensure_ascii=False), status=200, mimetype='application/json')
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': traceback.format_exc()}), status=400, mimetype='application/json')


@app.route('/api/start')
def start():
    try:
        modz = app.can_engine.start_loop()
        return Response(json.dumps({"status": modz}), status=200, mimetype='application/json')
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': traceback.format_exc()}), status=400, mimetype='application/json')


@app.route('/api/stop')
def stop():
    try:
        modz = app.can_engine.stop_loop()
        return Response(json.dumps({"status": modz}), status=200, mimetype='application/json')
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': traceback.format_exc()}), status=400, mimetype='application/json')


@app.route('/api/status')
def status():
    try:
        modz = app.can_engine.status_loop
        modz2 = app.can_engine.actions
        modz3 = {}
        for name, module, params in modz2:
            btns = {}
            for key, cmd in module.commands.items():
                btns[key] = cmd.is_enabled
            sts = module.get_status_bar()
            modz3[name] = {
                "bar": sts['bar'], "text": sts['text'], "status": module.is_active, "buttons": btns}
        return Response(json.dumps({"status": modz, "progress": modz3}), status=200, mimetype='application/json')
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': traceback.format_exc()}), status=400, mimetype='application/json')


@app.route('/api/edit/<int:id>', methods=['POST'])
def edit(id):
    try:
        paramz = request.get_json()
        if app.can_engine.edit_module(id, paramz) >= 0:
            mode = 1 if app.can_engine.actions[id][1].is_active else 0
            if mode == 1:
                app.can_engine.actions[id][1].do_activate(0, 0)
            if not app.can_engine._stop.is_set():
                app.can_engine.actions[id][1].do_stop(paramz)
                app.can_engine.actions[id][1].do_start(paramz)
            if mode == 1:
                app.can_engine.actions[id][1].do_activate(0, 1)

            new_params = app.can_engine.actions[id][2]
            return Response(json.dumps(new_params, ensure_ascii=False), status=200, mimetype='application/json')
        else:
            return Response(json.dumps({'error': 'module not found'}), status=404, mimetype='application/json')
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': traceback.format_exc()}), status=400, mimetype='application/json')


@app.route('/api/cmd/<path:module>', methods=['POST'])
def cmd(module):
    try:
        paramz = request.get_json().get("cmd")
        text = app.can_engine.call_module(app.can_engine.find_module(module), str(paramz))
        return Response(json.dumps({'response': str(text)}), status=200, mimetype='application/json')
    except Exception:
        traceback.print_exc()
        return Response(json.dumps({'error': traceback.format_exc()}), status=400, mimetype='application/json')
