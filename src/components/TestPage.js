import React from "react";
import { Header } from "semantic-ui-react";
// local imports
import Layout from "./Layout";
import TransactionSplit from "./FormItems/TransactionSplit";
import Amount from "./FormItems/Amount";
import TransactionForm from "./Forms/Transaction";
import TransactionView from "./Views/Transaction";

const TestPage = () => {

    const date = new Date();

    return (
        <Layout>
            <Header as={'h2'}>Test Page</Header>
            {/*<TransactionSplit />*/}
            {/*<Amount />*/}
            {/*<TransactionForm />*/}
            <TransactionView />
        </Layout>
    );
};

export default TestPage;