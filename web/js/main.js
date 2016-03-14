
/**
 * @typedef {{pipe: number}}
 */
var StepParams;

/**
 * @typedef {{name: string, params: StepParams}}
 */
var Step;

/**
 * @typedef {Array<!Step>}
 */
var Scenario;


/**
 * @param {Error} error
 * @param {Scenario} scenario
 */
function initScenario(error, scenario) {
  
}

/**
 * Application bootstrap.
 */
function main() {
  d3.json('/api/get_conf', initScenario);
}
