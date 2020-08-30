import * as React from 'react';
import {Card, CardContent, createStyles, Typography, WithStyles, withStyles} from '@material-ui/core';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import GoogleLogin, {GoogleLoginResponse, GoogleLoginResponseOffline} from 'react-google-login';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import UserProfile from './UserProfile';


const styles = createStyles({
    card: {
        display: 'flex',
        margin: '10px',
    },
    details: {
        display: 'flex',
        flexDirection: 'column',
    },
    content: {
        flex: '2 0 auto',
    },
    disclosure: {
        padding: '10px',
    },
    googleButton: {
        backgroundColor: 'lightgrey',
        padding: '2px',
    }
});

interface GoogleCardProps extends RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles>{
    validateSignInWithServer: (userProfile: UserProfile) => void
}

class GoogleCard extends React.Component<GoogleCardProps> {

    constructor(props: GoogleCardProps) {
        super(props);

        this.responseGoogle = this.responseGoogle.bind(this);
        this.handleFailure = this.handleFailure.bind(this);
    }

    responseGoogle = (response: GoogleLoginResponse | GoogleLoginResponseOffline): void => {
        const loginResponse = response as GoogleLoginResponse
        if (loginResponse.profileObj) {
            const userProfile = new UserProfile(
                loginResponse.profileObj.givenName,
                loginResponse.profileObj.familyName,
                loginResponse.profileObj.email,
                loginResponse.profileObj.imageUrl,
                loginResponse.accessToken,
                loginResponse.tokenId,
            );
            this.props.validateSignInWithServer(userProfile);
        } else {
            this.props.enqueueSnackbar("Cannot login, we appear to be offline!", {
                variant: 'error',
                autoHideDuration: 6000,
            })
        }
    }

    handleFailure = (response: any):void => {
        this.props.enqueueSnackbar(`An error occured while signing in`, {
            variant: 'error',
            autoHideDuration: 6000,
        });
    }

    render() {
        const { classes } = this.props;
        return <Card className={classes.card}>
            <div className={classes.details}>
                <CardContent className={classes.content}>
                    <Typography component="h5" variant="h5">
                        Login using google  - You can sign in to the newsroom using your google account.
                    </Typography>
                    <Typography variant="subtitle1" color="textSecondary">
                        If your account has already been approved you will be taken to the newsroom site.
                    </Typography>
                    <Typography variant="subtitle1" color="textSecondary">
                        If you do not have an account with newsroom, your account will have to be approved by the
                        moderator. This will typically take a few days.
                    </Typography>
                </CardContent>
                <div className={classes.disclosure}>
                    <Typography variant="subtitle2" >
                        Newsroom will access the following data in your google profile:
                                <ul>
                            <li>Your email address.</li>
                            <li>Your given name as registered with Google.</li>
                            <li>Your family name as registered with Google.</li>
                        </ul>

                        The data is only used on this site and will not be shared. By clicking on the login
                        button you acknowledge this.
                    </Typography>

                </div>
                <div className={classes.googleButton}>
                    <GoogleLogin
                        clientId="662875567592-9do93u1nppl2ks4geufjtm7n5hfo23m3.apps.googleusercontent.com"
                        buttonText="Login"
                        onSuccess={this.responseGoogle}
                        onFailure={this.handleFailure}
                        className={classes.googleButton}
                        cookiePolicy={'single_host_origin'}
                    />
                </div>
            </div>
        </Card>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(GoogleCard)));

