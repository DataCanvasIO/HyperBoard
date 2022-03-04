import  { experimentVis }  from "hyperboard-frontend";
import request from './request';

const { renderDatasetSummary, experimentReducer, renderExperimentProcess, ActionType, StepStatus } = experimentVis;

const log = console;

log.info(experimentReducer);

const experimentData = {
    status: "init", //
    steps: []
}

const domElement = document.getElementById('root');
const experimentStore = renderExperimentProcess(experimentData, domElement)

function send2store(event){
    experimentStore.dispatch(event)
}

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
            send2store(event)

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
    send2store(
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


