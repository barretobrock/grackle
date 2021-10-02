import { useEffect, useState } from "react";
import axios from "axios";
import {Dropdown} from "semantic-ui-react";
// local imports
import './AccountSelection.css'


const AccountSelection = ({ split_id, onChange }) => {
    const [accounts, setAccounts] = useState([]);

    useEffect(() => {
        axios.get('/api/accounts')
            .then(resp => setAccounts(resp.data.accounts.map((account, index) => {
                return({id: account.id, value: account.name, text: account.name})
            })))
            .catch(function(error){
                console.log(error);
            })
    }, []);


    const handleAccountChange = (event, data) => {
        const accountName = data.value;
        const accountIdx = accounts.findIndex(function(account) {
            return account.text === accountName
        })
        console.log(accounts[accountIdx]);
        onChange(split_id, accounts[accountIdx]);
    }

    return(
        <Dropdown
            className={'account-selection'}
            placeholder={'Select Account'}
            fluid
            search
            selection
            options={accounts}
            onChange={handleAccountChange}
        />
    )
}
export default AccountSelection;