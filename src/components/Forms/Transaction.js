import {Component} from "react";
import axios from "axios";
import {Button, Form} from "semantic-ui-react";
import SemanticDatepicker from "react-semantic-ui-datepickers";
// local imports
import './Transaction.css'
import DatePicker from "../FormItems/DatePicker";
import TransactionSplit from "../FormItems/TransactionSplit";
import getISODate from "../ISODate";



class TransactionForm extends Component {
    constructor(props) {
        super(props);
        this.handleAccountChange = this.handleAccountChange.bind(this);
        this.handleAmountChange = this.handleAmountChange.bind(this);
        this.addSplit = this.addSplit.bind(this);
        this.state = {
            transactionDate: '',
            desc: '',
            credits: 0,
            debits: 0,
            splits: [
                {account: {}},
                {account: {}}
            ],
        }
    }

    handleAccountChange = (split_id, acctDict) => {
        let splits = [...this.state.splits];
        let split = {...splits[split_id]};
        split.account = acctDict;
        splits[split_id] = split
        this.setState({ splits });
        console.log('Account selected for id ' + split_id + ': ' + acctDict);
        console.log(splits);
    }

    handleAmountChange = (split_id, name, value) => {
        let splits = [...this.state.splits];
        let split = {...splits[split_id]};
        split[name] = parseFloat(value);
        splits[split_id] = split
        this.setState({ splits });
        console.log('Amount of ' + name + ' selected for id ' + split_id + ': ' + value);
        console.log(splits);
        if(name === 'credit'){
            let credits = this.state.credits;
            let newVal = credits + parseFloat(value);
            this.setState({credits: newVal})
        } else if(name === 'debit'){
            let debits = this.state.debits;
            let newVal = debits + parseFloat(value);
            this.setState({debits: newVal})
        }
    }

    handleDateChange = (event, data) => {
        const newDate = getISODate(data.value);
        this.setState({ transactionDate: newDate });
        console.log('New date set to ' + newDate);
    }

    handleDescChange = event => {
        const desc = event.target.value;
        this.setState({ description: desc });
        console.log('New desc set to ' + desc);
    }

    addSplit = event => {
        // console.log(this.state.splits.length);
        let newSplit = this.state.splits.length;
        let splits = [...this.state.splits];
        let split = {...splits[newSplit]};
        split.account = {};
        splits[newSplit] = split;
        // console.log(split);
        this.setState({splits});
        // console.log(this.state.splits);
    }

    handleSubmit = event => {
        event.preventDefault();

        const details = {
            date: this.state.transactionDate,
            desc: this.state.desc,
            splits: this.state.splits,
        };

        axios.post('/api/transaction/new', { details })
            .then(res => {
                console.log(res);
                console.log(res.data);
            })
    }



    render() {
        return(
            <Form className={'transaction-form'}>
                <Form.Group>
                    <SemanticDatepicker onChange={this.handleDateChange} width={2} label={'Date'} clearable={true}/>
                    <Form.Input label={'Description'} width={7} onChange={this.handleDescChange} />
                    <Form.Input disabled label={'Total'} width={2}>{this.state.credits - this.state.debits}</Form.Input>
                </Form.Group>
                {this.state.splits.length > 0 && this.state.splits.map((split, i) => {
                    return <TransactionSplit
                        split_id={i}
                        onAccountChange={this.handleAccountChange}
                        onAmountChange={this.handleAmountChange}
                    />
                })}
                <Button onClick={this.addSplit} />
            </Form>
        )
    }
}

export default TransactionForm;