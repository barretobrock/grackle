import React, {Component} from "react";
import {Button, Form} from "semantic-ui-react";
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
        this.handleAmountChange = this.handleAmountChange.bind(this);
        this.state = {
            selectedAccount: '',
            credit: 0,
            debit: 0,
            memo: '',
            addToInvoice: false,
        }
    }

    componentDidMount() {
        if(this.props.transactionId){
            console.log("heere " + this.props.transactionId);
        }
    }

    handleAccountChange = (split_id, acctDict) => {
        this.props.onAccountChange(split_id, acctDict);
    }

    handleAmountChange = (split_id, name, value ) => {
        this.props.onAmountChange(split_id, name, value);
    }

    handleMemoChange = (split_id, value) => {
        this.props.onMemoChange(split_id, 'memo', value);
    }
    handleAddToInvoiceChange = (split_id, value) => {
        this.props.onAddToInvoiceChange(split_id, 'addToInvoice', value);
    }

    handleRemoveClick = (event, data) => {
        this.props.onRemoveClicked(data.split_id);
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
                    id={'amt_selection-' + this.props.split_id}
                    onChange={this.handleAmountChange}
                />
                <Form.Field
                    label={'Memo'}
                    width={2}
                    control={Memo}
                    split_id={this.props.split_id}
                    id={'memo_selection-' + this.props.split_id}
                    onChange={this.handleMemoChange}
                />
                <Form.Field
                    label={'Add to Invoice'}
                    width={1}
                    control={AddToInvoiceCheckbox}
                    split_id={this.props.split_id}
                    id={'a2i-' + this.props.split_id}
                    onChange={this.handleAddToInvoiceChange}
                />
                <Button
                    negative
                    icon={'trash alternate outline'}
                    size={'small'}
                    split_id={this.props.split_id}
                    compact
                    onClick={this.handleRemoveClick}
                    className={'delete-split'} />
            </Form.Group>
        )
    }
}

export default TransactionSplit;