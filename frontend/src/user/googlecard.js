import { Card, CardContent, Typography, withStyles } from '@material-ui/core';
import { withSnackbar } from 'notistack';
import PropTypes from 'prop-types';
import React from 'react';
import GoogleLogin from 'react-google-login';
import { withRouter } from 'react-router-dom';
import UserProfile from './UserProfile';


const styles = {
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
};

class GoogleCard extends React.Component {

    constructor(props) {
        super(props);

        this.responseGoogle = this.responseGoogle.bind(this);
        this.handleFailure = this.handleFailure.bind(this);
    }

    responseGoogle(response) {
        let userProfile = new UserProfile(
            response.profileObj.givenName,
            response.profileObj.familyName,
            response.profileObj.email,
            response.profileObj.imageUrl,

            response.accessToken,
            response.tokenId,
        );
        this.props.validateSignInWithServer(userProfile);        
    }

    handleFailure(response) {
        this.props.notifyError(`Failed fetching data. ${response}`);
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

GoogleCard.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(withSnackbar(GoogleCard)));

