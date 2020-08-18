import { Button, withStyles } from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import ArrowRightIcon from '@material-ui/icons/ArrowRight';
import SaveIcon from '@material-ui/icons/Save';
import { withSnackbar } from 'notistack';
import PropTypes from 'prop-types';
import { default as React } from 'react';
import { withRouter } from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar.js';
import UserProfile from './UserProfile.js';
import config from '../Config'

const styles = theme => ( {
    saveButton: {
        marginRight: '10px',
        marginLeft: '8px',
        fontSize: 13,
    },
    continueButton: {
        marginRight: '10px',
        fontSize: 13,
    },
    buttonBar: {
        backgroundColor: 'lightgrey',
        padding: '3px',
        marginTop: '20px',
    },
    signedInUI: {
        padding: '10px',
        marginLeft: '2px',
        [theme.breakpoints.down('sm')]: {
            width: '100%',
        },
        [theme.breakpoints.up('md')]: {
            width: '40%',
        },
        border: 'lightgrey',
        borderStyle: 'solid',
        borderWidth: '1px',
    }
});

class Profile extends React.Component {


    constructor(props) {
        super(props);

        this.updateProfile = this.updateProfile.bind(this);
        this.continueProfile = this.continueProfile.bind(this);

        this.state = {
            givenName: '',
            familyName: '',
        }
    }

    componentWillMount() {
        this.userProfile = UserProfile.load();
        if (this.userProfile === null) {
            this.props.history.push('/user/signin');
            return;
        }
        this.setState({
            givenName: this.userProfile.givenName,
            familyName: this.userProfile.familyName,
        });
    }

    notifySuccesfulUpdate() {
        this.props.enqueueSnackbar('Profile was succesfully updated.', {
            variant: 'info',
        });
    }

    notifyNoUpdate() {
        this.props.enqueueSnackbar('Profile was not updated. Continue to app...', {
            variant: 'warning',
            autoHideDuration: 3000,
        });
    }

    notifyError(message) {
        this.props.enqueueSnackbar(`An error occured ${message}`, {
            variant: 'error',
            autoHideDuration: 6000,
        });
    }


    updateProfile() {
        this.userProfile.givenName = this.state.givenName;
        this.userProfile.familyName = this.state.familyName;
        this.userProfile.merge(this.userProfile);

        const request = new Request(`${config.apihost}/api/user/profile`, {
            method: 'POST',
            headers: {
                'Authorization': this.userProfile.bearerToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.userProfile)
        });
        fetch(request)
            .then(response => {
                if (response.status === 200) {
                    response.json().then(json => {
                        this.notifySuccesfulUpdate();
                        this.props.history.push('/');
                    })
                } else {
                    this.notifyError(response.statusText)
                }
            })
    }


    continueProfile() {
        this.notifyNoUpdate();
        this.props.history.push('/');
    }

    signedInUI() {
        const { classes } = this.props;
        const handleChange = name => event => {
            this.setState({ [name]: event.target.value })
        };
        return <div className={classes.signedInUI}>
            <Typography variant="h6" gutterBottom>
                Welcome {this.userProfile.givenName} {this.userProfile.familyName}!
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
                Please update or acknowledge your profile.
            </Typography>
            <Grid container spacing={3}>
                <Grid item xs={12} >
                    <TextField
                        required
                        id="email"
                        name="email"
                        label="Email address"
                        disabled={true}
                        fullWidth
                        defaultValue={this.userProfile.email}
                        autoComplete="fname"
                    />
                </Grid>
                <Grid item xs={12} >
                    <TextField
                        required
                        id="givenName"
                        name="givenName"
                        label="Name"
                        defaultValue={this.userProfile.givenName}
                        onChange={handleChange('givenName')}
                        fullWidth
                    />
                </Grid>
                <Grid item xs={12} >
                    <TextField
                        required
                        id="familyName"
                        name="familyName"
                        label="Last name"
                        defaultValue={this.userProfile.familyName}
                        onChange={handleChange('familyName')}
                        fullWidth
                    />
                </Grid>
            </Grid>
            <div className={classes.buttonBar}>
                <Button variant="contained" size="small" className={classes.saveButton} onClick={this.updateProfile}>
                    <SaveIcon className={classes.saveButton} />
                    Save
            </Button>
                <Button variant="contained" size="small" className={classes.continueButton} onClick={this.continueProfile}>
                    <ArrowRightIcon className={classes.saveButton} />
                    Continue
            </Button>

            </div>
        </div>
    }

    render() {

        if (this.userProfile === null) {
            return <div>Not signed in. Redirecting to login page...</div>
        } else {
            return <div>
                <HeaderBar />
                {this.signedInUI()}
            </div>
        }
    }
}

Profile.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(withSnackbar(Profile)));
