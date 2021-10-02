import React, { useEffect, useState } from "react";
import ReactLoading from 'react-loading';
import Plot from 'react-plotly.js';

const ChartAccount = ({ name }) => {
    const [graphData, setGraphData] = useState([]);
    const [done, setDone] = useState(undefined);

    useEffect(() => {
        setTimeout(() => {
            fetch('/api/time', {
                method: 'GET'
            })
                .then(res => res.json())
                .then(json => {
                    console.log(json);
                    setGraphData(json);
                    setDone(true);
                });
        }, 2000);
    }, []);

    return (
        <div>
            {!done ? (
                <ReactLoading
                    type={'bars'}
                    color={'#03fc4e'}
                    height={100}
                    width={100}
                />
            ) : (
                <div className={'chart-container'}>
                    <Plot data={graphData.data} layout={graphData.layout}/>
                </div>
            )}
        </div>
    );
}

export default ChartAccount;