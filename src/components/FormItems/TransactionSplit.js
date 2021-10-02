import React, {Component} from "react";
import axios from "axios";
import {Form, Grid} from "semantic-ui-react";
// Local imports
import './TransactionSplit.css'
import Amount from "./Amount";
import AccountSelection from "./AccountSelection";
import Memo from "./Memo";
import AddToInvoiceCheckbox from "./AddToInvoiceCheckbox";


class TransactionSplit extends Component {
    constructor(props) {
        super(props);
        this.handleAccountChange = this.handleAccountChange.bind(this);
        this.state = {
            selectedAccount: '',
            credit: 0,
            debit: 0,
            memo: '',
            addToInvoice: false,
        }
    }


    handleAccountChange = (split_id, acctDict) => {
        this.props.onAccountChange(split_id, acctDict);
    }

    handleAmountChange = (split_id, name, value ) => {
        this.props.onAmountChange(split_id, name, value);
    }

    handleMemoChange = (id, value) => {
        this.setState({memo: value});
        console.log('Memo changed: ' + value);
    }
    handleAddToInvoiceChange = (id, value) => {
        this.setState({addToInvoice: value});
        console.log('A2I changed: ' + value);
    }

    render() {
        return(
            <Form.Group>
                <Form.Field
                    width={6}
                    label={'Account'}
                    control={AccountSelection}
                    split_id={this.props.split_id}
                    id={'acct-select-' + this.props.split_id}
                    onChange={this.handleAccountChange}
                />
                <Form.Field
                    width={3}
                    control={Amount}
                    split_id={this.props.split_id}
                    id={'amt_selection_1'}
                    onChange={this.handleAmountChange}
                />
                <Form.Field
                    label={'Memo'}
                    width={2}
                    control={Memo}
                    id={'memo_selection_1'}
                    onChange={this.handleMemoChange}
                />
                <Form.Field
                    label={'Invoice'}
                    control={AddToInvoiceCheckbox}
                    id={'a2i-1'}
                    onChange={this.handleAddToInvoiceChange}
                />
            </Form.Group>
        )
    }
}

export default TransactionSplit;