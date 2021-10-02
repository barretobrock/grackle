import {useState} from "react";
import {Checkbox} from "semantic-ui-react";

const AddToInvoiceCheckbox = ({ id, onChange }) => {
    const [addToInvoice, setAddToInvoice] = useState(false);

    const handleChange = (event, {checked}) => {
        const a2I = checked;
        setAddToInvoice(a2I);
        onChange(id, a2I);
    }

    return(
        <Checkbox
            checked={addToInvoice}
            onChange={handleChange}
        />
    )
}

export default AddToInvoiceCheckbox;