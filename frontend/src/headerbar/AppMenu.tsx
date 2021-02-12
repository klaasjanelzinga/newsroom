import * as React from 'react'
import {IconButton, Menu, MenuItem} from '@material-ui/core';
import MenuIcon from '@material-ui/icons/Menu';
import {RouteComponentProps, withRouter} from 'react-router-dom';

type AppMenuState = {
    anchorEl: null | HTMLElement;
    menuOpen: boolean;
}

class AppMenu extends React.Component<RouteComponentProps, AppMenuState> {
    state: AppMenuState = {
        anchorEl: null,
        menuOpen: false,
    };

    handleMenu = (event: React.MouseEvent<HTMLElement>): void => {
        this.setState({
            anchorEl: event.currentTarget,
            menuOpen: true,
        });
    }

    handleClose = (): void => {
        this.setState({
            menuOpen: false,
            anchorEl: null,
        });
    }

    handleManageSubscriptions = (): void => {
        this.handleClose();
        this.props.history.push('/user/manage-subscriptions');
    }

    handleNews = (): void => {
        this.handleClose();
        this.props.history.push('/');
    }

    handleReadNews = (): void => {
        this.handleClose();
        this.props.history.push('/read-news');
    }

    render(): JSX.Element {
        return (
            <div>
                <IconButton
                    aria-label="Application menu"
                    aria-controls="menu-appbar"
                    aria-haspopup="true"
                    onClick={this.handleMenu}
                    color="inherit">
                    <MenuIcon/>
                </IconButton>
                <Menu
                    id="menu-appbar"
                    anchorEl={this.state.anchorEl}
                    keepMounted
                    open={this.state.menuOpen}
                    onClose={this.handleClose}>
                    <MenuItem onClick={this.handleNews}>News</MenuItem>
                    <MenuItem onClick={this.handleReadNews}>Old news</MenuItem>
                    <MenuItem onClick={this.handleManageSubscriptions}>Manage subscriptions</MenuItem>
                </Menu>
            </div>
        );
    }
}

export default withRouter(AppMenu);
