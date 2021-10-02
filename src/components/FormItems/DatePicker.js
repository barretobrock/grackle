import {useState} from "react";
import SemanticDatepicker from "react-semantic-ui-datepickers";


const DatePicker = (id, onChange, lastDate) => {
    const [date, setDate] = useState(lastDate);

    const handleDateChange = (event, data) => {
        const date = data.value;
        setDate(date);
        console.log('Set date ' + date);
    }

    return(
        <SemanticDatepicker onChange={handleDateChange} value={date}/>
    )
}

export default DatePicker;