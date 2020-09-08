import {Button, createStyles, Theme, WithStyles, withStyles} from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import ArrowRightIcon from '@material-ui/icons/ArrowRight';
import SaveIcon from '@material-ui/icons/Save';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {default as React} from 'react';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import UserProfile from './UserProfile';
import {Api} from "../Api";
import Header from "./header";
import {UserProfileResponse} from "./model";

const styles = (theme: Theme) => createStyles({
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
    }
});

interface ProfileProps extends WithSnackbarProps, WithStyles<typeof styles>, RouteComponentProps {
}

interface ProfileState {
    givenName: string;
    familyName: string;
}

class Profile extends React.Component<ProfileProps, ProfileState> {

    userProfile: UserProfile
    apiFetch: Api

    constructor(props: ProfileProps) {
        super(props);

        this.state = {
            givenName: '',
            familyName: '',
        }
        this.userProfile = UserProfile.get()
        this.apiFetch  = new Api(props)
    }

    componentDidMount() {
        if (this.userProfile == null) {
            this.props.history.push('/user/signin');
            return;
        }
        this.setState({
            givenName: this.userProfile.givenName,
            familyName: this.userProfile.familyName,
        });
    }

    notifyNoUpdate() {
        this.props.enqueueSnackbar('Profile was not updated. Continue to app...', {
            variant: 'warning',
            autoHideDuration: 3000,
        });
    }

    updateProfile = (): void => {
        this.apiFetch.post<UserProfileResponse>('/user/profile', JSON.stringify({
            given_name: this.state.givenName,
            family_name: this.state.familyName}))
            .then(response => {
                this.props.enqueueSnackbar('Profile was succesfully updated.', {
                    variant: 'info',
                });
                const user_response = response[1]
                user_response.id_token = this.userProfile.id_token
                this.userProfile = UserProfile.save(user_response)
                this.props.history.push('/')
            })
            .catch(error => console.error(error))
    }

    onChange = (e: React.FormEvent<HTMLInputElement>): void => {
        this.setState({ givenName: e.currentTarget.value });
    };

    render() {
        const {classes} = this.props;

        return <div>
            <HeaderBar/>
            <Header title={"Manage profile"} />
            <div className={classes.signedInUI}>
                <Typography variant="h6" gutterBottom>
                    Welcome {this.userProfile.givenName} {this.userProfile.familyName}!
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    Please update or acknowledge your profile.
                </Typography>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
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
                    <Grid item xs={12}>
                        <TextField
                            required
                            id="givenName"
                            name="givenName"
                            label="Name"
                            defaultValue={this.userProfile.givenName}
                            onChange={(e) => this.setState({givenName: e.currentTarget.value})}
                            fullWidth
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <TextField
                            required
                            id="familyName"
                            name="familyName"
                            label="Last name"
                            defaultValue={this.userProfile.familyName}
                            onChange={(e) => this.setState({familyName: e.currentTarget.value})}
                            fullWidth
                        />
                    </Grid>
                </Grid>
                <div className={classes.buttonBar}>
                    <Button variant="contained" size="small" className={classes.saveButton}
                            onClick={this.updateProfile}>
                        <SaveIcon className={classes.saveButton}/>
                        Save
                    </Button>
                    <Button variant="contained" size="small" className={classes.continueButton}
                            onClick={ () => {
                                console.log(this.state)
                                this.props.enqueueSnackbar('Profile is acknowledged.', {
                                    variant: 'info',
                                });
                                this.props.history.push('/');
                            }
                            }>
                        <ArrowRightIcon className={classes.saveButton}/>
                        Acknowledge
                    </Button>

                </div>
            </div>
        </div>
    }
}

//
export default withStyles(styles)(withRouter(withSnackbar(Profile)));
