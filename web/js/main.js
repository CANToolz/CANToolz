
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
 * @param {!Scenario} scenario
 */
function initControls(scenario) {
  d3.select('.loop-action').on('click', function() {
    if (scenario.running) {
      scenario.running = false;
      d3.json('/api/stop', nop);
    } else {
      scenario.running = true;
      d3.json('/api/start', nop);
    }

    redrawHeader(scenario);
  });

  d3.select('.scenario').on('click', function() {
    var target = d3.select(d3.event.target);
    if (target.classed('step')) {
      scenario.current = target.datum();

      redrawCircuit(scenario);

      stepModule(scenario.current, function(module) {
        redrawMenu(scenario.current.name, module);
        redrawOptions(scenario, scenario.current)
      });
    }
  });

  d3.select('.controls').on('click', function() {
    var target = d3.select(d3.event.target);
    if (target.classed('command-run')) {
      var module = target.attr('module');
      var command = target.attr('command')
      var args = d3.select('.controls input[command="' + command + '"]')
          .node().value;

      d3.json('/api/cmd/' + module).post(JSON.stringify({
        'cmd': command + ' ' + args
      }), function(error, result) {
        if (result !== undefined) {
          d3.select('.output').insert('pre', ':first-child').text(result.response);
        } else {
          console.error(error);
        }        
      });
    }
  })
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

      form.append('span')
          .classed('command-name', true)
          .classed('input-group-addon', true);

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

  commands.select('.command-name').text(commandName);
  commands.select('.help-block').text(function(r) { return r.value.descr; });
  commands.select('input')
      .classed('hide', function (r) { return r.value.param_count === 0; })
      .attr('command', commandName)
      .attr('placeholder', function(r) { return r.value.descr_param; });

  commands.select('.command-run')
      .attr('command', commandName)
      .attr('module', name)
}

/**
 * @param {!Scenario} scenario
 */
function redrawHeader(scenario) {
  d3.select('.loop-action')
      .classed('btn-success', !scenario.running)
      .classed('btn-danger', scenario.running)
}

/**
 * @param {!Scenario} scenario
 * @param {!Step} step
 */
function redrawOptions(scenario, step) {
  var fields = d3.select('.options tbody')
      .selectAll('tr')
      .data(d3.entries(step.params));

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

  fields.select('input').attr('value', function(record) {
    return record.value;
  });

  fields.selectAll('button').attr('param', function(record) {
    return record.key;
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
      .style('left', function(step) { return (step.params.pipe - 1) * width + '%' })
      .style('width', width + '%')
      .style('height', STEP_HEIGHT_UNIT + 'px');

  circuit
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

    redrawHeader(scenario);
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
}
