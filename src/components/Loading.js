import React from "react";
import { Dimmer, Loader } from "semantic-ui-react";

const Loading = () => {
    return(
        <Dimmer active size={'massive'}>
            <Loader>Loading</Loader>
        </Dimmer>
    )
}

export default Loading;