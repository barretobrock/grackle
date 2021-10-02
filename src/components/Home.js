import React from "react";
import { Link } from "react-router-dom";
// local imports
import Layout from "./Layout";
import logo from '../logo.svg'
import '../css/Home.css'

const Home = () => {
    return (
        <div>
            <img className={'grackle-big'} src={logo} alt={'logo'} />
            <Layout>
                <p>Hello World of React and Webpack! hot loaded :)</p>
                <p>
                    <Link to={'/dynamic'}>Navigate to Dynamic Page</Link>
                </p>
            </Layout>
        </div>
    );
};

export default Home;