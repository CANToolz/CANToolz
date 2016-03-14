
/**
 * @typedef {{pipe: number}}
 */
var StepParams;

/**
 * @typedef {{name: string, params: StepParams}}
 */
var Step;

/**
 * @typedef {{ queue: Array<!Step> }}
 */
var Scenario;


/**
 * @param {Error} error
 * @param {Scenario} scenario
 */
function initScenario(error, scenario) {
  if (scenario !== null) {
    var queue = scenario.queue;

    var pipeScale = d3.scale.linear()
        .domain(d3.extent(queue, function(step) { return step.params.pipe; }))
        .range([0, 128]);

    var stepScale = d3.scale.linear()
        .domain([0, queue.length])
        .range([0, 720]);
    
    var circuit = d3.select('.application')
        .selectAll('.step')
        .data(queue);

    circuit.enter()
        .append('div')
        .classed('step', true)
        .text(function (s) { return s.name })
        .style('top', function(s, i) { return stepScale(i) + 'px' })
        .style('left', function(s) { return pipeScale(s.params.pipe) + 'px' })
        


  } else {
    console.error(error);
  }
}

/**
 * Application bootstrap.
 */
function main() {
  d3.json('/api/get_conf', initScenario);
}
