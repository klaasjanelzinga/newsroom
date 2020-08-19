import { withStyles } from '@material-ui/core';
import { withSnackbar } from 'notistack';
import PropTypes from 'prop-types';
import React from 'react';
import { withRouter } from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import GoogleCard from './googlecard';
import UserProfile from './UserProfile';
import config from '../Config'


const styles = {
    card: {
        display: 'flex',
        width: '600px',
        margin: '10px',
    },
    details: {
        display: 'flex',
        flexDirection: 'column',
    },
    content: {
        flex: '2 0 auto',
    },
    cards: {
        padding: '10px',
        width: '100%',
        display: 'flex',
    },
    disclosure: {
        padding: '10px',
    },
    googleButton: {
        backgroundColor: 'lightgrey',
        padding: '2px',
    }
};

class SignIn extends React.Component {

    constructor(props) {
        super(props);

        this.handleFailure = this.handleFailure.bind(this);
        this.saveAndRedirect = this.saveAndRedirect.bind(this);
    }

    notifySuccesfulLogin() {
        this.props.enqueueSnackbar('Succesfully signed in', {
            variant: 'info',
        });
    }

    notifyError(message) {
        this.props.enqueueSnackbar(`An error occured ${message}`, {
            variant: 'error',
            autoHideDuration: 6000,
        });
    }

    validateSignInWithServer(userProfile) {

        console.log("Getting userprofile", userProfile)

        this.userProfile = UserProfile.save(userProfile);

        const request = new Request(`${config.apihost}/user/signup`, {
            method: 'POST',
            headers: {
                'Authorization': userProfile.bearerToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userProfile)
        });
        fetch(request)
            .then(response => {
                if (response.status === 200) {
                    response.json().then(json => {
                        this.saveAndRedirect(json, '/');
                    })
                } else if (response.status === 201) {
                    response.json().then(json => {
                        this.saveAndRedirect(json, '/user/profile');
                    })
                } else {
                    this.notifyError(`Cannot register user at server: ${response.statusText}`);
                    UserProfile.delete();
                }
            });
    }

    saveAndRedirect(json, redirectUrl) {
        this.props.history.push(redirectUrl);
        this.userProfile.merge(json);
        this.notifySuccesfulLogin();
    }

    handleFailure(response) {
        this.notifyError(`Failed fetching data. ${response}`);
    }

    render() {
        const { classes } = this.props;
        return <div>
            <HeaderBar />

            <div className={classes.cards}>
                <GoogleCard 
                    validateSignInWithServer={(userProfile) => this.validateSignInWithServer(userProfile)} 
                    notifyError={(message) => this.notifyError(message)}
                    >
                </GoogleCard>
            </div>
        </div>
    }
}

SignIn.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(withSnackbar(SignIn)));

