import React from 'react';
import ReactDOM from 'react-dom';
import { ExperimentSummary } from './pages/experimentSummary'
import { Dataset } from './pages/dataset'
import { ExperimentUIContainer, experimentReducer } from './pages/experimentRedux'
import { getInitData, sendFinishData } from './mock/spaceSearchMockData.js'
import { Provider } from "react-redux"
import { createStore } from "redux"
import { Result } from 'antd'

export function renderDatasetSummary(data, domElement){
    ReactDOM.render(
        <Dataset data={data}/>,
        domElement
    );
}

export function renderExperimentSummary(experimentData, domElement){
    ReactDOM.render(
        <ExperimentSummary experimentData={experimentData}/>,
        domElement
    );
}


export function renderExperimentProcess(experimentData, domElement) {
    const store = createStore(experimentReducer, experimentData);
    ReactDOM.render(
        <Provider store={store}>
            <ExperimentUIContainer/>
        </Provider>,
        domElement
    );
    return store
}

export function renderLossState(domElement) {
    ReactDOM.render(
        <Result
            status="warning"
            title="The experiment state data was lost"
            subTitle={"Maybe you refreshed the page before the experiment finished, you may be able to create the widget by running the appropriate cells. "}
        />,
        domElement
    );
}

export { ActionType, StepStatus, Steps } from "./constants";
export { experimentReducer } from './pages/experimentRedux'

// ----------------------------Test Experiment UI----------------------------------------
// const initData = getInitData();
// const store = renderExperimentProcess(initData, document.getElementById('root'));
// sendFinishData(store);
// --------------------------------------------------------------------------------------

// ----------------------------Test Dataset----------------------------------------
// renderDatasetSummary(datasetMockDataClassification, document.getElementById('root'));
// --------------------------------------------------------------------------------------

// ----------------------------Test Experiment Summary----------------------------------------
// renderExperimentSummary(experimentConfigMockData, document.getElementById('root'));
// --------------------------------------------------------------------------------------


// ----------------------------Test Render loss state -----------------------------------
// renderLossState(document.getElementById('root'));
// --------------------------------------------------------------------------------------
