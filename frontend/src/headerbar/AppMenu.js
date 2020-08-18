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
    this.handleEvents = this.handleEvents.bind(this);
    this.handleVenues = this.handleVenues.bind(this);
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

  handleVenues() {
    this.handleClose();
    this.props.history.push('/venues');
  }

  handleEvents() {
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
          <MenuItem onClick={this.handleEvents}>Events</MenuItem>
          <MenuItem onClick={this.handleVenues}>Venues</MenuItem>
        </Menu>
      </div>
    );
  }
}

AppMenu.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(AppMenu));
