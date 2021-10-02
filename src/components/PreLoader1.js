import React, { useEffect, useState } from "react";
import ReactLoading from 'react-loading';

function PreLoader1() {
    const [data, setData] = useState([]);
    const [done, setDone] = useState(undefined);

    useEffect(() => {
        setTimeout(() => {
            fetch('/api/time')
                .then(res => res.json())
                .then(json => {
                    console.log(json);
                    setData(json);
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
                <ul>
                    <li key={1}>{data.time}</li>
                </ul>
            )}
        </div>
    );
}

export default PreLoader1;