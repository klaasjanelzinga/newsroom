import * as React from 'react';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import UserProfile from './UserProfile';
import {GoogleLogout} from "react-google-login";
import {createStyles, Typography, WithStyles} from "@material-ui/core";
import withStyles from "@material-ui/core/styles/withStyles";

const styles = createStyles({
    googleButton: {
        margin: '10px',
    },
    signoutForm: {
        margin: '5px',
    }
})

interface SignoutProps extends RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles> {
}

class SignOut extends React.Component<SignoutProps> {

    logout = () => {
        UserProfile.delete();

        this.props.enqueueSnackbar('You were signed out.', {
            variant: 'info',
        });
        this.props.history.push('/');
    }

    render() {
        const {classes} = this.props
        return <div>
            <HeaderBar/>
            <div className={classes.signoutForm}>
                <Typography component="h5" variant="h5">
                    Logout with google for the newsroom site.
                </Typography>
                <Typography variant="subtitle1" color="textSecondary">
                    <GoogleLogout
                        clientId="662875567592-9do93u1nppl2ks4geufjtm7n5hfo23m3.apps.googleusercontent.com"
                        buttonText="Logout"
                        className={classes.googleButton}
                        onLogoutSuccess={this.logout}
                    />
                    Click here to logout.
                </Typography>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(SignOut)));
  
  