import {useState} from "react";
import {Input} from "semantic-ui-react";

const Memo = ({ id, onChange }) => {
    const [memo, setMemo] = useState('');

    const handleChange = (event) => {
        const memo = event.target.value;
        setMemo(memo);
        onChange(id, memo);
    }

    return(
        <Input
            placeholder={'Memo'}
            type={'text'}
            value={memo}
            onChange={handleChange}
        />
    )
}

export default Memo;