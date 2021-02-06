import {Button, createStyles, Icon, WithStyles, withStyles} from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {default as React} from 'react';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import {Api} from "../Api";
import Header from "./header";
import {TokenBasedAuthenticator, withAuthHandling, WithAuthHandling} from "../WithAuthHandling";
import {UserProfileRequest, UserResponse} from "./model";

const styles = createStyles({
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

interface ProfileProps extends WithAuthHandling, WithSnackbarProps, WithStyles<typeof styles>, RouteComponentProps {
}

interface ProfileState {
    email_address: string
    display_name: string
}

class Profile extends React.Component<ProfileProps, ProfileState> {

    api: Api
    authHandler: TokenBasedAuthenticator

    constructor(props: ProfileProps) {
        super(props);
        this.state = {
            email_address: props.authHandling.user_information?.email_address || '',
            display_name: props.authHandling.user_information?.display_name || '',
        }
        this.api = new Api(props)
        this.authHandler = this.props.authHandling
    }

    async update_profile(): Promise<void> {
        this.api.post<UserResponse>("/user/update-profile", JSON.stringify({
            display_name: this.state.display_name,
        }))
            .then(userResponse => {
                if (userResponse[0] == 200) {
                    this.authHandler.update_user_information(userResponse[1])
                    this.props.enqueueSnackbar(`Profile updated`, {
                        variant: 'info',
                        autoHideDuration: 1500,
                    });
                    this.props.history.push('/')
                }
                else {
                    this.props.enqueueSnackbar(`Profile not updated`, {
                        variant: 'warning',
                        autoHideDuration: 3000,
                    });
                }
            })
            .catch(reason => console.log(reason))
        return Promise.resolve()
    }

    render() {
        const {classes} = this.props;

        return <div>
            <HeaderBar/>
            <Header title={"Manage profile"}/>
            <div className={classes.signedInUI}>
                <Typography variant="h6" gutterBottom>
                    Welcome {this.authHandler.user_information?.display_name || ''}!
                </Typography>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <TextField
                            required
                            id="email"
                            name="email"
                            label="Email address"
                            value={this.state.email_address}
                            disabled={true}
                            fullWidth
                            autoComplete="username"
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <TextField
                            required
                            id="display_name"
                            name="display_name"
                            label="Display name"
                            value={this.state.display_name}
                            onChange={(e) => this.setState({display_name: e.currentTarget.value})}
                            fullWidth
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <div className={classes.buttonBar}>
                            <Button
                                variant="contained"
                                color="primary"
                                className={classes.saveButton}
                                onClick={async () => await this.update_profile()} >
                                Change profile
                            </Button>
                        </div>
                    </Grid>
                </Grid>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(Profile))))
