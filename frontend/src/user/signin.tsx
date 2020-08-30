import * as React from 'react';
import {createStyles, WithStyles, withStyles} from '@material-ui/core';
import {withSnackbar, WithSnackbarProps} from 'notistack';
import {RouteComponentProps, withRouter} from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import GoogleCard from './googlecard';
import UserProfile from './UserProfile';
import {ApiFetch} from "../ApiFetch";


const styles = createStyles({
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
});

interface SigninProps extends WithStyles<typeof styles>, RouteComponentProps, WithSnackbarProps {

}

class SignIn extends React.Component<SigninProps> {

    apiFetch: ApiFetch

    constructor(props: SigninProps) {
        super(props);
        this.apiFetch = new ApiFetch(props)
    }

    validateSignInWithServer= (userProfile: UserProfile):void => {
        this.apiFetch.post<UserProfile>('/user/signup', null, userProfile)
            .then((response) => {
                this.props.enqueueSnackbar('Succesfully signed in', {
                    variant: 'info',
                });
                UserProfile.save(userProfile)
                console.log(response)
                if (response[0] === 200) {
                    this.props.history.push('/')
                } else {
                    this.props.history.push('/user/needs-approval')
                }
            })
            .catch((reason) => console.error("IN ERROR validate signin", reason))
    }

    render() {
        const { classes } = this.props;
        return <div>
            <HeaderBar />

            <div className={classes.cards}>
                <GoogleCard 
                    validateSignInWithServer={this.validateSignInWithServer}
                    >
                </GoogleCard>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(SignIn)));

