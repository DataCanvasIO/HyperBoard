import React from 'react';
import ReactDOM from 'react-dom';
import { ExperimentSummary } from './pages/experimentSummary'
import {ActionType, Steps, StepStatus} from "./constants";
import { prepareExperimentData } from "./components/prepare";
import { Dataset } from './pages/dataset'
import { experimentReducer, ExperimentUIContainer } from './pages/experimentRedux'
import { getInitData, sendFinishData } from './mock/spaceSearchMockData.js'
import { datasetMockData, datasetMockDataClassification } from './mock/plotDatasetMockData.js'
import { experimentConfigMockData } from './mock/experimentConfigMockData'
import { Provider } from "react-redux"
import { createStore } from "redux"
import request from './request';


const log = console;

// const experimentData = getInitData() ; // 给一个初始化数据，在页面提示正在等待后端返回数据
const experimentData = {
    status: "init", //
    steps: []
}

const domElement = document.getElementById('root');

const store = createStore(experimentReducer, experimentData);

ReactDOM.render(
    <Provider store={store}>
        <ExperimentUIContainer/>
    </Provider>,
    domElement
);


function isExperimentFinishedEvent(event){
    const {type} = event;
    return type === ActionType.ExperimentBreak || type === ActionType.ExperimentEnd
}

let eventBegin = 0;
let watchEventInterval = null ;

function watchNewEvents(){
    const params = {begin: eventBegin};
    request.get(`/api/events`, params).then(response => {
        log.info("watchNewEvents begin event "+ eventBegin.toString() + ", response")
        log.info(JSON.stringify(response))


        const events = response.data.events ;
        eventBegin = eventBegin + events.length;

        events.forEach(event => {
            // 往 store 里发送事件
            store.dispatch(
                event
            )

            // check experiment whatever finished
            if (isExperimentFinishedEvent(event)){
                log.info("checked finished event, stop the interval, id: " + watchEventInterval.toString())
                if (watchEventInterval !== null){
                    clearInterval(watchEventInterval)
                }
            }
        });
    })
}

// TODO: 处理后端服务已经停止的情况，实验中断或者被强行停止
request.get(`/api/events`).then(response => {
    console.info("response");
    console.info(response);

    const data = response.data;
    const { events } = data;
    let experimentFinished = false;
    // merge all events now
    let expState = {}
    events.forEach( event => {
        expState = experimentReducer(expState, event)
        const {type} = event;
        if(type === ActionType.ExperimentBreak || type === ActionType.ExperimentEnd) {
            experimentFinished = true;
        }
    });

    // send to store
    store.dispatch(
        {
            type: ActionType.ExperimentStart,
            payload: expState
        }
    )

    // start interval to watch new events if experiment not finished
    if (!experimentFinished){
        eventBegin = events.length;
        watchEventInterval = setInterval(watchNewEvents, 1000);
        log.info("experiment not finished yet, start a interval to watch new event, interval id: "
            + watchEventInterval.toString() + ", current already received " + eventBegin.toString() + " events ")
    }else{
        log.info("checked experiment is finished on page start, do not start the watchNewEvent interval")
    }
})


