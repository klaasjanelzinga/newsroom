import * as React from 'react'
import {createStyles, Typography, WithStyles} from '@material-ui/core';
import {withStyles} from '@material-ui/core/styles';
import {RouteComponentProps, withRouter} from 'react-router-dom';

const styles = createStyles({
    title: {
        cursor: 'pointer',
    },
});

export interface TitleProps extends RouteComponentProps, WithStyles<typeof styles> {
    title: string
}


const Title: React.FunctionComponent<TitleProps> = (props) => {
    const {classes} = props
    return <Typography onClick={() => props.history.push('/')}
                       className={classes.title}
                       variant="h6" color="inherit" noWrap>
        {props.title}
    </Typography>
}

export default withStyles(styles)(withRouter(Title));
