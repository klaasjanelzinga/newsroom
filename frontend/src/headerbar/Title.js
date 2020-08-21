import React from 'react';
import {Typography} from '@material-ui/core';
import {withStyles} from '@material-ui/core/styles';
import {withRouter} from 'react-router-dom';

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

function Title(props) {
        const { classes } = props;

        return <Typography onClick={() => props.history.push('/')}
                           className={classes.title}
                           variant="h6" color="inherit" noWrap>
            Newsroom
        </Typography>
}

export default withStyles(styles)(withRouter(Title));
