import { Typography } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import React from 'react';
import { withRouter } from 'react-router-dom';

const styles = theme => ({
    title: {
        display: 'none',
        cursor: 'pointer',
        [theme.breakpoints.up('sm')]: {
            display: 'block',
        },
    },
}
);


class Title extends React.Component {

    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        this.props.history.push('/');
    }

    render() {
        const { classes } = this.props;

        return <Typography onClick={this.handleClick} className={classes.title} variant="h6" color="inherit" noWrap>
            Newsroom
        </Typography>


    }
}

Title.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(Title));

