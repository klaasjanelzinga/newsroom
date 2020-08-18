import AppBar from '@material-ui/core/AppBar';
import { withStyles } from '@material-ui/core/styles';
import Toolbar from '@material-ui/core/Toolbar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import PropTypes from 'prop-types';
import React from 'react';
import AppMenu from './AppMenu';
import HeaderMenu from './HeaderMenu';
import SearchBox from './SearchBox';
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

const SELECTED_TAB = {
  "TODAY": 0,
  "TOMORROW": 1,
  "ALL": 2,
  "SEARCH_RESULTS": 3,
}
const SELECTED_TAB_ARRAY = [
  "TODAY",
  "TOMORROW",
  "ALL",
  "SEARCH_RESULTS",
]

class HeaderBar extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedTab: SELECTED_TAB[props.selected],
    };
    this.handleChange = this.handleChange.bind(this);
  }


  handleChange(event, newValue) {
    this.setState({ selectedTab: newValue })
    this.props.switchView(SELECTED_TAB_ARRAY[newValue])
  }

  componentDidUpdate() {
    if (this.state.selectedTab !== SELECTED_TAB[this.props.selected]) {
      this.setState({ selectedTab: SELECTED_TAB[this.props.selected] })
    }
  }

  renderSearchBox() {
    if (this.props.searchEvents === undefined) {
      return <div></div>
    } else {
      return <SearchBox searchEvents={this.props.searchEvents} />;
    }
  }

  renderTabs() {
    if (this.props.selected === "SEARCH_RESULTS") {
      return <Tabs value={this.state.selectedTab} onChange={this.handleChange} aria-label="Tabs">
        <Tab label="Vandaag" />
        <Tab label="Morgen" />
        <Tab label="Alles" />
        <Tab label="Zoek resultaten" />
      </Tabs>
    } else if (this.props.selected === undefined) {
    } else {
      return <Tabs value={this.state.selectedTab} onChange={this.handleChange} aria-label="Tabs">
        <Tab label="Vandaag" />
        <Tab label="Morgen" />
        <Tab label="Alles" />
      </Tabs>
    }
  }

  render() {
    const { classes } = this.props;
    return (
      <div className={classes.headerbar}>
        <AppBar position="static">
          <Toolbar>
            <Title />
            <div className={classes.grow} />
            {this.renderSearchBox()}
            <AppMenu />
            <HeaderMenu />
          </Toolbar>
          {this.renderTabs()}
        </AppBar>

      </div>
    );
  }
}

HeaderBar.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(HeaderBar);
