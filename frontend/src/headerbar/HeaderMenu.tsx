import {Avatar, createStyles, IconButton, Menu, MenuItem, WithStyles} from '@material-ui/core';
import {withStyles} from '@material-ui/core/styles';
import {AccountCircle} from '@material-ui/icons';
import React from 'react';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import UserProfile from '../user/UserProfile';

const styles = createStyles({});

interface HeaderMenuProps extends RouteComponentProps, WithStyles<typeof styles> {
}

type HeaderMenuState = {
    anchorEl: null | HTMLElement;
    menuOpen: boolean;
    userProfile: UserProfile|null;
}

class HeaderMenu extends React.Component<HeaderMenuProps, HeaderMenuState> {

    state: HeaderMenuState = {
        anchorEl: null,
        menuOpen: false,
        userProfile: null,
    };

    componentDidMount= () => {
        this.setState({userProfile: UserProfile.load() })
    }

    handleMenu = (event: React.MouseEvent<HTMLElement>):void => {
        this.setState({
            anchorEl: event.currentTarget,
            menuOpen: true,
        });
    }

    handleClose = () => {
        this.setState({
            menuOpen: false,
            anchorEl: null,
        });
    }

    handleSignIn = () => {
        this.handleClose();
        this.props.history.push('/user/signin');
    }

    handleSignOut = () => {
        this.handleClose();
        this.props.history.push('/user/signout');
    }

    handleMyProfile = () => {
        this.handleClose();
        this.props.history.push('/user/profile');
    }

    accountAvatar = () => {
        if (this.state.userProfile != null) {
            return <Avatar alt={this.state.userProfile.givenName}
                           src={this.state.userProfile.avatarUrl}
            />
        }
        return <AccountCircle/>
    }

    render() {
        return (
            <div>
                <IconButton
                    aria-label="Account of current user"
                    aria-controls="menu-appbar"
                    aria-haspopup="true"
                    onClick={this.handleMenu}
                    color="inherit">
                    {this.accountAvatar()}
                </IconButton>
                <Menu
                    id="menu-appbar"
                    anchorEl={this.state.anchorEl}
                    keepMounted
                    open={this.state.menuOpen}
                    onClose={this.handleClose}>
                    <MenuItem disabled={this.state.userProfile != null} onClick={this.handleSignIn}>Sign in</MenuItem>
                    <MenuItem disabled={this.state.userProfile == null} onClick={this.handleMyProfile}>Profile</MenuItem>
                    <MenuItem disabled={this.state.userProfile == null} onClick={this.handleSignOut}>Sign out</MenuItem>
                </Menu>
            </div>
        );
    }
}

export default withStyles(styles)(withRouter(HeaderMenu));