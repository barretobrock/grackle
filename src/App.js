import React  from "react";
import {BrowserRouter as Router, Route, Switch} from "react-router-dom";
// local imports
import './App.css';
import Home from "./components/Home";
import DynamicPage from "./components/DynamicPage";
import TestPage from "./components/TestPage";
import MainMenu from "./components/Menu";


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
                        <Route path={'/ledger'}><DynamicPage /></Route>
                        <Route path={'/test'}><TestPage /></Route>
                    </Switch>
                </div>
            </Router>
        </div>
  );
}

export default App;
