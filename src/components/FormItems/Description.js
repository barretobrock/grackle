import { useEffect, useState } from "react";
import axios from "axios";
import {Dropdown} from "semantic-ui-react";
// local imports


const Description = ({ onChange }) => {
    const [descs, setDescs] = useState([]);

    useEffect(() => {
        axios.get('/api/transactions/descriptions')
            .then(resp => setDescs(resp.data.transactions.map((transaction, index) => {
                return({id: transaction.id, desc: transaction.desc})
            })))
            .catch(function(error){
                console.log(error);
            })
    }, []);


    const handleDescriptionChange = (event, data) => {
        const description = data.value;
        console.log(description);
        const descriptionIdx = descs.findIndex(function(desc) {
            return desc.desc === description
        })
        console.log(descs[descriptionIdx]);
        onChange(descs[descriptionIdx]);
    }

    return(
        <Dropdown
            className={'description'}
            placeholder={'Description'}
            fluid
            search
            selection
            options={descs}
            onChange={handleDescriptionChange}
        />
    )
}
export default Description;