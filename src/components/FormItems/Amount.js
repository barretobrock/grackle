import { useState} from "react";
import {Form} from "semantic-ui-react";
// local imports
import './Amount.css'

const Amount = ({ split_id, onChange }) => {
    const [credit, setCredit] = useState(Object);
    const [debit, setDebit] = useState(Object);

    const handleChange = (event, {name, value}) => {
        if(name === 'credit') {
            setCredit(value);
        } else if(name === 'debit') {
            setDebit(value);
        }
        onChange(split_id, name, value);
        // console.log('Set ' + name + ' to ' + value);
    }

    return(
        <Form.Group >
            <Form.Input
                width={10}
                label={'Credit (-)'}
                placeholder={'Credit (-)'}
                type={'number'}
                id={'credit-' + split_id}
                name={'credit'}
                value={credit}
                onChange={handleChange}
            />
            <Form.Input
                width={10}
                label={'Debit (+)'}
                placeholder={'Debit (+)'}
                type={'number'}
                 id={'debit-' + split_id}
                name={'debit'}
                value={debit}
                onChange={handleChange}
            />
        </Form.Group>
    )
}

export default Amount;