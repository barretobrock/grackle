import React from "react";
import { Header } from "semantic-ui-react";
// local imports
import Layout from "./Layout";
import TransactionSplit from "./FormItems/TransactionSplit";
import Amount from "./FormItems/Amount";
import DatePicker from "./FormItems/DatePicker";
import TransactionForm from "./Forms/Transaction";

const TestPage = () => {

    const date = new Date();

    return (
        <Layout>
            <Header as={'h2'}>Test Page</Header>
            {/*<TransactionSplit />*/}
            {/*<Amount />*/}
            {/*<DatePicker id={'dp'} lastDate={date}/>*/}
            <TransactionForm />
        </Layout>
    );
};

export default TestPage;