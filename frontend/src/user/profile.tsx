import {Button, createStyles, WithStyles, withStyles} from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import ArrowRightIcon from '@material-ui/icons/ArrowRight';
import SaveIcon from '@material-ui/icons/Save';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {default as React} from 'react';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import {Api} from "../Api";
import Header from "./header";
import {withAuthHandling, WithAuthHandling} from "../WithAuthHandling";

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
}

class Profile extends React.Component<ProfileProps, ProfileState> {

    apiFetch: Api

    constructor(props: ProfileProps) {
        super(props);
        this.state = {
            email_address: props.authHandling.user_information?.email_address || ''
        }
        this.apiFetch  = new Api(props)
    }

    notifyNoUpdate() {
        this.props.enqueueSnackbar('Profile was not updated. Continue to app...', {
            variant: 'warning',
            autoHideDuration: 3000,
        });
    }

    render() {
        const {classes} = this.props;

        return <div>
            <HeaderBar/>
            <Header title={"Manage profile"} />
            <div className={classes.signedInUI}>
                <Typography variant="h6" gutterBottom>
                    Welcome!
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
                </Grid>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(Profile))))
