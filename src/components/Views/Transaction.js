import {Component, createRef} from "react";
import {Button, Table} from "semantic-ui-react";
import axios from "axios";
import {Link} from "react-router-dom";
// local
import './Transaction.css'
import Loading from "../Loading";


class TransactionView extends Component {
    constructor(props) {
        super(props);
        this.state = {
            accountName: this.props.accountName,
            accountId: this.props.accountId,
            transactions: null,
        }
    }

    componentDidMount() {
        axios.get('/api/account/transactions/' + this.state.accountId)
            .then(resp => this.setState({ transactions: resp.data.splits.map((split, index) => {
                return({
                    id: split.id,
                    transaction_id: split.transaction_id,
                    transaction_date: split.transaction_date,
                    is_credit: split.is_credit,
                    desc: split.desc,
                    reconciled: split.reconciled,
                    invoice: split.invoice,
                    amount: split.amount,
                    balance: split.balance
                })
                })}))
            .catch(function(error) {
                console.log(error);
            });
    }

    render() {
        if (!this.state.transactions)
            return (
                <Loading />
            );
        return(
            <div className={'transaction-table'}>
                <Table celled inverted selectable>
                    <Table.Header fullWidth>
                        <Table.Row>
                            <Table.HeaderCell width={1}>Date</Table.HeaderCell>
                            <Table.HeaderCell width={1}>R</Table.HeaderCell>
                            <Table.HeaderCell>Description</Table.HeaderCell>
                            <Table.HeaderCell width={1}>Credit (-)</Table.HeaderCell>
                            <Table.HeaderCell width={1}>Debit (+)</Table.HeaderCell>
                            <Table.HeaderCell width={2}>Balance</Table.HeaderCell>
                            <Table.HeaderCell width={2}>Invoice</Table.HeaderCell>
                            <Table.HeaderCell width={1}>Edit</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {this.state.transactions.length > 0 && this.state.transactions.map((t, i) => {
                            return <Table.Row className={'transaction rec-state-' + t.reconciled} key={i}>
                                <Table.Cell>{t.transaction_date}</Table.Cell>
                                <Table.Cell>{t.reconciled}</Table.Cell>
                                <Table.Cell>{t.desc}</Table.Cell>
                                <Table.Cell className={'credit-cell'}>{t.is_credit ? Math.round(t.amount * 100) / 100 : 0}</Table.Cell>
                                <Table.Cell className={'debit-cell'}>{!t.is_credit ? Math.round(t.amount * 100) / 100 : 0}</Table.Cell>
                                <Table.Cell className={'balance-cell'}>{Math.round(t.balance * 100) / 100}</Table.Cell>
                                <Table.Cell>{t.invoice}</Table.Cell>
                                <Table.Cell><Button icon={'edit outline'} as={Link} to={'/api/transaction/edit/' + t.transaction_id} /></Table.Cell>
                            </Table.Row>
                        })}
                    </Table.Body>
                </Table>
            </div>

        )
    }
}

TransactionView.defaultProps = {
    accountName: 'Assets.Current Assets.UFCU.CHK',
    accountId: 163
}

export default TransactionView;