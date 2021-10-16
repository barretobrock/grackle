import React  from "react";
import {BrowserRouter as Router, Route, Switch} from "react-router-dom";
import importedComponent from "react-imported-component";
// local imports
import './App.css';
import Home from "./components/Home";
import DynamicPage from "./components/DynamicPage";
import TestPage from "./components/TestPage";
import MainMenu from "./components/Menu";
import Loading from "./components/Loading";
import TransactionSplit from "./components/FormItems/TransactionSplit";

const AsyncDynamicPage = importedComponent(
    () => import(/* webpackChunkName:'DynamicPage' */ './components/DynamicPage'),
    {
        LoadingComponent: Loading
    }
);

const AsyncNoMatch = importedComponent(
    () => import(/* webpackChunkName:'NoMatch' */ './components/NoMatch'),
    {
        LoadingComponent: Loading
    }
);


const App = () => {
    return (
        <div className="App">
            <Router>
                <div className={'menu'}>
                    <MainMenu />
                </div>
                <div className={'content-area'}>
                    <Switch>
                        <Route exact path={'/'}><Home /></Route>
                        <Route path={'/ledger'} component={AsyncDynamicPage} />
                        <Route path={'/test'}><TestPage /></Route>
                        <Route path={'/transaction/edit/:transactionId'}><TransactionSplit /></Route>
                        <Route component={AsyncNoMatch} />
                    </Switch>
                </div>
            </Router>
        </div>
  );
}

export default App;
