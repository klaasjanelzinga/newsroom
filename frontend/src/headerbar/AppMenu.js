import { IconButton, Menu, MenuItem } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import MenuIcon from '@material-ui/icons/Menu';
import PropTypes from 'prop-types';
import React from 'react';
import { withRouter } from 'react-router-dom';

const styles = theme => ({
});


class AppMenu extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      anchorEl: null,
      menuOpen: false,
    };

    this.handleClose = this.handleClose.bind(this);
    this.handleMenu = this.handleMenu.bind(this);
    this.handleManageSubscriptions = this.handleManageSubscriptions.bind(this);
    this.handleNews = this.handleNews.bind(this);
    this.handleSignout = this.handleSignout.bind(this);
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

  handleSignout() {
    this.handleClose();
    this.props.history.push('/user/signout');
  }

  handleManageSubscriptions() {
    this.handleClose();
    this.props.history.push('/user/manage-subscriptions');
  }

  handleNews() {
    this.handleClose();
    this.props.history.push('/');
  }

  render() {

    return (
      <div>
        <IconButton
          aria-label="Application menu"
          aria-controls="menu-appbar"
          aria-haspopup="true"
          onClick={this.handleMenu}
          color="inherit">
          <MenuIcon />
        </IconButton>
        <Menu
          id="menu-appbar"
          anchorEl={this.state.anchorEl}
          keepMounted
          open={this.state.menuOpen}
          onClose={this.handleClose} >
          <MenuItem onClick={this.handleNews}>News</MenuItem>
          <MenuItem onClick={this.handleManageSubscriptions}>Manage subscriptions</MenuItem>
          <MenuItem onClick={this.handleSignout}>Signout</MenuItem>
        </Menu>
      </div>
    );
  }
}

AppMenu.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(AppMenu));
