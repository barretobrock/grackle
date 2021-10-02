import React, { Component } from "react";
import { Icon, Menu, Dropdown } from "semantic-ui-react";
import { Link } from "react-router-dom";
// local imports
import logo from "../logo.svg";


class MainMenu extends Component {
    state = { activeItem: 'home' }

    handleItemClick = (e, { name }) => this.setState({ activeItem: name })

    GrackleLogo = () => {
        return (
            <img src={logo} className="logo" alt="logo" />
        )
    }

    make_menu_item = (route, name, icon, text ) => {
        return (
            <Menu.Item as={ Link } to={route} name={name} active={this.state.activeItem === name} onClick={this.handleItemClick}>
                {icon}
                {text}
            </Menu.Item>
        )
    }

    make_dropdown_item = ( route, name, text ) => {
        return (
            <Dropdown.Item as={ Link } to={route} name={name} active={this.state.activeItem === name} onClick={this.handleItemClick}>
                {text}
            </Dropdown.Item>
        )
    }

    render() {
        return (
            <Menu pointing compact fixed={'top'} size={'small'} id={'main-menu'}>
                {this.make_menu_item('/', 'home', this.GrackleLogo(), '')}
                <Dropdown item icon={'chart line'} text={'Analysis'}>
                    <Dropdown.Menu>
                        {this.make_dropdown_item('/mvb', 'mvb', 'MvB')}
                        {this.make_dropdown_item('/mvm', 'mvm', 'MvM')}
                        {this.make_dropdown_item('/budget-analysis', 'budget-analysis', 'Budget Analysis')}
                    </Dropdown.Menu>
                </Dropdown>
                {this.make_menu_item('/ledger', 'ledger', <Icon name={'book'}/>, 'Ledger')}
                {this.make_menu_item('/test', 'test', <Icon name={'book'}/>, 'Test')}
                {this.make_menu_item('/new-transaction', 'new-transaction', <Icon name={'plus'}/>, 'New Transaction')}
                {this.make_menu_item('/upload', 'upload', <Icon name={'upload'}/>, 'Upload')}
                {this.make_menu_item('/invoices', 'invoices', <Icon name={'clipboard outline'}/>, 'Invoices')}
            </Menu>
        )
    }
}

export default MainMenu;