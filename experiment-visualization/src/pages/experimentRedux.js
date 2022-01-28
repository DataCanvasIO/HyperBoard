import React from 'react';
import {showNotification} from "../util"
import {connect } from "react-redux";
import {ExperimentUI} from "./experiment"
import {ActionType} from "../constants";
import {Steps, StepStatus} from "../constants";


const log = console;

const handleAction = (state, action, stepIndex, handler, actionType) => {
    const experimentConfig = state;

    var found = false;
    experimentConfig.steps.forEach((step, i, array) => {
        if (step.index === stepIndex) {
            found = true;
            // experimentConfig, action, stepIndexInArray
            handler(state, action, stepIndex)
        }
    });

    if (!found) {
        console.error(`Handler= ${actionType} index = ${action.stepIndex}  not found for update trial and action/state is :`);
        console.error(action);
        console.error(state);
    }
    return experimentConfig;

};

const handleProbaDensityLabelChange = (experimentConfig, action, stepIndexInArray) => {
    const  stepPayload = action.payload;
    experimentConfig.steps[stepIndexInArray].extension.selectedLabel = stepPayload.selectedLabel;
    return experimentConfig;
};


const handleFeatureImportanceChange = (experimentConfig, action, stepIndexInArray) => {
    const  stepPayload = action.payload;
    experimentConfig.steps[stepIndexInArray].extension.selectedTrialNo = stepPayload.selectedTrialNo;
    return experimentConfig;
};


const handleTrailFinish = (experimentConfig, action, stepIndexInArray) => {

    const {trialData: stepPayload} = action.payload;


    const searchStepExtension = experimentConfig.steps[stepIndexInArray].extension;
    if (searchStepExtension === undefined || searchStepExtension == null) {
        experimentConfig.steps[stepIndexInArray].extension = {}
    }
    const trials = experimentConfig.steps[stepIndexInArray].extension.trials;
    if (trials === undefined || trials === null) {
        experimentConfig.steps[stepIndexInArray].extension.trials = []
    }

    const trialData = {...stepPayload};

    experimentConfig.steps[stepIndexInArray].extension.earlyStopping = trialData.earlyStopping;
    experimentConfig.steps[stepIndexInArray].extension.maxTrials = trialData.maxTrials;  // persist maxTrials (does not use a special action)


    delete trialData.earlyStopping;

    experimentConfig.steps[stepIndexInArray].extension.trials.push(trialData);

    return experimentConfig;

};

const handleEarlyStopped = (experimentConfig, action, stepIndexInArray) => {
    const {payload} = action;
    experimentConfig.steps[stepIndexInArray].extension.earlyStopping = payload.data;
    return experimentConfig
};

const handleStepFinish = (experimentConfig, action, stepIndexInArray) => {

    const stepPayload = action.payload;
    const step = experimentConfig.steps[stepIndexInArray];
    if (step.type !== 'SpaceSearchStep') { // to avoid override 'trials'
        experimentConfig.steps[stepIndexInArray].extension = stepPayload.extension;
    } else {
        experimentConfig.steps[stepIndexInArray].extension.input_features = stepPayload.extension.input_features;
        experimentConfig.steps[stepIndexInArray].extension.features = stepPayload.extension.features;
    }
    // experimentConfig.steps[i].extension = stepPayload.extension;
    experimentConfig.steps[stepIndexInArray].status = stepPayload.status;
    experimentConfig.steps[stepIndexInArray].end_datetime = stepPayload.end_datetime;

    return experimentConfig;
};

const handleStepBegin = (experimentConfig, action, stepIndexInArray) => {
    const stepPayload = action.payload;
    const step = experimentConfig.steps[stepIndexInArray];
    step.status = stepPayload.status;
    const start_datetime = stepPayload.start_datetime;
    if(start_datetime !== undefined && start_datetime !== null){
        step.start_datetime = stepPayload.start_datetime
    }else {
        console.error("in step begin event but start_datetime is null ");
    }
    return experimentConfig;
};

const handleStepError = (experimentConfig, action, stepIndexInArray) => {
    const stepPayload = action.payload;

    const step = experimentConfig.steps[stepIndexInArray];

    step.status = stepPayload.status;
    const reason = stepPayload.extension.reason;
    if (reason !== null && reason !== undefined){
        showNotification(<span>
            {reason.toString()}
        </span>);
    }
    return experimentConfig;

};

// Map Redux state to component props
function mapStateToProps(state) {
    return {experimentData: state}
}

// Map Redux actions to component props
function mapDispatchToProps(dispatch) {
    return {dispatch}
}

function getRunningSpaceSearchStepIndex(experimentConfig){
    // TODO: not init
    for(const step of experimentConfig.steps){
        if(step.type === Steps.SpaceSearch.type){
            if(step.status === StepStatus.Process){
                return  step.index
            }
        }
    }
    return -1
}

// Reducer: Transform action to new state
export function experimentReducer(state, action) {
    const requestId = Math.random() * 10000;

    const {type, payload } = action;  // every action should has `type` and `payload` field
    console.debug(`Rev action(${requestId}): `);
    console.debug(action);
    console.debug(`Rev state(${requestId}): `);
    console.debug(state);
// ActionType.ExperimentInit

    let newState;
    if (type === ActionType.StepEnd) {
        const { index } = payload;
        newState  = handleAction(state, action, index, handleStepFinish, type);
    } else if (type === ActionType.StepStart) {
        const { index } = payload;
        newState  = handleAction(state, action, index, handleStepBegin, type);
    } else if (type === ActionType.StepBreak) {
        const { index } = payload;
        newState  = handleAction(state, action, index, handleStepError, type);
    } else if (type === ActionType.ProbaDensityLabelChange) {
        const { stepIndex } = payload;
        newState  = handleAction(state, action, stepIndex, handleProbaDensityLabelChange, type);
    } else if (type === ActionType.FeatureImportanceChange) {
        const { stepIndex } = payload;
        newState  = handleAction(state, action, stepIndex, handleFeatureImportanceChange, type);
    } else if (type === ActionType.TrialEnd) {
        const stepIndex = getRunningSpaceSearchStepIndex(state);
        const { modelInstanceId } = payload;
        if(stepIndex !== -1){
            log.debug("found step index " + stepIndex + " for model instance id " + modelInstanceId);
            newState  = handleAction(state, action, stepIndex, handleTrailFinish, type);
        }else{
            log.error("do not match trial to step, payload:");
            log.error(payload)
            newState = {...state}
        }
    } else if (type === ActionType.EarlyStopped) {
        const { stepIndex } = payload;
        newState  = handleAction(state, action, stepIndex, handleEarlyStopped, type);
    }  else if (type === ActionType.ExperimentStart) {
        newState = {...payload}
    }  else if (type === ActionType.ExperimentEnd) {
        console.info("experiment finished") // TODO: 接受到这个事件停止定时器轮询
        // newState = {...payload}
        newState = {...state}
    } else {
        if(!type.startsWith('@@redux')){  // redux built-in action type
            console.error("Unknown action type: " + type);
        }
        newState = state
    }

    console.debug(`Output new state(${requestId}): `);
    console.debug(newState);
    return {...newState};
}


// Connected Component
export const ExperimentUIContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(ExperimentUI);


