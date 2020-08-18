import IconButton from '@material-ui/core/IconButton';
import InputBase from '@material-ui/core/InputBase';
import Paper from '@material-ui/core/Paper';
import { withStyles } from '@material-ui/core/styles';
import SearchIcon from '@material-ui/icons/Search';
import PropTypes from 'prop-types';
import React from 'react';

const styles = {
  root: {
    padding: '2px 4px',
    display: 'flex',
    alignItems: 'center',
    width: 400,
  },
  input: {
    marginLeft: 8,
    flex: 1,
  },
  iconButton: {
    padding: 10,
  },
};

class SearchBox extends React.Component {

  constructor(props) {
    super(props);
    this.state = { value: '' };

    this.handleChange = this.handleChange.bind(this);
    this.handleEnter = this.handleEnter.bind(this);
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleEnter(event) {
    if (event.key === 'Enter') {
      this.props.searchEvents(this.state.value)
    }
  }

  render() {
    const { classes } = this.props;

    return (
      <Paper className={classes.root} elevation={1}>
        <InputBase className={classes.input}
          placeholder="Zoek"
          value={this.state.value}
          onChange={this.handleChange}
          onKeyPress={this.handleEnter}
        />
        <IconButton className={classes.iconButton}
          aria-label="Search"
          onClick={() => this.props.searchEvents(this.state.value)}>
          <SearchIcon />
        </IconButton>
      </Paper>
    );
  }
}

SearchBox.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(SearchBox);

