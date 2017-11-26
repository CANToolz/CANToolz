/**
 * @typedef {{pipe: number}}
 */
var StepParams;

/**
 * @typedef {{name: string, params: StepParams}}
 */
var Step;

/**
 * @typedef {{queue: Array<!Step>, current: ?Step, running: boolean}}
 */
var Scenario;

/**
 * @typedef {{param_count: number, descr_param: string, descr: string }}
 */
var Command;

/**
 * @typedef {Object<string, Command>}
 */
var Module;

/**
 * @const {number}
 */
var STEP_HEIGHT_UNIT = 64;

/**
 * @type {!Object<string, !Module>}
 */
var moduleCache = {};

/**
 * No Operation Performed
 */
function nop() {}

/**
 * @param {!Step} step
 * @param {function(!Module)} callback
 */
function stepModule(step, callback) {
  var module = moduleCache[step.name];
  if (module === undefined) {
    d3.json('/api/help/' + step.name, function(error, module) {
      if (module !== undefined) {
        callback(moduleCache[step.name] = module);
      } else {
        console.error(error);
      }
    });
  } else {
    callback(module);
  }
}

/**
 * @param {Scenario} scenario
 */
function redrawStatus(status) {
  if (status !== undefined && status != null) {
    d3.select('.loop-action')
      .classed('btn-success', !status.status)
      .classed('btn-danger', status.status)

    currentName = d3.select('.step.well.current');
    if (currentName[0][0]!=null){
      name = currentName[0][0].__data__.name;
      bar = status.progress[name].bar;
      btns = status.progress[name].buttons;
      redrawProgressBar(bar);
      redrawButtons(btns)
    }

    for (data in status.progress){
      err_text = status.progress[data]['text'];
      if (err_text!="")
      {
        //New notification
        d3.select('.output').insert('pre', ':first-child').text(err_text);
      }
    }
  }

  return status.status;
}

function redrawButtons(buttons){

    d3.selectAll('.command-run')  //here's how you get all the nodes
    .each(function(d) {
      if (buttons[d.key] == true){
        d3.select(this).classed("disabled", false);
      }else{
        d3.select(this).classed("disabled", true);
      }
    });

}

/**
 * @param {Status} current status
 */
function changeStatus(status) {
  if (status !== undefined) {
    if (!status.status){
        d3.json('/api/start', nop);
    }else{
        d3.json('/api/stop', nop);
    }
  }

  redrawHeader();

}

/**
 * @param {!Scenario} scenario
 */
function redrawHeader() {
  d3.json('/api/status', redrawStatus);
}

/**
 * @param {!Scenario} scenario
 */
function initControls(scenario) {
  redrawHeader();
  d3.select('.loop-action').on('click', function() {
    d3.json('/api/status', changeStatus);

 });

  d3.select('.scenario').on('click', function() {
    var target = d3.select(d3.event.target);
    if (target.classed('step')) {
      scenario.current = target.datum();

      redrawCircuit(scenario);
      redrawOptions(scenario.current, scenario.queue.indexOf(scenario.current));

      stepModule(scenario.current, function(module) {
        redrawMenu(scenario.current.name, module);
      });
    }
  });

  d3.select('.controls').on('click', function() {
    var target = d3.select(d3.event.target);
    if (target.classed('command-run')) {
      var module = target.attr('module');
      var command = target.attr('command');
      var args = d3.select('.controls input[command="' + command + '"]')
          .node().value;

      d3.json('/api/cmd/' + module).header("Content-Type","application/json").post(JSON.stringify({
        'cmd': command + ' ' + args
      }), function(error, result) {
        if (result !== undefined) {
          d3.select('.output').insert('pre', ':first-child').text(result.response);
        } else {
          console.error(error);
        }
      });
    }
  });


  d3.select('.options').on('click', function() {
    var target = d3.select(d3.event.target);
    var index = target.attr('step');
    var step = scenario.queue[index];

    function handleResult(error, result) {
      if (result !== undefined) {
        redrawCircuit(scenario);
        redrawOptions(scenario.queue[index], index);
      } else {
        console.error(error);
      }
    }

    if (step && target.classed('btn-danger')) {
      delete step.params[target.attr('param')];
    }

    if (step && target.classed('btn-primary')) {
      var param = target.attr('param');
      var input = d3.select('.options input[param="' + param + '"]');
      var type = input.attr('format');
      var value = input.node().value;

      switch (type) {
        case 'object': step.params[param] = JSON.parse((value.replace(/:\s*(0x[0-9a-f]+)/ig, function(match, code) {
                return ": " + parseInt(code,16);
        }))); break;
        case 'string': step.params[param] = value; break;
        case 'number': step.params[param] = Number(value); break;
      }
    }

    if (step && target.classed('btn-success')) {
      var newParam = d3.select('.options .new-param').node().value;
      var newValue = d3.select('.options .new-value').node().value;
      var newType = d3.select('.options select').node().value;

      switch (newType) {
        case 'json': step.params[newParam] = JSON.parse((newValue.replace(/:\s*(0x[0-9a-f]+)/ig, function(match, code) {
                return ": " + parseInt(code,16);
        }))); break;
        case 'str': step.params[newParam] = newValue; break;
        case 'num': step.params[newParam] = Number(newValue); break;
      }
    }

    if (step) {
      d3.json('/api/edit/' + index).header("Content-Type","application/json")
          .post(JSON.stringify(step.params), handleResult);
    }
  });
}


/**
 * @param {string} name
 * @param {!Module} module
 */
function redrawMenu(name, module) {
  /**
   * @param {{key: string, value: Command}} record
   * @returns {string}
   */
  function commandName(record) {
    return record.key;
  }

  var commands = d3.select('.controls')
      .selectAll('.command')
      .data(d3.entries(module));

  var enter = commands.enter().append('div')
      .classed('command', true)
      .classed('row', true);

    var form = enter.append('div')
        .classed('input-group', true);

      form.append('input')
          .attr('type', 'text')
          .classed('form-control', true);

      form.append('span')
          .text('Run!')
          .classed('command-run', true)
          .classed('btn', true)
          .classed('input-group-addon', true);

    enter.append('span')
        .classed('help-block', true);

  commands.exit().remove();

  commands.select('.command-run').text(function(r) { return r.value.descr; });
  commands.select('input')
      .classed('hide', function (r) { return r.value.param_count === 0; })
      .attr('command', commandName)
      .attr('placeholder', function(r) { return r.value.descr_param; })
      .each(function(record) {
        this.value = ""
      });;

  commands.select('.command-run')
      .attr('command', commandName)
      .attr('module', name)
}

/**
 * @param {!Precent} percent
 * @param {number} index
 */
function redrawProgressBar(percent) {

 progressBar = d3.select('.progress-bar.progress-bar-info.progress-bar-striped');
 progressBar.attr('aria-valuenow',percent);
 progressBar.attr('style','width:'+percent+'%');
 progressBar.text(percent+'%');

}

/**
 * @param {!Step} step
 * @param {number} index
 */
function redrawOptions(step, index) {
  /**
   * @param {{key: string, value: *}} record
   * @returns {string}
   */
  function paramName(record) {
    return record.key;
  }

  /**
   * @param {{key: string, value: *}} record
   * @returns {string}
   */
  function paramFormat(record) {
    return typeof record.value;
  }

  /**
   * @param {{key: string, value: *}} record
   * @returns {string}
   */
  function paramValue(record) {
    if (typeof record.value === 'object') {
      return JSON.stringify(record.value);
    }

    return record.value;
  }

  var fields = d3.select('.options tbody')
      .selectAll('tr')
      .data(d3.entries(step.params));

  d3.select('.options .btn-success')
      .attr('step', index);

  d3.select('.options')
      .classed('hide', false);

  var enter = fields.enter().append('tr');

    enter.append('td')
        .append('p')
        .classed('form-control-static', true);

    enter.append('td')
        .append('input')
        .classed('form-control', true);

    enter.append('td')
        .append('button')
        .classed('btn btn-primary', true)
        .text('\u2714');

    enter.append('td')
        .append('button')
        .classed('btn btn-danger', true)
        .text('\u00D7');

  fields.exit().remove();

  fields.select('.btn-danger').attr('param', paramName).attr('step', index);
  fields.select('.btn-primary').attr('param', paramName).attr('step', index);
  fields.select('input')
      .attr('param', paramName)
      .attr('format', paramFormat)
      .each(function(record) {
        this.value = paramValue(record)
      });

  fields.select('p').text(function(record) {
    return record.key;
  });
}

/**
 * @param {!Scenario} scenario
 */
function redrawCircuit(scenario) {
  var circuit = d3.select('.scenario')
      .selectAll('.step')
      .data(scenario.queue);

  var width = 100 / d3.max(scenario.queue, function(step) {
    return step.params.pipe
  });

  circuit
      .enter()
      .append('div')
      .classed('step', true)
      .classed('well', true)
      .text(function (step) { return step.name })
      .style('top', function(step, i) { return i * STEP_HEIGHT_UNIT + 'px' })
      .style('height', STEP_HEIGHT_UNIT + 'px');

  circuit
      .style('left', function(step) { return (step.params.pipe - 1) * width + '%' })
      .style('width', width + '%')
      .classed('current', function(step) { return step === scenario.current; });
}


/**
 * @param {Error} error
 * @param {Scenario} scenario
 */
function init(error, scenario) {
  if (scenario !== undefined) {
    scenario.current = null;
    scenario.running = false;

    initControls(scenario);
    redrawCircuit(scenario);
  } else {
    console.error(error);
  }
}

/**
 * Application bootstrap.
 */
function main() {
  d3.json('/api/get_conf', init);

  setInterval(redrawHeader, 1000);
}

