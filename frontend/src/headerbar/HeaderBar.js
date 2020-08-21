import AppBar from '@material-ui/core/AppBar';
import {withStyles} from '@material-ui/core/styles';
import Toolbar from '@material-ui/core/Toolbar';
import PropTypes from 'prop-types';
import React from 'react';
import AppMenu from './AppMenu';
import HeaderMenu from './HeaderMenu';
import Title from './Title';


const styles = theme => ({
  headerbar: {
    width: '100%',
  },
  grow: {
    flexGrow: 1,
  },
  sectionDesktop: {
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'flex',
    },
  },
  sectionMobile: {
    display: 'flex',
    [theme.breakpoints.up('md')]: {
      display: 'none',
    },
  },
});

class HeaderBar extends React.Component {

  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
  }


  handleChange(event, newValue) {
    this.setState({ selectedTab: newValue })
  }

  render() {
    const { classes } = this.props;
    return (
      <div className={classes.headerbar}>
        <AppBar position="static">
          <Toolbar>
            <Title />
            <div className={classes.grow} />
            <AppMenu />
            <HeaderMenu />
          </Toolbar>
        </AppBar>

      </div>
    );
  }
}

HeaderBar.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(HeaderBar);
