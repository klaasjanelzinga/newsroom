import React from 'react';
import {createStyles, Typography, WithStyles} from '@material-ui/core';
import {withStyles} from '@material-ui/core/styles';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from "../headerbar/HeaderBar";


const styles = createStyles({
    content: {
        margin: '10px',
    },
})

interface NeedsApprovalProps extends RouteComponentProps, WithStyles<typeof styles> {
}

const NeedsApproval: React.FunctionComponent<NeedsApprovalProps> = (props) => {
    const { classes } = props;
    return <div>
        <HeaderBar />
        <div className={classes.content}>
            <Typography component="h4" variant="h4">
                Hooray! You are signed in!
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
                But, your account has to be approved before you can actually use this site. Don&amp;apos;t worry, the webmaster
                promised to do this quickly. You receive an email when your account is approved and ready to go!.
            </Typography>
        </div>
    </div>
}

export default withStyles(styles)(withRouter(NeedsApproval));
