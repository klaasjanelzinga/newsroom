import { Avatar, IconButton, Menu, MenuItem } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import { AccountCircle } from '@material-ui/icons';
import PropTypes from 'prop-types';
import React from 'react';
import { withRouter } from 'react-router-dom';
import UserProfile from '../user/UserProfile';

const styles = theme => ({
});


class HeaderMenu extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      anchorEl: null,
      menuOpen: false,
      signedIn: false,
    };

    this.handleClose = this.handleClose.bind(this);
    this.handleMenu = this.handleMenu.bind(this);
    this.handleSignIn = this.handleSignIn.bind(this);
    this.handleSignOut = this.handleSignOut.bind(this);
    this.handleMyProfile = this.handleMyProfile.bind(this);
  }

  componentDidMount() {
    this.userProfile = UserProfile.load();
    this.setState({signedIn: this.userProfile !== null })
  }

  handleMenu(event) {
    this.setState({
      anchorEl: event.currentTarget,
      menuOpen: true,
    });
  }

  handleClose() {
    this.setState({
      menuOpen: false,
      anchorEl: null,
    });
  }

  handleSignIn() {
    this.handleClose();
    this.setState({ signedIn: true });
    this.props.history.push('/user/signin');
  }

  handleSignOut() {
    this.handleClose();
    this.setState({ signedIn: false });
    this.props.history.push('/user/signout');
  }

  handleMyProfile() {
    this.props.history.push('/user/profile');
  }

  accountAvatar() {
    if (this.state.signedIn) {
      return <Avatar alt={this.userProfile.givenName} 
                      src={this.userProfile.avatarUrl} 
                      />
    }
    return <AccountCircle />
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
            onClose={this.handleClose} >
            <MenuItem disabled={this.state.signedIn} onClick={this.handleSignIn}>Sign in</MenuItem>
            <MenuItem disabled={!this.state.signedIn} onClick={this.handleMyProfile}>Profile</MenuItem>
            <MenuItem disabled={!this.state.signedIn} onClick={this.handleSignOut}>Sign out</MenuItem>
        </Menu>
      </div>
    );
  }
}

HeaderMenu.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(HeaderMenu));