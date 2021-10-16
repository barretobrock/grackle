import {Component} from "react";
import axios from "axios";
import {Button, Form} from "semantic-ui-react";
import SemanticDatepicker from "react-semantic-ui-datepickers";
// local imports
import './Transaction.css'
import TransactionSplit from "../FormItems/TransactionSplit";
import getISODate from "../ISODate";
import Description from "../FormItems/Description";



class TransactionForm extends Component {
    constructor(props) {
        super(props);
        this.handleAccountChange = this.handleAccountChange.bind(this);
        this.handleAmountChange = this.handleAmountChange.bind(this);
        this.addSplit = this.addSplit.bind(this);
        this.state = {
            transactionDate: '',
            desc: {},
            credit: 0,
            credits: [],
            debit: 0,
            debits: [],
            balance: 0,
            splits: [
                {account: this.props.primaryAccount, credit: 0, debit: 0},
                {account: {}, credit: 0, debit: 0}
            ],
        }
    }

    componentDidMount() {
        this.setState({credit: this.calculateTotal(this.state.credits)});
        this.setState({debit: this.calculateTotal(this.state.debits)});
    }

    calculateTotal = (figures) => {
        return Object.entries(figures).reduce((finalValue, [key, value]) => {
            if(value === '') {
                // if entered value is empty string '', omit
                return finalValue;
            }
            return finalValue + value;
        }, 0)
    }

    handleTotal = (split_id, name, value) => {
        const parsedValue = value === '' ? '' : parseFloat(value);
        this.setState((prevState) => {
            if(name === 'credit'){
                const updatedCredits = {
                    ...prevState.credits,
                    [name]: parsedValue
                };
                const newCredit = this.calculateTotal(updatedCredits);
                const debit = prevState.debit
                return {
                    credits: updatedCredits,
                    credit: newCredit,
                    balance: debit - newCredit
                }
            } else if(name === 'debit') {
                const updatedDebits = {
                    ...prevState.debits,
                    [name]: parsedValue
                };
                const newDebit = this.calculateTotal(updatedDebits);
                const credit = prevState.credit
                return {
                    debits: updatedDebits,
                    debit: newDebit,
                    balance: newDebit - credit
                }
            }
        })
    }

    splitDataHandler = (split_id, name, value) => {
        // Handles taking in new data for a given split and setting state with it
        const floatObjs = ['credit', 'debit'];
        let splits = [...this.state.splits];
        let split = {...splits[split_id]};
        if(floatObjs.includes(name)) {
            // Cast this object to float while adding
            split[name] = parseFloat(value);
        } else {
            split[name] = value;
        }
        splits[split_id] = split;
        this.setState({ splits });
        console.log('Split data with name ' + name + ' set with data ' + value + ' at id ' + split_id);
        console.log(splits);
    }

    handleAccountChange = (split_id, acctDict) => {
        this.splitDataHandler(split_id, 'account', acctDict);
    }

    handleAmountChange = (split_id, name, value) => {
        this.splitDataHandler(split_id, name, value);
        this.handleTotal(split_id, name, value);
    }

    handleGeneralChange = (split_id, name, value) => {
        this.splitDataHandler(split_id, name, value);
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

    addSplit = () => {
        // console.log(this.state.splits.length);
        let newSplit = this.state.splits.length;
        let splits = [...this.state.splits];
        let split = {...splits[newSplit]};
        split.account = {};
        split.credit = 0;
        split.debit = 0;
        splits[newSplit] = split;
        // console.log(split);
        this.setState({splits});
        // console.log(this.state.splits);
    }

    removeSplit = (split_id) => {
        // Remove from state
        this.setState({splits: this.state.splits.filter((_, i) => i !== split_id)});
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
            <Form className={'transaction-form'} onSubmit={this.handleSubmit}>
                <Form.Group>
                    <SemanticDatepicker onChange={this.handleDateChange} width={2} label={'Date'} clearable={true}/>
                    {/*<Form.Input width={7} control={Description} onChange={this.handleDescChange} />*/}
                    <Form.Input label={'Description'} width={7} onChange={this.handleDescChange} />
                    <Form.Input label={'Balance'} error={this.state.balance !== 0} className={'total-box'} width={1}>{this.state.balance}</Form.Input>
                </Form.Group>
                {this.state.splits.length > 0 && this.state.splits.map((split, i) => {
                    return <TransactionSplit
                        split_id={i}
                        onAccountChange={this.handleAccountChange}
                        onAmountChange={this.handleAmountChange}
                        onMemoChange={this.handleGeneralChange}
                        onAddToInvoiceChange={this.handleGeneralChange}
                        onRemoveClicked={this.removeSplit}
                    />
                })}
                <div className={'main-buttons'}>
                    <Button positive compact onClick={this.addSplit}>Add Split</Button>
                    <Button primary compact floated={'right'} onClick={this.handleSubmit}>Submit</Button>
                    <Button negative compact floated={'right'}>Cancel</Button>
                </div>
            </Form>
        )
    }
}

TransactionForm.defaultProps = {
    primaryAccount: {}
}

export default TransactionForm;