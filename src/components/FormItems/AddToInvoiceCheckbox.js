import {useState} from "react";
import {Checkbox} from "semantic-ui-react";

const AddToInvoiceCheckbox = ({ split_id, onChange }) => {
    const [addToInvoice, setAddToInvoice] = useState(false);

    const handleChange = (event, {checked}) => {
        const a2I = checked;
        setAddToInvoice(a2I);
        onChange(split_id, a2I);
    }

    return(
        <Checkbox
            checked={addToInvoice}
            onChange={handleChange}
        />
    )
}

export default AddToInvoiceCheckbox;