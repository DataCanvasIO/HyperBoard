import {Steps, TWO_STAGE_SUFFIX} from "../constants";
import {getStepComponent} from "./steps";


export function prepareExperimentData(experimentData) {
    const retExperimentData = {...experimentData}; // must clone a copy to avoid modify origin data
    // exclude steps that does not support to visualize
    // const supportedSteps = steps.filter(step => getStepComponent(step.type) !== null)
    const supportedSteps = []
    for (const stepData of retExperimentData.steps){
        const stepType = stepData.type;
        if(getStepComponent(stepType) !== null){
            supportedSteps.push(stepData);
        }else{
            console.debug("Unseen step type: " + stepType);
        }
    }

    const stepsCounter = {};

    const accumulate = (key) => {
        const v = stepsCounter[key];
        if(v === undefined || v === null){
            stepsCounter[key] = 1
        }else{
            stepsCounter[key] = v + 1;
        }
    };

    for(const stepData of supportedSteps){
        const stepType = stepData.type;
        // 1. find meta data
        const CompCls = getStepComponent(stepType);
        const displayName = CompCls.getDisplayName();
        accumulate(stepType);
        const stepCount = stepsCounter[stepType];

        // 2. get step ui title
        let stepTitle;
        if (stepCount > 1) {
            stepTitle = displayName + TWO_STAGE_SUFFIX
        } else {
            stepTitle = displayName;
        }
        stepData['displayName'] = stepTitle;
    }

    retExperimentData.steps = supportedSteps;

    return retExperimentData;
}